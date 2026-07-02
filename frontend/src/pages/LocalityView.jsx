import React from 'react';
import NodeList from '../components/NodeList';
import IncidentTable from '../components/IncidentTable';

const LocalityView = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-800">Vue par Localité</h2>
        <select className="border border-gray-300 rounded px-4 py-2 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option>Ouagadougou</option>
          <option>Bobo-Dioulasso</option>
          <option>Dédougou</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <NodeList />
        </div>
        <div className="lg:col-span-2">
          <IncidentTable title="Incidents Récents (Localité)" />
        </div>
      </div>
    </div>
  );
};

export default LocalityView;
