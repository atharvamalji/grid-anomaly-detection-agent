"use client";

import { useEffect, useState } from "react";

type Theme = "light" | "dark";

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("light");

  useEffect(() => {
    const current = document.documentElement.getAttribute("data-theme");
    if (current === "dark" || current === "light") {
      setTheme(current);
    } else {
      setTheme(
        window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light",
      );
    }
  }, []);

  const toggle = () => {
    const next: Theme = theme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
    setTheme(next);
  };

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      className="fixed top-4 right-4 z-40 flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium shadow-sm"
      style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)", color: "var(--text-secondary)" }}
    >
      {theme === "dark" ? (
        <>
          <span aria-hidden>☀️</span> Light
        </>
      ) : (
        <>
          <span aria-hidden>🌙</span> Dark
        </>
      )}
    </button>
  );
}
