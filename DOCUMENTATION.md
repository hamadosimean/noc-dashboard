# NOC ANPTIC Dashboard

Ce document présente l'architecture et la structure du projet pour le tableau de bord du Centre des Opérations Réseau (NOC) de l'ANPTIC. Ce projet est conçu pour centraliser les KPI de disponibilité et d'incidents en temps réel en s'intégrant avec des outils de supervision tels que Zabbix, Nagios, NetXMS, Centreon et iTop.

## Architecture Générale

L'application repose sur une architecture 3-tiers conteneurisée à l'aide de Docker Compose :
- **Backend (FastAPI)** : Gère les API REST, la collecte d'événements (webhooks) et le calcul des KPI.
- **Frontend (React)** : Fournit le tableau de bord interactif pour visualiser les données en temps réel.
- **Base de données (PostgreSQL)** : Stocke les dimensions (régions, localités, nœuds) et la table de faits (incidents).
- **Cache (Redis)** : Optimise les performances et met en cache les appels API fréquents (ex. résumés KPI mensuels).
- **Reverse Proxy (NGINX)** : Route le trafic web, servant l'application React et redirigeant les requêtes API vers le backend.

---

## Structure du Projet

```text
noc/
├── docker-compose.yml       # Déclaration des services Docker (Backend, Frontend, NGINX, Redis, PostgreSQL)
├── database/
│   └── init.sql             # Script d'initialisation de la base de données (Schéma SQL complet)
├── nginx/
│   └── nginx.conf           # Configuration du Reverse Proxy NGINX
├── backend/                 # API FastAPI (Python 3.12)
│   ├── Dockerfile           # Fichier de construction Docker pour le backend
│   ├── requirements.txt     # Dépendances Python
│   └── app/
│       ├── main.py          # Point d'entrée de l'application FastAPI
│       ├── api/             # Définition des endpoints REST (/api/kpi, /api/alerts, etc.)
│       ├── core/            # Configuration centralisée et constantes métier (ex. constants.py)
│       ├── db/              # Gestion des connexions et sessions de la base de données
│       ├── models/          # Modèles SQLAlchemy (ORM)
│       ├── schemas/         # Modèles Pydantic pour validation des requêtes et réponses API
│       └── services/        # Logique métier (calculs KPI, intégrations iTop/Zabbix)
└── frontend/                # Application React (Vite)
    ├── Dockerfile           # Fichier de construction Docker pour le frontend
    ├── package.json         # Dépendances Node.js
    ├── vite.config.js       # Configuration Vite
    └── src/
        ├── api/             # Clients HTTP pour communiquer avec le Backend (via Axios)
        ├── components/      # Composants React réutilisables (Tableaux, Cartes)
        │   ├── charts/      # Composants graphiques basés sur Chart.js
        │   └── layout/      # Composants de mise en page (Navigation, En-têtes)
        ├── hooks/           # Hooks React personnalisés (ex. useKPI, useRealtime)
        ├── pages/           # Vues principales du tableau de bord (Vue globale, Localités, SLA)
        ├── store/           # Gestionnaire d'état global (Zustand)
        ├── App.jsx          # Composant racine de l'application React
        └── main.jsx         # Point d'entrée React
```

---

## Composants Principaux

### 1. Base de Données (PostgreSQL)
Le dossier `database/` contient `init.sql`. Lors du premier lancement de `docker-compose up`, ce script est automatiquement exécuté pour créer :
- Les tables de dimension (`dim_region`, `dim_locality`, `dim_node`, `dim_cause`).
- La table des faits principale (`fact_incident`).
- La vue matérialisée pour les KPI mensuels (`mv_kpi_node_monthly`).

### 2. Backend (FastAPI)
Le dossier `backend/app/` respecte une structure modulaire professionnelle. Les requêtes entrantes (ex. les webhooks provenant de Centreon) sont acheminées vers les routeurs définis dans `api/`. Les `services/` traitent les événements asynchrones, et interagissent avec la base via les `models/` et `db/`. Les variables d'environnement, la sécurité (JWT), et d'autres constantes (ex. URL iTop) se trouvent dans le module `core/`.

### 3. Frontend (React / Vite)
Le tableau de bord est organisé logiquement autour des fonctionnalités. Les requêtes asynchrones vers le backend sont traitées dans le dossier `api/`, mis en cache via des outils comme TanStack React Query (dans `hooks/`), et affichées via les `pages/` et `components/`. L'état de l'application (ex. les filtres de mois et d'année) est géré globalement par le `store/` via Zustand.

### 4. Reverse Proxy (NGINX)
NGINX agit comme la porte d'entrée du projet. Il gère le routage du trafic réseau:
- `/api/*` -> Route redirigée vers le conteneur du backend (Port 8000).
- `/` -> Route redirigée vers le conteneur du frontend (Port 80).

---

## Déploiement Local

Pour lancer l'ensemble des services en environnement local :

```bash
# Aller dans le répertoire du projet
cd noc

# Construire et lancer les conteneurs (en arrière-plan avec l'option -d)
docker-compose up --build -d
```

L'application sera accessible aux adresses suivantes :
- Frontend : `http://localhost:3000`
- Backend API Docs : `http://localhost:8000/docs`
