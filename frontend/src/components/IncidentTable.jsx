import React from 'react';

const IncidentTable = ({ title = 'Liste des Incidents' }) => {
  const incidents = [
    { id: 4821, node: 'DED-001', severity: 'critical', status: 'open', desc: 'Perte de connectivité - onduleur', time: 'il y a 2h' },
    { id: 4820, node: 'OUA-003', severity: 'high', status: 'acknowledged', desc: 'Surcharge processeur', time: 'il y a 4h' },
    { id: 4819, node: 'BOB-012', severity: 'medium', status: 'resolved', desc: 'Latence réseau', time: 'il y a 1j' },
  ];

  const getSeverityBadge = (sev) => {
    const colors = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-blue-100 text-blue-800',
    };
    return <span className={`px-2 py-1 text-xs rounded-full font-medium ${colors[sev]}`}>{sev}</span>;
  };

  const getStatusBadge = (status) => {
    const colors = {
      open: 'bg-red-100 text-red-800',
      acknowledged: 'bg-blue-100 text-blue-800',
      resolved: 'bg-green-100 text-green-800',
    };
    return <span className={`px-2 py-1 text-xs rounded-full font-medium ${colors[status]}`}>{status}</span>;
  };

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <h3 className="text-lg font-medium">{title}</h3>
        <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">Voir tout</button>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nœud</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sévérité</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Détection</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {incidents.map((inc) => (
              <tr key={inc.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{inc.id}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{inc.node}</td>
                <td className="px-6 py-4 whitespace-nowrap">{getSeverityBadge(inc.severity)}</td>
                <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(inc.status)}</td>
                <td className="px-6 py-4 text-sm text-gray-500 truncate max-w-xs">{inc.desc}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{inc.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default IncidentTable;
