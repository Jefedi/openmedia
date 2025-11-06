'use client';

import { useEffect, useState } from 'react';

interface HealthStatus {
  status: string;
  version: string;
  environment: string;
}

export default function Home() {
  const [apiHealth, setApiHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:18000/health')
      .then(res => res.json())
      .then(data => {
        setApiHealth(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      {/* Header */}
      <header className="border-b border-gray-700 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-3xl">🎬</span>
              <h1 className="text-2xl font-bold">OpenMedia</h1>
            </div>
            <nav className="flex gap-4">
              <a
                href="http://localhost:18000/api/v1/docs"
                target="_blank"
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 transition"
              >
                API Docs
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-600 text-transparent bg-clip-text">
            Your All-in-One Movie & Series Platform
          </h2>
          <p className="text-xl text-gray-300 mb-12">
            Track, discover, and manage your favorite movies and TV shows with OpenMedia
          </p>

          {/* Status Card */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-8 mb-12">
            <h3 className="text-2xl font-bold mb-6">🚀 Platform Status</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-gray-900/50 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400">API Status</span>
                  {loading ? (
                    <span className="text-yellow-500">⏳ Checking...</span>
                  ) : apiHealth ? (
                    <span className="text-green-500">✅ {apiHealth.status}</span>
                  ) : (
                    <span className="text-red-500">❌ Offline</span>
                  )}
                </div>
                {apiHealth && (
                  <div className="text-sm text-gray-500">
                    Version: {apiHealth.version} | Env: {apiHealth.environment}
                  </div>
                )}
              </div>

              <div className="bg-gray-900/50 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400">Database</span>
                  <span className="text-green-500">✅ PostgreSQL 15</span>
                </div>
                <div className="text-sm text-gray-500">
                  19 tables created
                </div>
              </div>
            </div>
          </div>

          {/* Admin Credentials */}
          <div className="bg-yellow-900/20 border border-yellow-600/50 rounded-xl p-6 mb-12">
            <h3 className="text-xl font-bold mb-4 text-yellow-400">🔐 Admin Credentials</h3>
            <div className="text-left space-y-2 font-mono text-sm">
              <div>
                <span className="text-gray-400">Email:</span>{' '}
                <span className="text-white">admin@openmedia.local</span>
              </div>
              <div>
                <span className="text-gray-400">Password:</span>{' '}
                <span className="text-white">2wEKIewcTKJi4q6RDF_Zi0Y91lE5zdfkInkH4UsJSdc</span>
              </div>
            </div>
            <p className="text-yellow-400 text-sm mt-4">
              ⚠️ Change this password after first login!
            </p>
          </div>

          {/* Quick Links */}
          <div className="grid md:grid-cols-3 gap-6">
            <a
              href="http://localhost:18000/api/v1/docs"
              target="_blank"
              className="bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-xl p-6 transition group"
            >
              <div className="text-4xl mb-4">📚</div>
              <h4 className="text-lg font-bold mb-2">API Documentation</h4>
              <p className="text-gray-400 text-sm">
                Interactive Swagger UI
              </p>
            </a>

            <a
              href="http://localhost:18000/api/v1/redoc"
              target="_blank"
              className="bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-xl p-6 transition group"
            >
              <div className="text-4xl mb-4">📖</div>
              <h4 className="text-lg font-bold mb-2">ReDoc</h4>
              <p className="text-gray-400 text-sm">
                Alternative API docs
              </p>
            </a>

            <a
              href="http://localhost:17700"
              target="_blank"
              className="bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-xl p-6 transition group"
            >
              <div className="text-4xl mb-4">🔍</div>
              <h4 className="text-lg font-bold mb-2">Meilisearch</h4>
              <p className="text-gray-400 text-sm">
                Search engine dashboard
              </p>
            </a>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-20 border-t border-gray-800">
        <div className="max-w-4xl mx-auto">
          <h3 className="text-3xl font-bold text-center mb-12">Platform Features</h3>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="flex items-start space-x-4">
              <span className="text-3xl">🎯</span>
              <div>
                <h4 className="font-bold mb-2">Track Your Watchlist</h4>
                <p className="text-gray-400">Keep track of movies and series you want to watch</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <span className="text-3xl">⭐</span>
              <div>
                <h4 className="font-bold mb-2">Rate & Review</h4>
                <p className="text-gray-400">Share your opinions and ratings with the community</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <span className="text-3xl">📊</span>
              <div>
                <h4 className="font-bold mb-2">Progress Tracking</h4>
                <p className="text-gray-400">Monitor your viewing progress across all series</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <span className="text-3xl">🌍</span>
              <div>
                <h4 className="font-bold mb-2">Streaming Availability</h4>
                <p className="text-gray-400">Find where to watch your favorite content</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 text-center text-gray-500">
        <p>OpenMedia v0.1.0 - Open Source Movie & Series Platform</p>
        <p className="text-sm mt-2">Built with FastAPI, Next.js, PostgreSQL & Meilisearch</p>
      </footer>
    </main>
  );
}
