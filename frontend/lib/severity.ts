import type { CSSProperties } from "react";

// Status colors from the dataviz skill's validated reference palette — fixed,
// never themed, distinct from the categorical series colors.
export function severityBadgeStyle(score: number): CSSProperties {
  if (score >= 0.03) {
    return { backgroundColor: "var(--diverging-mid)", color: "var(--status-critical)" };
  }
  if (score >= 0.015) {
    return { backgroundColor: "var(--diverging-mid)", color: "var(--status-serious)" };
  }
  return { backgroundColor: "var(--gridline)", color: "var(--text-secondary)" };
}
