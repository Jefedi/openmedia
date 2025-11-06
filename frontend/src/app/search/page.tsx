'use client';

import { useState } from 'react';
import Link from 'next/link';
import MediaCard from '@/components/MediaCard';

interface SearchResult {
  id: number;
  title?: string;
  name?: string;
  year?: number;
  poster_path?: string;
  vote_average?: number;
  overview?: string;
  imdb_id: string;
  type: 'movie' | 'series';
}

interface SearchResponse {
  query: string;
  movies: SearchResult[];
  series: SearchResult[];
  from_cache: boolean;
  from_omdb: boolean;
  message?: string;
  error?: string;
}

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!query.trim()) return;

    setLoading(true);

    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Search error:', error);
      setResults({
        query,
        movies: [],
        series: [],
        from_cache: false,
        from_omdb: false,
        error: 'Erreur lors de la recherche'
      });
    } finally {
      setLoading(false);
    }
  };

  const totalResults = (results?.movies?.length || 0) + (results?.series?.length || 0);

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      {/* Header */}
      <header className="border-b border-gray-700 bg-black/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition">
              <span className="text-3xl"><¬</span>
              <h1 className="text-2xl font-bold">OpenMedia</h1>
            </Link>
            <nav className="flex gap-6 items-center">
              <Link href="/movies" className="hover:text-blue-400 transition">
                Films
              </Link>
              <Link href="/series" className="hover:text-blue-400 transition">
                Séries
              </Link>
              <Link href="/search" className="text-blue-400">
                Recherche
              </Link>
              <div className="flex gap-3 ml-4">
                <Link
                  href="/login"
                  className="px-4 py-2 rounded-lg border border-gray-600 hover:border-gray-500 transition"
                >
                  Connexion
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 transition"
                >
                  S'inscrire
                </Link>
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Search Section */}
      <section className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold mb-8 text-center">= Recherche Intelligente</h1>

          {/* Info Box */}
          <div className="bg-blue-900/20 border border-blue-600/50 rounded-lg p-4 mb-8">
            <p className="text-blue-200 text-sm">
              =¡ <strong>Recherche optimisée :</strong> Nous cherchons d'abord dans notre base de données.
              Si le film/série n'est pas trouvé, nous le recherchons sur OMDb et l'ajoutons automatiquement
              à notre collection pour les prochaines recherches.
            </p>
          </div>

          {/* Search Form */}
          <form onSubmit={handleSearch} className="mb-8">
            <div className="flex gap-3">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Rechercher un film ou une série..."
                className="flex-1 px-6 py-4 bg-gray-800 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
                autoFocus
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="px-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold transition text-lg"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Recherche...
                  </span>
                ) : (
                  'Rechercher'
                )}
              </button>
            </div>
          </form>

          {/* Results Info */}
          {results && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">
                  {totalResults > 0 ? (
                    `${totalResults} résultat${totalResults > 1 ? 's' : ''} pour "${results.query}"`
                  ) : (
                    `Aucun résultat pour "${results.query}"`
                  )}
                </h2>

                {/* Cache indicator */}
                {totalResults > 0 && (
                  <div className="flex items-center gap-2 text-sm">
                    {results.from_cache && (
                      <span className="px-3 py-1 bg-green-900/50 border border-green-600 rounded-full text-green-300">
                        ¡ Depuis le cache
                      </span>
                    )}
                    {results.from_omdb && (
                      <span className="px-3 py-1 bg-orange-900/50 border border-orange-600 rounded-full text-orange-300">
                        < Depuis OMDb (ajouté au cache)
                      </span>
                    )}
                  </div>
                )}
              </div>

              {results.error && (
                <div className="bg-red-900/20 border border-red-600 rounded-lg p-4 mb-6">
                  <p className="text-red-300">L {results.error}</p>
                </div>
              )}

              {results.message && totalResults === 0 && (
                <div className="bg-gray-800/50 rounded-lg p-12 text-center">
                  <p className="text-gray-400 text-lg">{results.message}</p>
                  <p className="text-gray-500 mt-4">Essayez avec un autre terme de recherche</p>
                </div>
              )}
            </div>
          )}

          {/* Movies Results */}
          {results && results.movies && results.movies.length > 0 && (
            <div className="mb-12">
              <h3 className="text-2xl font-bold mb-4"><¥ Films ({results.movies.length})</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {results.movies.map((movie) => (
                  <MediaCard
                    key={movie.id}
                    id={movie.id}
                    title={movie.title || ''}
                    year={movie.year}
                    posterPath={movie.poster_path}
                    voteAverage={movie.vote_average}
                    type="movie"
                    overview={movie.overview}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Series Results */}
          {results && results.series && results.series.length > 0 && (
            <div className="mb-12">
              <h3 className="text-2xl font-bold mb-4">=ú Séries ({results.series.length})</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {results.series.map((series) => (
                  <MediaCard
                    key={series.id}
                    id={series.id}
                    title={series.name || ''}
                    year={series.year}
                    posterPath={series.poster_path}
                    voteAverage={series.vote_average}
                    type="series"
                    overview={series.overview}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 text-center text-gray-500 mt-12">
        <p>OpenMedia v0.1.0 - Plateforme Open Source de Films & Séries</p>
        <p className="text-sm mt-2">Propulsé par FastAPI, Next.js, PostgreSQL & OMDb</p>
      </footer>
    </main>
  );
}
