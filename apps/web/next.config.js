/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // By default, Next.js 14 App Router routes in src/app/api/v1/[...slug]/route.ts
  // handle all API requests with zero external host dependencies.
  async rewrites() {
    if (process.env.PROXY_EXTERNAL_BACKEND === "true" && process.env.BACKEND_API_URL) {
      return [
        {
          source: "/api/:path*",
          destination: `${process.env.BACKEND_API_URL}/api/:path*`,
        },
      ];
    }
    return [];
  },
};

module.exports = nextConfig;
