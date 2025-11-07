'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import LibraryActions from '@/components/LibraryActions';


interface Movie {
  id: number;
  title: string;
  original_title?: string;
  year?: number;
  runtime?: number;
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
  box_office?: string;
  production?: string;
  tagline?: string;
  vote_average?: number;
  vote_count?: number;
  created_at?: string;
}

export default function MovieDetailPage() {
  const params = useParams();
  const [movie, setMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMovie = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/movies/${params.id}`);

        if (!response.ok) {
          if (response.status === 404) {
            setError('Film non trouvé');
          } else {
            setError('Erreur lors du chargement du film');
          }
          return;
        }

        const data = await response.json();
        setMovie(data);
      } catch (err) {
        console.error('Error fetching movie:', err);
        setError('Erreur lors du chargement du film');
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchMovie();
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

  if (error || !movie) {
    return (
      <div className="min-h-screen bg-gray-900 text-white">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 text-center">
            <p className="text-xl mb-4">❌ {error || 'Film non trouvé'}</p>
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

  const posterUrl = movie.poster_path || 'https://via.placeholder.com/300x450?text=No+Poster';
  const backdropUrl = movie.backdrop_path || '';
  const rating = movie.imdb_rating || movie.vote_average || movie.rating;
  const ratingPercent = rating ? Math.round(Number(rating) * 10) : 0;
  const genres = movie.genre ? movie.genre.split(',').map(g => g.trim()) : [];

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
            <img src={backdropUrl} alt={movie?.title || ""} className="object-cover opacity-30" />
            <div className="absolute inset-0 bg-gradient-to-r from-gray-900 via-gray-900/95 to-gray-900/80"></div>
          </div>
        )}

        {/* Content */}
        <div className="relative container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-[300px,1fr] gap-8">
            {/* Poster */}
            <div className="flex flex-col items-center md:items-start">
              <div className="relative w-full max-w-[300px] aspect-[2/3] rounded-lg overflow-hidden shadow-2xl">
                <img src={posterUrl} alt={movie?.title || ""} className="w-full h-full object-cover" />
              </div>

              {/* IMDb Link */}
              {movie.imdb_id && (
                <a
                  href={`https://www.imdb.com/title/${movie.imdb_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-4 w-full max-w-[300px] bg-yellow-500 hover:bg-yellow-600 text-black font-bold text-center py-3 rounded-lg transition"
                >
                  Voir sur IMDb
                </a>
              )}
            </div>

            {/* Movie Info */}
            <div className="flex flex-col justify-center">
              {/* Title */}
              <h1 className="text-4xl md:text-5xl font-bold mb-2">
                {movie.title}
                {movie.year && <span className="text-gray-400 font-normal ml-3">({movie.year})</span>}
              </h1>

              {/* Original Title */}
              {movie.original_title && movie.original_title !== movie.title && (
                <p className="text-xl text-gray-400 italic mb-4">{movie.original_title}</p>
              )}

              {/* Tagline */}
              {movie.tagline && (
                <p className="text-lg text-gray-300 italic mb-4">{movie.tagline}</p>
              )}

              {/* Meta Info */}
              <div className="flex flex-wrap items-center gap-4 mb-6 text-lg">
                {movie.released && (
                  <span className="text-gray-300">{new Date(movie.released).toLocaleDateString('fr-FR')}</span>
                )}
                {genres.length > 0 && (
                  <>
                    <span className="text-gray-500">•</span>
                    <div className="flex flex-wrap gap-2">
                      {genres.map((genre, i) => (
                        <span key={i} className="px-3 py-1 bg-blue-600/30 border border-blue-500/50 rounded-full text-sm">
                          {genre}
                        </span>
                      ))}
                    </div>
                  </>
                )}
                {movie.runtime && (
                  <>
                    <span className="text-gray-500">•</span>
                    <span className="text-gray-300">{Math.floor(movie.runtime / 60)}h {movie.runtime % 60}min</span>
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

                  {movie.imdb_rating && (
                    <div className="flex items-center gap-2">
                      <span className="text-yellow-400 text-2xl">⭐</span>
                      <div>
                        <p className="font-semibold">{Number(movie.imdb_rating).toFixed(1)}/10</p>
                        <p className="text-sm text-gray-400">IMDb</p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Library Actions */}
              <div className="mb-6">
                <LibraryActions
                  mediaType="movie"
                  mediaId={movie.id}
                  mediaTitle={movie.title}
                />
              </div>

              {/* Overview/Plot */}
              {(movie.plot || movie.overview) && (
                <div className="mb-6">
                  <h2 className="text-2xl font-bold mb-3">Synopsis</h2>
                  <p className="text-gray-300 text-lg leading-relaxed">
                    {movie.plot || movie.overview}
                  </p>
                </div>
              )}

              {/* Crew Info */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {movie.director && (
                  <div>
                    <p className="text-sm text-gray-400 mb-1">Réalisateur</p>
                    <p className="font-semibold">{movie.director}</p>
                  </div>
                )}
                {movie.actors && (
                  <div className="md:col-span-2">
                    <p className="text-sm text-gray-400 mb-1">Acteurs principaux</p>
                    <p className="font-semibold">{movie.actors.split(',').slice(0, 3).join(', ')}</p>
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
            {movie.actors && (
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span>🎭</span> Distribution
                </h3>
                <div className="space-y-2">
                  {movie.actors.split(',').slice(0, 5).map((actor, i) => (
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
                {movie.country && (
                  <div>
                    <dt className="text-sm text-gray-400">Pays</dt>
                    <dd className="text-gray-200">{movie.country}</dd>
                  </div>
                )}
                {movie.language && (
                  <div>
                    <dt className="text-sm text-gray-400">Langue</dt>
                    <dd className="text-gray-200">{movie.language}</dd>
                  </div>
                )}
                {movie.box_office && (
                  <div>
                    <dt className="text-sm text-gray-400">Box Office</dt>
                    <dd className="text-gray-200">{movie.box_office}</dd>
                  </div>
                )}
                {movie.production && (
                  <div>
                    <dt className="text-sm text-gray-400">Production</dt>
                    <dd className="text-gray-200">{movie.production}</dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Awards */}
            {movie.awards && (
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span>🏆</span> Récompenses
                </h3>
                <p className="text-gray-300">{movie.awards}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
