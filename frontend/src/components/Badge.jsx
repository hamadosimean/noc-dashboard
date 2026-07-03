import React from "react";
import { SEVERITY_COLOR, STATUS } from "../theme/colors";

const STATUS_COLOR = {
  open: STATUS.critical,
  acknowledged: STATUS.warning,
  resolved: STATUS.good,
  closed: "var(--color-text-muted)",
};

const withAlpha = (hex, alpha) => {
  if (!hex.startsWith("#")) return hex; // css var fallback, no alpha blend needed
  return `${hex}${Math.round(alpha * 255)
    .toString(16)
    .padStart(2, "0")}`;
};

export const SeverityBadge = ({ severity }) => {
  const color = SEVERITY_COLOR[severity] ?? STATUS.good;
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium capitalize"
      style={{ background: withAlpha(color, 0.15), color }}
    >
      <span
        className="h-1.5 w-1.5 rounded-full"
        style={{ background: color }}
      />
      {severity}
    </span>
  );
};

export const StatusBadge = ({ status }) => {
  const color = STATUS_COLOR[status] ?? "var(--color-text-muted)";
  return (
    <span
      className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize"
      style={{ background: withAlpha(color, 0.15), color }}
    >
      {status}
    </span>
  );
};
