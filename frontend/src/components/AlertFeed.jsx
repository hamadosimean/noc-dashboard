import React from 'react';
import { Bell } from 'lucide-react';

const AlertFeed = () => {
  const alerts = [
    { id: 1, message: "Alerte Centreon: DED-001 Hors Ligne", time: "Maintenant", severity: "critical" },
    { id: 2, message: "Alerte Zabbix: Onduleur OUA-003 Faible Batterie", time: "il y a 5 min", severity: "high" },
    { id: 3, message: "Webhook iTop: Ticket TKT-2026-4821 créé", time: "il y a 10 min", severity: "info" },
  ];

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 h-full flex flex-col">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex items-center space-x-2">
        <Bell className="w-5 h-5 text-gray-500" />
        <h3 className="text-lg font-medium">Flux d'Alertes en Direct</h3>
      </div>
      <div className="p-4 flex-1 overflow-y-auto">
        <div className="space-y-4">
          {alerts.map(alert => (
            <div key={alert.id} className="flex border-l-4 border-red-500 pl-3 py-1">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                <p className="text-xs text-gray-500">{alert.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AlertFeed;
