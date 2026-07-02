import React from 'react';
import KPICard from '../components/KPICard';
import WeeklyBar from '../components/charts/WeeklyBar';
import MTTRDonut from '../components/charts/MTTRDonut';

const GlobalView = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-800">Vue Globale</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard title="Total Incidents" value="32" trend="+4" trendType="negative" />
        <KPICard title="Disponibilité Réseau" value="93.8%" trend="-1.2%" trendType="negative" />
        <KPICard title="Taux de Résolution" value="65.6%" trend="+5%" trendType="positive" />
        <KPICard title="MTTR Moyen" value="138 min" trend="-10 min" trendType="positive" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
          <h3 className="text-lg font-medium mb-4">Évolution Hebdomadaire</h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 border border-dashed border-gray-300 rounded">
            <WeeklyBar />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
          <h3 className="text-lg font-medium mb-4">Répartition MTTR par cause</h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 border border-dashed border-gray-300 rounded">
            <MTTRDonut />
          </div>
        </div>
      </div>
    </div>
  );
};

export default GlobalView;
