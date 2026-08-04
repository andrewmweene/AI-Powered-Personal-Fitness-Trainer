/**
 * Tailwind CSS configuration for the React frontend.
 */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#1976D2',
        success: '#388E3C',
        warning: '#F57C00',
        danger: '#D32F2F',
        surface: '#F5F7FA',
      },
    },
  },
  plugins: [],
};
