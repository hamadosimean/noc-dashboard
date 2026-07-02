import React from 'react';

const HourHeatmap = () => {
  // Simple representation instead of a complex chart
  return (
    <div className="flex flex-col items-center justify-center h-full text-gray-500">
      <div className="grid grid-cols-6 gap-1 w-full h-full p-2">
        {Array.from({ length: 24 }).map((_, i) => (
          <div key={i} className={`rounded ${i % 3 === 0 ? 'bg-red-200' : 'bg-green-100'} flex items-center justify-center text-xs`}>
            {i}h
          </div>
        ))}
      </div>
    </div>
  );
};

export default HourHeatmap;
