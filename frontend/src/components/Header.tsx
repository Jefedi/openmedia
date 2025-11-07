'use client';

import { useState, FormEvent, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface SearchResult {
  id: number;
  title?: string;
  name?: string;
  year?: number;
  poster_path?: string;
  vote_average?: number;
  type: 'movie' | 'series';
}

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<SearchResult[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [username, setUsername] = useState('');
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const router = useRouter();
  const searchRef = useRef<HTMLFormElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Check authentication status and load profile
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUsername = localStorage.getItem('username');

    if (token) {
      setIsAuthenticated(true);
      setUsername(storedUsername || 'Utilisateur');

      // Fetch user profile to get avatar
      fetch('/api/profile/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
        .then(res => res.json())
        .then(data => {
          if (data.avatar_url) {
            // Convert relative URL to full backend URL
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:18000';
            setAvatarUrl(`${apiUrl}${data.avatar_url}`);
          }
        })
        .catch(err => console.error('Error fetching profile:', err));
    } else {
      setIsAuthenticated(false);
    }
  }, []);

  // Close suggestions and user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search
  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(searchQuery.trim())}`);
        const data = await response.json();

        // Combine and limit results to top 8
        const combined = [
          ...(data.movies || []).map((m: any) => ({ ...m, type: 'movie' as const })),
          ...(data.series || []).map((s: any) => ({ ...s, type: 'series' as const }))
        ].slice(0, 8);

        setSuggestions(combined);
        setShowSuggestions(true);
      } catch (error) {
        console.error('Search error:', error);
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    }, 300); // Wait 300ms after user stops typing

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setShowSuggestions(false);
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleResultClick = (result: SearchResult) => {
    setShowSuggestions(false);
    setSearchQuery('');
    router.push(`/${result.type === 'movie' ? 'movies' : 'series'}/${result.id}`);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    setIsAuthenticated(false);
    setShowUserMenu(false);
    router.push('/');
    window.location.reload(); // Force refresh to update auth state
  };

  return (
    <header className="bg-gray-900/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Logo */}
          <Link href="/" className="text-2xl font-bold hover:text-blue-400 transition">
            🎬 OpenMedia
          </Link>

          {/* Search Bar with Suggestions */}
          <form onSubmit={handleSearch} className="flex-1 max-w-2xl w-full relative" ref={searchRef}>
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                placeholder="Rechercher un film ou une série..."
                className="w-full bg-gray-800 text-white px-4 py-3 pl-12 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                autoComplete="off"
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
              {loading && (
                <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                  <svg className="animate-spin h-5 w-5 text-blue-500" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
              )}
            </div>

            {/* Suggestions Dropdown */}
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute top-full mt-2 w-full bg-gray-800 border border-gray-700 rounded-lg shadow-2xl overflow-hidden z-50 max-h-96 overflow-y-auto">
                {suggestions.map((result) => (
                  <button
                    key={`${result.type}-${result.id}`}
                    onClick={() => handleResultClick(result)}
                    className="w-full flex items-center gap-4 p-3 hover:bg-gray-700 transition text-left"
                  >
                    {/* Poster */}
                    <div className="w-12 h-16 flex-shrink-0 bg-gray-700 rounded overflow-hidden">
                      {result.poster_path && result.poster_path !== 'N/A' ? (
                        <img
                          src={result.poster_path}
                          alt={result.title || result.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-500">
                          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" />
                          </svg>
                        </div>
                      )}
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-semibold truncate">
                          {result.title || result.name}
                        </p>
                        <span className="text-xs px-2 py-0.5 rounded bg-blue-600 text-white flex-shrink-0">
                          {result.type === 'movie' ? '🎬' : '📺'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        {result.year && <span>{result.year}</span>}
                        {result.vote_average && result.vote_average > 0 && (
                          <>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              ⭐ {result.vote_average.toFixed(1)}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </button>
                ))}

                {/* See all results link */}
                {searchQuery.trim() && (
                  <Link
                    href={`/search?q=${encodeURIComponent(searchQuery.trim())}`}
                    className="block p-3 text-center text-blue-400 hover:bg-gray-700 transition border-t border-gray-700"
                    onClick={() => setShowSuggestions(false)}
                  >
                    Voir tous les résultats →
                  </Link>
                )}
              </div>
            )}
          </form>

          {/* Navigation */}
          <nav className="flex items-center gap-4">
            <Link
              href="/"
              className="text-gray-300 hover:text-white transition hidden sm:block"
            >
              Accueil
            </Link>
            <Link
              href="/search"
              className="text-gray-300 hover:text-white transition hidden sm:block"
            >
              Recherche
            </Link>

            {isAuthenticated ? (
              /* User Menu */
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg transition"
                >
                  {avatarUrl ? (
                    <img
                      src={avatarUrl}
                      alt={username}
                      className="w-8 h-8 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center font-bold">
                      {username.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <span className="hidden md:inline">{username}</span>
                  <svg
                    className={`w-4 h-4 transition-transform ${showUserMenu ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Dropdown Menu */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-56 bg-gray-800 border border-gray-700 rounded-lg shadow-xl overflow-hidden z-50">
                    <div className="px-4 py-3 border-b border-gray-700">
                      <p className="text-sm text-gray-400">Connecté en tant que</p>
                      <p className="font-semibold truncate">{username}</p>
                    </div>

                    <Link
                      href="/library"
                      onClick={() => setShowUserMenu(false)}
                      className="flex items-center gap-3 px-4 py-3 hover:bg-gray-700 transition"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      <span>Ma Bibliothèque</span>
                    </Link>

                    <Link
                      href="/profile"
                      onClick={() => setShowUserMenu(false)}
                      className="flex items-center gap-3 px-4 py-3 hover:bg-gray-700 transition"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      <span>Mon Profil</span>
                    </Link>

                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-4 py-3 hover:bg-red-900/20 text-red-400 transition border-t border-gray-700"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      <span>Déconnexion</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              /* Login Button */
              <Link
                href="/login"
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition font-semibold"
              >
                Connexion
              </Link>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
