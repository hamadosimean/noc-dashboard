import { create } from "zustand";

const STORAGE_KEY = "noc-theme";

const applyThemeClass = (theme) => {
  document.documentElement.classList.toggle("dark", theme === "dark");
};

const getInitialTheme = () => {
  const stored =
    typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
  return stored === "light" ? "light" : "dark"; // dark is the default, prioritized theme
};

const initialTheme = getInitialTheme();
if (typeof document !== "undefined") applyThemeClass(initialTheme);

export const useThemeStore = create((set, get) => ({
  theme: initialTheme,
  toggleTheme: () => {
    const next = get().theme === "dark" ? "light" : "dark";
    localStorage.setItem(STORAGE_KEY, next);
    applyThemeClass(next);
    set({ theme: next });
  },
}));
