/** @type {import('next').NextConfig} */
const backendApi = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_API_URL || "http://127.0.0.1:8001";

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendApi}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
