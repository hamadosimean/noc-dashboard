import { create } from "zustand";

const now = new Date();

export const usePeriodStore = create((set, get) => ({
  month: now.getMonth() + 1,
  year: now.getFullYear(),
  setPeriod: (month, year) => set({ month, year }),
  goToPreviousMonth: () => {
    const { month, year } = get();
    set(
      month === 1 ? { month: 12, year: year - 1 } : { month: month - 1, year },
    );
  },
  goToNextMonth: () => {
    const { month, year } = get();
    set(
      month === 12 ? { month: 1, year: year + 1 } : { month: month + 1, year },
    );
  },
}));
