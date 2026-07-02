import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

const KPICard = ({ title, value, trend, trendType }) => {
  const isPositive = trendType === 'positive';
  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-100 flex flex-col">
      <h3 className="text-sm font-medium text-gray-500 mb-1">{title}</h3>
      <div className="text-3xl font-bold text-gray-900">{value}</div>
      <div className={`flex items-center mt-2 text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
        {isPositive ? <ArrowUpRight className="w-4 h-4 mr-1" /> : <ArrowDownRight className="w-4 h-4 mr-1" />}
        <span>{trend} depuis le mois dernier</span>
      </div>
    </div>
  );
};

export default KPICard;
