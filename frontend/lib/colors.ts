// Sequential single-hue (blue) ramps for magnitude encoding — low -> high severity.
// Values from the dataviz skill's validated reference palette (references/palette.md).
const SEVERITY_RAMP_LIGHT = [
  "#cde2fb",
  "#9ec5f4",
  "#5598e7",
  "#2a78d6",
  "#1c5cab",
  "#0d366b",
];

const SEVERITY_RAMP_DARK = [
  "#20334a",
  "#284370",
  "#2f5590",
  "#3987e5",
  "#6da7ec",
  "#9ec5f4",
];

// Categorical palette, fixed order — from the dataviz skill's validated
// reference palette (references/palette.md). Never cycled/reordered per-render.
export const CATEGORICAL_LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"];
export const CATEGORICAL_DARK = ["#3987e5", "#d95926", "#199e70", "#c98500"];

export function categoricalColor(index: number, isDark: boolean): string {
  const palette = isDark ? CATEGORICAL_DARK : CATEGORICAL_LIGHT;
  return palette[index % palette.length];
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

function hexToRgb(hex: string): [number, number, number] {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function rgbToHex([r, g, b]: [number, number, number]): string {
  const toHex = (v: number) => Math.round(v).toString(16).padStart(2, "0");
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

/**
 * Map a severity score (0..1-ish, unbounded above in practice) to a step on the
 * sequential blue ramp. `maxSeverity` calibrates what counts as "fully saturated"
 * for the current dataset, so the ramp uses the full visual range.
 */
export function severityColor(
  severity: number,
  maxSeverity: number,
  isDark: boolean,
): string {
  const ramp = isDark ? SEVERITY_RAMP_DARK : SEVERITY_RAMP_LIGHT;
  const t = maxSeverity > 0 ? Math.min(Math.max(severity / maxSeverity, 0), 1) : 0;
  const scaled = t * (ramp.length - 1);
  const lowIndex = Math.floor(scaled);
  const highIndex = Math.min(lowIndex + 1, ramp.length - 1);
  const frac = scaled - lowIndex;

  const low = hexToRgb(ramp[lowIndex]);
  const high = hexToRgb(ramp[highIndex]);
  return rgbToHex([
    lerp(low[0], high[0], frac),
    lerp(low[1], high[1], frac),
    lerp(low[2], high[2], frac),
  ]);
}
