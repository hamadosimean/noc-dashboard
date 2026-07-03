import React from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { STATUS } from "../theme/colors";

const SLATracker = ({ metric, value, target }) => {
  const isMet = value >= target;
  const color = isMet ? STATUS.good : STATUS.critical;

  return (
    <div
      className="rounded-xl border p-5"
      style={{
        background: "var(--color-surface)",
        borderColor: "var(--color-border)",
        boxShadow: "var(--shadow-elevate)",
      }}
    >
      <div className="mb-3 flex items-center justify-between">
        <h4
          className="text-sm font-semibold"
          style={{ color: "var(--color-text-primary)" }}
        >
          {metric}
        </h4>
        <span
          className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-bold"
          style={{ background: `${color}26`, color }}
        >
          {isMet ? (
            <CheckCircle2 className="h-3.5 w-3.5" />
          ) : (
            <XCircle className="h-3.5 w-3.5" />
          )}
          {isMet ? "Atteint" : "Non Atteint"}
        </span>
      </div>
      <div className="mb-2 flex items-baseline justify-between">
        <span
          className="text-2xl font-bold tabular-nums"
          style={{ color: "var(--color-text-primary)" }}
        >
          {value}%
        </span>
        <span
          className="text-sm"
          style={{ color: "var(--color-text-secondary)" }}
        >
          Cible: {target}%
        </span>
      </div>
      <div
        className="h-2 w-full rounded-full"
        style={{ background: "var(--color-surface-3)" }}
      >
        <div
          className="h-2 rounded-full transition-all"
          style={{ width: `${Math.min(value, 100)}%`, background: color }}
        />
      </div>
    </div>
  );
};

export default SLATracker;
