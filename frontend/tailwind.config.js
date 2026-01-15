/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#0E1117',
        panel: '#111827',
        border: '#1F2937',
        text: '#E6E8EB',
        muted: '#9AA0A6',
        enrollment: '#14B8A6', // teal
        demographic: '#E0B15C', // amber
        biometric: '#6C7FF2', // indigo
        anomaly: '#C44536', // crimson
      },
      fontFamily: {
        display: ['"DM Sans"', 'Inter', 'system-ui', 'sans-serif'],
        body: ['"DM Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        panel: '0 10px 40px rgba(0,0,0,0.25)',
      },
    },
  },
  plugins: [],
}

