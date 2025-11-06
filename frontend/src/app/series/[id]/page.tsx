'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';

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
  tagline?: string;
  vote_average?: number;
  vote_count?: number;
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
      <div className="min-h-screen bg-gray-900 text-white">
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-96 bg-gray-800 rounded-lg mb-8"></div>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="h-96 bg-gray-800 rounded-lg"></div>
              <div className="md:col-span-2 space-y-4">
                <div className="h-8 bg-gray-800 rounded w-3/4"></div>
                <div className="h-4 bg-gray-800 rounded w-1/2"></div>
                <div className="h-32 bg-gray-800 rounded"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !series) {
    return (
      <div className="min-h-screen bg-gray-900 text-white">
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
  const backdropUrl = series.backdrop_path || '';
  const rating = series.imdb_rating || series.vote_average || series.rating;
  const ratingPercent = rating ? Math.round(Number(rating) * 10) : 0;
  const genres = series.genre ? series.genre.split(',').map(g => g.trim()) : [];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-900/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
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
      </header>

      {/* Backdrop Section */}
      <div className="relative">
        {/* Backdrop Image */}
        {backdropUrl && (
          <div className="absolute inset-0 w-full h-full">
            <Image
              src={backdropUrl}
              alt={series.name}
              fill
              className="object-cover opacity-30"
              priority
            />
            <div className="absolute inset-0 bg-gradient-to-r from-gray-900 via-gray-900/95 to-gray-900/80"></div>
          </div>
        )}

        {/* Content */}
        <div className="relative container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-[300px,1fr] gap-8">
            {/* Poster */}
            <div className="flex flex-col items-center md:items-start">
              <div className="relative w-full max-w-[300px] aspect-[2/3] rounded-lg overflow-hidden shadow-2xl">
                <Image
                  src={posterUrl}
                  alt={series.name}
                  fill
                  className="object-cover"
                  priority
                />
              </div>

              {/* IMDb Link */}
              {series.imdb_id && (
                <a
                  href={`https://www.imdb.com/title/${series.imdb_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-4 w-full max-w-[300px] bg-yellow-500 hover:bg-yellow-600 text-black font-bold text-center py-3 rounded-lg transition"
                >
                  Voir sur IMDb
                </a>
              )}
            </div>

            {/* Series Info */}
            <div className="flex flex-col justify-center">
              {/* Title */}
              <h1 className="text-4xl md:text-5xl font-bold mb-2">
                {series.name}
                {series.year && <span className="text-gray-400 font-normal ml-3">({series.year})</span>}
              </h1>

              {/* Original Title */}
              {series.original_name && series.original_name !== series.name && (
                <p className="text-xl text-gray-400 italic mb-4">{series.original_name}</p>
              )}

              {/* Tagline */}
              {series.tagline && (
                <p className="text-lg text-gray-300 italic mb-4">{series.tagline}</p>
              )}

              {/* Meta Info */}
              <div className="flex flex-wrap items-center gap-4 mb-6 text-lg">
                {series.released && (
                  <span className="text-gray-300">{new Date(series.released).toLocaleDateString('fr-FR')}</span>
                )}
                {genres.length > 0 && (
                  <>
                    <span className="text-gray-500">•</span>
                    <div className="flex flex-wrap gap-2">
                      {genres.map((genre, i) => (
                        <span key={i} className="px-3 py-1 bg-purple-600/30 border border-purple-500/50 rounded-full text-sm">
                          {genre}
                        </span>
                      ))}
                    </div>
                  </>
                )}
                {series.total_seasons && (
                  <>
                    <span className="text-gray-500">•</span>
                    <span className="text-gray-300">
                      {series.total_seasons} saison{series.total_seasons > 1 ? 's' : ''}
                    </span>
                  </>
                )}
              </div>

              {/* Rating */}
              {rating && (
                <div className="flex items-center gap-6 mb-6">
                  <div className="flex items-center gap-3">
                    <div className="relative w-16 h-16">
                      <svg className="w-16 h-16 transform -rotate-90">
                        <circle
                          cx="32"
                          cy="32"
                          r="28"
                          stroke="currentColor"
                          strokeWidth="4"
                          fill="none"
                          className="text-gray-700"
                        />
                        <circle
                          cx="32"
                          cy="32"
                          r="28"
                          stroke="currentColor"
                          strokeWidth="4"
                          fill="none"
                          strokeDasharray={`${2 * Math.PI * 28}`}
                          strokeDashoffset={`${2 * Math.PI * 28 * (1 - ratingPercent / 100)}`}
                          className={
                            ratingPercent >= 70
                              ? 'text-green-500'
                              : ratingPercent >= 50
                              ? 'text-yellow-500'
                              : 'text-red-500'
                          }
                          strokeLinecap="round"
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-xl font-bold">{ratingPercent}%</span>
                      </div>
                    </div>
                    <div>
                      <p className="font-semibold">Note</p>
                      <p className="text-sm text-gray-400">utilisateurs</p>
                    </div>
                  </div>

                  {series.imdb_rating && (
                    <div className="flex items-center gap-2">
                      <span className="text-yellow-400 text-2xl">⭐</span>
                      <div>
                        <p className="font-semibold">{Number(series.imdb_rating).toFixed(1)}/10</p>
                        <p className="text-sm text-gray-400">IMDb</p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Overview/Plot */}
              {(series.plot || series.overview) && (
                <div className="mb-6">
                  <h2 className="text-2xl font-bold mb-3">Synopsis</h2>
                  <p className="text-gray-300 text-lg leading-relaxed">
                    {series.plot || series.overview}
                  </p>
                </div>
              )}

              {/* Crew Info */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {series.director && (
                  <div>
                    <p className="text-sm text-gray-400 mb-1">Créateur</p>
                    <p className="font-semibold">{series.director}</p>
                  </div>
                )}
                {series.actors && (
                  <div className="md:col-span-2">
                    <p className="text-sm text-gray-400 mb-1">Acteurs principaux</p>
                    <p className="font-semibold">{series.actors.split(',').slice(0, 3).join(', ')}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Information */}
      <div className="bg-gray-800/50 border-t border-gray-700">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Cast */}
            {series.actors && (
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span>🎭</span> Distribution
                </h3>
                <div className="space-y-2">
                  {series.actors.split(',').slice(0, 5).map((actor, i) => (
                    <p key={i} className="text-gray-300">{actor.trim()}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Details */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <span>ℹ️</span> Informations
              </h3>
              <dl className="space-y-3">
                {series.country && (
                  <div>
                    <dt className="text-sm text-gray-400">Pays</dt>
                    <dd className="text-gray-200">{series.country}</dd>
                  </div>
                )}
                {series.language && (
                  <div>
                    <dt className="text-sm text-gray-400">Langue</dt>
                    <dd className="text-gray-200">{series.language}</dd>
                  </div>
                )}
                {series.total_seasons && (
                  <div>
                    <dt className="text-sm text-gray-400">Nombre de saisons</dt>
                    <dd className="text-gray-200">{series.total_seasons}</dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Awards */}
            {series.awards && (
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span>🏆</span> Récompenses
                </h3>
                <p className="text-gray-300">{series.awards}</p>
              </div>
            )}
          </div>

          {/* Seasons - Placeholder for future implementation */}
          {series.total_seasons && series.total_seasons > 0 && (
            <div className="mt-8">
              <h3 className="text-2xl font-bold mb-4">Saisons</h3>
              <div className="bg-gray-800 rounded-lg p-6">
                <p className="text-gray-400">
                  Cette série comporte {series.total_seasons} saison{series.total_seasons > 1 ? 's' : ''}.
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Les détails des saisons et épisodes seront bientôt disponibles.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
