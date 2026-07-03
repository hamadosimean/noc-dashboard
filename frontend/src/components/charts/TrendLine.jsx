import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import { useChartTheme } from '../../hooks/useChartTheme';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

// Network availability trend, fed by GET /api/kpi/trend
const TrendLine = ({ points = [] }) => {
  const { chrome, categorical } = useChartTheme();
  const accent = categorical[0];

  const data = {
    labels: points.map((p) => p.label),
    datasets: [
      {
        label: 'Disponibilité Moyenne (%)',
        data: points.map((p) => p.availability_pct),
        borderColor: accent,
        backgroundColor: `${accent}26`,
        pointBackgroundColor: accent,
        pointBorderColor: chrome.surface,
        pointBorderWidth: 2,
        pointRadius: 4,
        borderWidth: 2,
        tension: 0.35,
        fill: true,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: { backgroundColor: chrome.surface, titleColor: chrome.primaryInk, bodyColor: chrome.secondaryInk, borderColor: chrome.grid, borderWidth: 1 },
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: chrome.mutedInk } },
      y: { grid: { color: chrome.grid }, ticks: { color: chrome.mutedInk } },
    },
  };

  return <Line data={data} options={options} />;
};

export default TrendLine;
