/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',

  // Configuration pour la production
  reactStrictMode: true,
  swcMinify: true,

  // Variables d'environnement publiques
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'OpenMedia',
  },

  // Headers de sécurité
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },

  // Optimisation des images
  images: {
    domains: [
      'image.tmdb.org',  // TMDB images
      'localhost',
    ],
    formats: ['image/webp', 'image/avif'],
  },

  // Webpack configuration personnalisée si nécessaire
  webpack: (config, { isServer }) => {
    // Modifications webpack ici si besoin
    return config;
  },
};

module.exports = nextConfig;
