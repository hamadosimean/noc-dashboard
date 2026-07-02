import React from 'react';
import { Activity } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-blue-900 text-white p-4 shadow-md flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <Activity className="h-6 w-6 text-blue-400" />
        <h1 className="text-xl font-bold tracking-wide">NOC ANPTIC Dashboard</h1>
      </div>
      <div className="text-sm text-blue-200">
        <span>Connecté: Admin NOC</span>
      </div>
    </header>
  );
};

export default Header;
