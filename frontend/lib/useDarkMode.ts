"use client";

import { useEffect, useState } from "react";

function computeIsDark(): boolean {
  const explicit = document.documentElement.getAttribute("data-theme");
  if (explicit === "dark") return true;
  if (explicit === "light") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

/**
 * Tracks the effective theme (manual `data-theme` toggle, falling back to OS
 * preference), so chart colors computed in JS follow the same theme as the
 * CSS-variable-driven chrome.
 */
export function useDarkMode(): boolean {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Reading `document`/`window` can only happen after mount (SSR has
    // neither), so this initial sync must run in an effect, not render.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsDark(computeIsDark());

    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    const onMqlChange = () => setIsDark(computeIsDark());
    mql.addEventListener("change", onMqlChange);

    const observer = new MutationObserver(() => setIsDark(computeIsDark()));
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });

    return () => {
      mql.removeEventListener("change", onMqlChange);
      observer.disconnect();
    };
  }, []);

  return isDark;
}
