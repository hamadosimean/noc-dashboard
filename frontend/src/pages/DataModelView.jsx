import React from 'react';
import HourHeatmap from '../components/charts/HourHeatmap';

const DataModelView = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-800">Modèle de Données & Analytics</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h3 className="font-medium text-lg mb-4">Architecture de la Base de Données</h3>
          <ul className="list-disc pl-5 space-y-2 text-gray-700">
            <li><strong>dim_region</strong> : Régions administratives (13)</li>
            <li><strong>dim_locality</strong> : Localités, villes, et communes</li>
            <li><strong>dim_node</strong> : Granularité fine, routeurs, onduleurs, etc.</li>
            <li><strong>fact_incident</strong> : Table centrale de faits (Tickets, alertes)</li>
            <li><strong>mv_kpi_node_monthly</strong> : Vue matérialisée pour KPI rapides</li>
          </ul>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h3 className="font-medium text-lg mb-4">Distribution H24 (Heatmap)</h3>
          <div className="h-48 border border-dashed border-gray-300 rounded bg-gray-50">
            <HourHeatmap />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataModelView;
