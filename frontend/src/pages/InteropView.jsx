import React from 'react';
import TrendLine from '../components/charts/TrendLine';

const InteropView = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-800">Interopérabilité</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h3 className="font-medium text-lg mb-2">Zabbix</h3>
          <p className="text-gray-600 text-sm mb-4">Surveillance énergie et onduleurs. Agent actif.</p>
          <div className="text-sm font-semibold text-green-600">Statut: Connecté</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h3 className="font-medium text-lg mb-2">Nagios</h3>
          <p className="text-gray-600 text-sm mb-4">Disponibilité hôtes et services via NDO2DB.</p>
          <div className="text-sm font-semibold text-green-600">Statut: Connecté</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h3 className="font-medium text-lg mb-2">Centreon / iTop</h3>
          <p className="text-gray-600 text-sm mb-4">Agrégation des alertes et création de tickets automatique.</p>
          <div className="text-sm font-semibold text-green-600">Statut: Webhooks Actifs</div>
        </div>
      </div>
      
      <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
        <h3 className="text-lg font-medium mb-4">Disponibilité globale agrégée</h3>
        <div className="h-64">
          <TrendLine />
        </div>
      </div>
    </div>
  );
};

export default InteropView;
