import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { useChartTheme } from '../../hooks/useChartTheme';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

// Monthly incidents trend (resolved vs. still open), fed by GET /api/kpi/trend
const WeeklyBar = ({ points = [] }) => {
  const { chrome, categorical } = useChartTheme();

  const data = {
    labels: points.map((p) => p.label),
    datasets: [
      {
        label: 'Incidents résolus',
        data: points.map((p) => p.resolved),
        backgroundColor: categorical[0],
        borderRadius: 4,
        maxBarThickness: 28,
      },
      {
        label: 'Incidents en cours',
        data: points.map((p) => p.total_incidents - p.resolved),
        backgroundColor: categorical[5],
        borderRadius: 4,
        maxBarThickness: 28,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { position: 'bottom', labels: { color: chrome.secondaryInk, usePointStyle: true, boxWidth: 8 } },
      tooltip: { backgroundColor: chrome.surface, titleColor: chrome.primaryInk, bodyColor: chrome.secondaryInk, borderColor: chrome.grid, borderWidth: 1 },
    },
    scales: {
      x: { stacked: false, grid: { display: false }, ticks: { color: chrome.mutedInk } },
      y: { beginAtZero: true, grid: { color: chrome.grid }, ticks: { color: chrome.mutedInk } },
    },
  };

  return <Bar data={data} options={options} />;
};

export default WeeklyBar;
