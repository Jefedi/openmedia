'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="bg-gray-900/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Logo */}
          <Link href="/" className="text-2xl font-bold hover:text-blue-400 transition">
            🎬 OpenMedia
          </Link>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="flex-1 max-w-2xl w-full">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Rechercher un film ou une série..."
                className="w-full bg-gray-800 text-white px-4 py-3 pl-12 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
              />
              <svg
                className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </form>

          {/* Navigation */}
          <nav className="flex items-center gap-4">
            <Link
              href="/"
              className="text-gray-300 hover:text-white transition"
            >
              Accueil
            </Link>
            <Link
              href="/search"
              className="bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg transition"
            >
              Recherche avancée
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
