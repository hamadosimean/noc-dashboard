import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const WeeklyBar = () => {
  const data = {
    labels: ['Semaine 1', 'Semaine 2', 'Semaine 3', 'Semaine 4'],
    datasets: [
      {
        label: 'Incidents résolus',
        data: [12, 19, 3, 5],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
      },
      {
        label: 'Incidents en cours',
        data: [2, 3, 1, 4],
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' },
    },
  };

  return <Bar data={data} options={options} />;
};

export default WeeklyBar;
