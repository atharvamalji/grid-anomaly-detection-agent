import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Minimal production image for Docker — only traced files + node_modules
  // subset get copied into .next/standalone.
  output: "standalone",
};

export default nextConfig;
