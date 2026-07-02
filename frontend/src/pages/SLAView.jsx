import React from 'react';
import SLATracker from '../components/SLATracker';
import AlertFeed from '../components/AlertFeed';

const SLAView = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-800">SLA & Alertes Temps Réel</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <SLATracker metric="Disponibilité Cœur de Réseau" value={99.9} target={99.5} />
          <SLATracker metric="Disponibilité Nœuds d'Accès" value={93.8} target={95.0} />
          <SLATracker metric="Taux de Résolution < 4h" value={65.6} target={80.0} />
        </div>
        <div>
          <AlertFeed />
        </div>
      </div>
    </div>
  );
};

export default SLAView;
