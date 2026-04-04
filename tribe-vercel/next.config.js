/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@gradio/client'],
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**.hf.space' },
      { protocol: 'https', hostname: 'huggingface.co' },
    ],
  },
};

module.exports = nextConfig;
