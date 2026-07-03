import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { useChartTheme } from '../../hooks/useChartTheme';

ChartJS.register(ArcElement, Tooltip, Legend);

// Incident count by cause category, fed by GET /api/kpi/causes
const MTTRDonut = ({ causes = [] }) => {
  const { chrome, categorical } = useChartTheme();

  const data = {
    labels: causes.map((c) => c.category),
    datasets: [
      {
        data: causes.map((c) => c.total_incidents),
        backgroundColor: causes.map((_, i) => categorical[i % categorical.length]),
        borderColor: chrome.surface,
        borderWidth: 2,
        hoverOffset: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '68%',
    plugins: {
      legend: { position: 'bottom', labels: { color: chrome.secondaryInk, usePointStyle: true, boxWidth: 8 } },
      tooltip: { backgroundColor: chrome.surface, titleColor: chrome.primaryInk, bodyColor: chrome.secondaryInk, borderColor: chrome.grid, borderWidth: 1 },
    },
  };

  return <Doughnut data={data} options={options} />;
};

export default MTTRDonut;
