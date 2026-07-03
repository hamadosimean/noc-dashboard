import { useThemeStore } from '../store/theme';
import { CATEGORICAL, CHART_CHROME, STATUS } from '../theme/colors';

// Chart.js reads plain colors, not CSS custom properties — this hook exposes
// the current theme's chrome + categorical ramp so every chart stays in sync
// with the header's dark/light toggle.
export const useChartTheme = () => {
  const { theme } = useThemeStore();
  return {
    theme,
    chrome: CHART_CHROME[theme],
    categorical: CATEGORICAL[theme],
    status: STATUS,
  };
};
