import React from 'react';
import { NavLink } from 'react-router-dom';
import { Globe, MapPin, ShieldAlert, Zap, Database } from 'lucide-react';

const TabNav = () => {
  const tabs = [
    { name: 'Vue Globale', path: '/global', icon: Globe },
    { name: 'Vue par Localité', path: '/locality', icon: MapPin },
    { name: 'SLA & Alertes', path: '/sla', icon: ShieldAlert },
    { name: 'Interopérabilité', path: '/interop', icon: Zap },
    { name: 'Modèle de Données', path: '/datamodel', icon: Database },
  ];

  return (
    <nav className="bg-white border-b border-gray-200 px-6 flex space-x-8">
      {tabs.map((tab) => (
        <NavLink
          key={tab.path}
          to={tab.path}
          className={({ isActive }) =>
            `flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              isActive
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`
          }
        >
          <tab.icon className="w-4 h-4 mr-2" />
          {tab.name}
        </NavLink>
      ))}
    </nav>
  );
};

export default TabNav;
