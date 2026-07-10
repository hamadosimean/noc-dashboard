import React from "react";
import { useChartTheme } from "../../hooks/useChartTheme";

// Incident count per hour of day (H24), fed by GET /api/kpi/hour-distribution.
// Sequential single-hue encoding: opacity of the accent color scales with
// magnitude (near-zero fades toward the surface, peak hours saturate fully).
const HourHeatmap = ({ hours = [] }) => {
  const { categorical } = useChartTheme();
  const accent = categorical[0];
  const max = Math.max(1, ...hours.map((h) => h.total_incidents));

  return (
    <div className="grid grid-cols-6 gap-1.5 sm:grid-cols-8 xl:grid-cols-12">
      {hours.map((h) => {
        const ratio = h.total_incidents / max;
        const alpha = h.total_incidents === 0 ? 0.06 : 0.22 + ratio * 0.78;
        return (
          <div
            key={h.hour}
            title={`${h.total_incidents} incident(s) à ${h.hour}h`}
            className="flex aspect-square items-center justify-center rounded-md text-[11px] font-semibold"
            style={{
              backgroundColor: `${accent}${Math.round(alpha * 255)
                .toString(16)
                .padStart(2, "0")}`,
              color: ratio > 0.45 ? "#ffffff" : "var(--color-text-secondary)",
            }}
          >
            {h.hour}h
          </div>
        );
      })}
    </div>
  );
};

export default HourHeatmap;
