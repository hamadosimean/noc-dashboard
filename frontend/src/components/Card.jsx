import React from "react";

const Card = ({
  title,
  subtitle,
  action,
  icon: Icon,
  children,
  className = "",
  bodyClassName = "",
  bodyStyle = {},
}) => (
  <div
    className={`rounded-xl border ${className}`}
    style={{
      background: "var(--color-surface)",
      borderColor: "var(--color-border)",
      boxShadow: "var(--shadow-elevate)",
    }}
  >
    {(title || action) && (
      <div
        className="flex items-center justify-between gap-3 border-b px-5 py-3.5"
        style={{ borderColor: "var(--color-border)" }}
      >
        <div className="flex items-center gap-2 min-w-0">
          {Icon && (
            <Icon
              className="h-4 w-4 shrink-0"
              style={{ color: "var(--color-accent)" }}
            />
          )}
          <div className="min-w-0">
            <h3
              className="truncate text-sm font-semibold"
              style={{ color: "var(--color-text-primary)" }}
            >
              {title}
            </h3>
            {subtitle && (
              <p
                className="truncate text-xs"
                style={{ color: "var(--color-text-secondary)" }}
              >
                {subtitle}
              </p>
            )}
          </div>
        </div>
        {action}
      </div>
    )}
    <div className={`p-5 ${bodyClassName}`} style={bodyStyle}>{children}</div>
  </div>
);

export default Card;
