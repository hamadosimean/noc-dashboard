import React from 'react';
import { Server, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

const NodeList = () => {
  const nodes = [
    { id: 'OUA-001', name: 'DREP Ouaga', status: 'ok' },
    { id: 'OUA-002', name: 'Gouvernorat Centre', status: 'warning' },
    { id: 'OUA-003', name: 'Trésor Public', status: 'critical' },
    { id: 'OUA-004', name: 'Hôpital Yalgado', status: 'ok' },
  ];

  const getStatusIcon = (status) => {
    switch(status) {
      case 'ok': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'critical': return <XCircle className="w-5 h-5 text-red-500" />;
      default: return <Server className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
        <h3 className="text-lg font-medium">Nœuds du réseau</h3>
      </div>
      <ul className="divide-y divide-gray-200">
        {nodes.map(node => (
          <li key={node.id} className="p-4 flex items-center justify-between hover:bg-gray-50 cursor-pointer">
            <div className="flex items-center space-x-3">
              <Server className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm font-medium text-gray-900">{node.name}</p>
                <p className="text-xs text-gray-500">{node.id}</p>
              </div>
            </div>
            <div>
              {getStatusIcon(node.status)}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default NodeList;
