/** @type {import('next').NextConfig} */
const backendApi = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_API_URL;

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    if (!backendApi) {
      // In local development without env, fallback to local backend port 8001
      // In Vercel serverless mode, rewrites are handled by vercel.json -> /api/index.py
      return process.env.NODE_ENV === "development"
        ? [
            {
              source: "/api/:path*",
              destination: "http://127.0.0.1:8001/api/:path*",
            },
          ]
        : [];
    }
    return [
      {
        source: "/api/:path*",
        destination: `${backendApi}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
