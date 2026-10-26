/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0B0F19",
        surface: "#111827",
        surfaceHover: "#1E293B",
        borderSubtle: "#1F2937",
        safeGreen: "#10B981",
        cautionYellow: "#F59E0B",
        dangerRed: "#EF4444",
        agentIndigo: "#6366F1",
        voiceCyan: "#06B6D4",
      },
      animation: {
        "pulse-glow": "pulseGlow 2s infinite",
        "waveform": "wave 1.2s ease-in-out infinite alternate",
      },
      keyframes: {
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 15px rgba(99, 102, 241, 0.4)" },
          "50%": { boxShadow: "0 0 30px rgba(6, 182, 212, 0.7)" },
        },
        wave: {
          "0%": { height: "6px" },
          "100%": { height: "24px" },
        },
      },
    },
  },
  plugins: [],
};
