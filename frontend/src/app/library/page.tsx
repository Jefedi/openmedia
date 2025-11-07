'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import MediaCard from '@/components/MediaCard';

interface WatchlistItem {
  id: number;
  media_type: 'movie' | 'series';
  media_id: number;
  title: string;
  year?: number;
  poster_path?: string;
  vote_average?: number;
  priority?: number;
  notes?: string;
  added_at: string;
}

export default function LibraryPage() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'movie' | 'series'>('all');
  const router = useRouter();

  useEffect(() => {
    const fetchWatchlist = async () => {
      const token = localStorage.getItem('access_token');

      if (!token) {
        router.push('/login');
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const url = filter === 'all'
          ? '/api/library/watchlist'
          : `/api/library/watchlist?media_type=${filter}`;

        console.log('Fetching watchlist from:', url);
        console.log('Token present:', !!token);

        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        console.log('Response status:', response.status);

        if (response.status === 401) {
          console.error('Unauthorized - redirecting to login');
          router.push('/login');
          return;
        }

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          console.error('API error:', response.status, errorData);
          throw new Error(errorData.error?.message || errorData.detail || 'Failed to fetch watchlist');
        }

        const data = await response.json();
        console.log('Watchlist data received:', data);
        setWatchlist(data.watchlist || []);
      } catch (err: any) {
        console.error('Error fetching watchlist:', err);
        setError(`Impossible de charger votre bibliothèque: ${err.message || 'Erreur inconnue'}`);
      } finally {
        setLoading(false);
      }
    };

    fetchWatchlist();
  }, [filter, router]);

  const handleRemoveFromWatchlist = async (mediaType: string, mediaId: number) => {
    const token = localStorage.getItem('access_token');

    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const response = await fetch(
        `/api/library/watchlist?media_type=${mediaType}&media_id=${mediaId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        // Remove from local state
        setWatchlist(watchlist.filter(item =>
          !(item.media_type === mediaType && item.media_id === mediaId)
        ));
      } else {
        console.error('Failed to remove from watchlist');
      }
    } catch (error) {
      console.error('Error removing from watchlist:', error);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      <Header />

      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">📚 Ma Bibliothèque</h1>
          <p className="text-gray-400 text-lg">
            Gérez vos films et séries à voir
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-4 mb-8 border-b border-gray-700">
          <button
            onClick={() => setFilter('all')}
            className={`px-6 py-3 font-semibold transition ${
              filter === 'all'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Tout
          </button>
          <button
            onClick={() => setFilter('movie')}
            className={`px-6 py-3 font-semibold transition ${
              filter === 'movie'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            🎬 Films
          </button>
          <button
            onClick={() => setFilter('series')}
            className={`px-6 py-3 font-semibold transition ${
              filter === 'series'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            📺 Séries
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-gray-800 rounded-lg aspect-[2/3] animate-pulse"></div>
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 text-center">
            <p className="text-red-300 text-lg">{error}</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && watchlist.length === 0 && (
          <div className="bg-gray-800/50 rounded-lg p-12 text-center">
            <div className="text-6xl mb-4">🎬</div>
            <h2 className="text-2xl font-bold mb-4">Votre liste est vide</h2>
            <p className="text-gray-400 mb-8">
              {filter === 'all'
                ? 'Commencez à ajouter des films et séries à votre liste'
                : filter === 'movie'
                ? 'Aucun film dans votre liste'
                : 'Aucune série dans votre liste'}
            </p>
            <button
              onClick={() => router.push('/search')}
              className="inline-block px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition"
            >
              Découvrir des {filter === 'movie' ? 'films' : filter === 'series' ? 'séries' : 'contenus'}
            </button>
          </div>
        )}

        {/* Watchlist Grid */}
        {!loading && !error && watchlist.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">
                {watchlist.length} {watchlist.length > 1 ? 'éléments' : 'élément'}
              </h2>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {watchlist.map((item) => (
                <div key={`${item.media_type}-${item.media_id}`} className="relative group">
                  <MediaCard
                    id={item.media_id}
                    title={item.title}
                    year={item.year}
                    posterPath={item.poster_path}
                    voteAverage={item.vote_average}
                    type={item.media_type}
                  />

                  {/* Remove Button Overlay */}
                  <button
                    onClick={() => handleRemoveFromWatchlist(item.media_type, item.media_id)}
                    className="absolute top-2 right-2 bg-red-600 hover:bg-red-700 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Retirer de ma liste"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>

                  {/* Priority Badge */}
                  {item.priority !== undefined && item.priority > 0 && (
                    <div className="absolute top-2 left-2 bg-yellow-500 text-black px-2 py-1 rounded text-xs font-bold">
                      Priorité {item.priority}
                    </div>
                  )}

                  {/* Notes Indicator */}
                  {item.notes && (
                    <div className="absolute bottom-2 left-2 bg-blue-600 text-white p-1 rounded" title={item.notes}>
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                      </svg>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
