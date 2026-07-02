import React from 'react';

const SLATracker = ({ metric, value, target }) => {
  const isMet = value >= target;
  
  return (
    <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
      <div className="flex justify-between items-center mb-2">
        <h4 className="font-medium text-gray-700">{metric}</h4>
        <span className={`px-2 py-1 text-xs font-bold rounded ${isMet ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {isMet ? 'Atteint' : 'Non Atteint'}
        </span>
      </div>
      <div className="flex justify-between items-baseline mb-2">
        <span className="text-2xl font-bold">{value}%</span>
        <span className="text-sm text-gray-500">Cible: {target}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div className={`h-2.5 rounded-full ${isMet ? 'bg-green-500' : 'bg-red-500'}`} style={{ width: `${value}%` }}></div>
      </div>
    </div>
  );
};

export default SLATracker;
