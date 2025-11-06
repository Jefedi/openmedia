'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

interface Series {
  id: number;
  name: string;
  original_name?: string;
  year?: number;
  total_seasons?: number;
  rating?: number;
  imdb_rating?: number;
  imdb_id?: string;
  overview?: string;
  poster_path?: string;
  backdrop_path?: string;
  genre?: string;
  director?: string;
  actors?: string;
  plot?: string;
  awards?: string;
  country?: string;
  language?: string;
  released?: string;
  created_at?: string;
}

export default function SeriesDetailPage() {
  const params = useParams();
  const [series, setSeries] = useState<Series | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSeries = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/series/${params.id}`);

        if (!response.ok) {
          if (response.status === 404) {
            setError('Série non trouvée');
          } else {
            setError('Erreur lors du chargement de la série');
          }
          return;
        }

        const data = await response.json();
        setSeries(data);
      } catch (err) {
        console.error('Error fetching series:', err);
        setError('Erreur lors du chargement de la série');
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchSeries();
    }
  }, [params.id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-700 rounded w-1/4 mb-4"></div>
            <div className="h-96 bg-gray-700 rounded mb-4"></div>
            <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-gray-700 rounded w-2/3"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !series) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 text-center">
            <p className="text-xl mb-4">❌ {error || 'Série non trouvée'}</p>
            <Link
              href="/"
              className="inline-block bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg transition"
            >
              Retour à l'accueil
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const posterUrl = series.poster_path || 'https://via.placeholder.com/300x450?text=No+Poster';
  const rating = series.imdb_rating || series.rating;

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
      {/* Header */}
      <div className="bg-gray-900/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold hover:text-blue-400 transition">
            🎬 OpenMedia
          </Link>
          <Link
            href="/search"
            className="bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg transition"
          >
            🔍 Rechercher
          </Link>
        </div>
      </div>

      {/* Backdrop */}
      {series.backdrop_path && (
        <div
          className="h-96 bg-cover bg-center relative"
          style={{
            backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.9)), url(${series.backdrop_path})`,
          }}
        >
          <div className="absolute bottom-0 left-0 right-0 p-8">
            <div className="container mx-auto">
              <h1 className="text-5xl font-bold mb-2">{series.name}</h1>
              {series.original_name && series.original_name !== series.name && (
                <p className="text-gray-300 text-xl mb-2">({series.original_name})</p>
              )}
              <div className="flex items-center gap-4 text-lg">
                {series.year && <span className="text-gray-300">{series.year}</span>}
                {series.total_seasons && (
                  <span className="text-gray-300">
                    • {series.total_seasons} saison{series.total_seasons > 1 ? 's' : ''}
                  </span>
                )}
                {rating && (
                  <span className="bg-yellow-500 text-black px-3 py-1 rounded-full font-bold">
                    ⭐ {rating}/10
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Poster */}
          <div className="md:col-span-1">
            <img
              src={posterUrl}
              alt={series.name}
              className="w-full rounded-lg shadow-2xl"
            />

            {/* IMDb Link */}
            {series.imdb_id && (
              <a
                href={`https://www.imdb.com/title/${series.imdb_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="block mt-4 bg-yellow-500 hover:bg-yellow-600 text-black font-bold text-center py-3 rounded-lg transition"
              >
                Voir sur IMDb
              </a>
            )}
          </div>

          {/* Details */}
          <div className="md:col-span-2">
            {/* Genre */}
            {series.genre && (
              <div className="mb-6">
                <div className="flex flex-wrap gap-2">
                  {series.genre.split(',').map((g, i) => (
                    <span
                      key={i}
                      className="bg-purple-600 px-3 py-1 rounded-full text-sm"
                    >
                      {g.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Plot/Overview */}
            {(series.plot || series.overview) && (
              <div className="mb-6">
                <h2 className="text-2xl font-bold mb-3">Synopsis</h2>
                <p className="text-gray-300 text-lg leading-relaxed">
                  {series.plot || series.overview}
                </p>
              </div>
            )}

            {/* Additional Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              {series.director && (
                <div>
                  <h3 className="text-gray-400 text-sm mb-1">Créateur</h3>
                  <p className="text-white">{series.director}</p>
                </div>
              )}

              {series.actors && (
                <div>
                  <h3 className="text-gray-400 text-sm mb-1">Acteurs</h3>
                  <p className="text-white">{series.actors}</p>
                </div>
              )}

              {series.released && (
                <div>
                  <h3 className="text-gray-400 text-sm mb-1">Première diffusion</h3>
                  <p className="text-white">{series.released}</p>
                </div>
              )}

              {series.country && (
                <div>
                  <h3 className="text-gray-400 text-sm mb-1">Pays</h3>
                  <p className="text-white">{series.country}</p>
                </div>
              )}

              {series.language && (
                <div>
                  <h3 className="text-gray-400 text-sm mb-1">Langue</h3>
                  <p className="text-white">{series.language}</p>
                </div>
              )}

              {series.awards && (
                <div className="md:col-span-2">
                  <h3 className="text-gray-400 text-sm mb-1">Récompenses</h3>
                  <p className="text-white">{series.awards}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
