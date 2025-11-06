'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';

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
  created_at?: string;
}

export default function MovieDetailPage() {
  const params = useParams();
  const router = useRouter();
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

  if (error || !movie) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
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
  const rating = movie.imdb_rating || movie.rating;

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
      {movie.backdrop_path && (
        <div
          className="h-96 bg-cover bg-center relative"
          style={{
            backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.9)), url(${movie.backdrop_path})`,
          }}
        >
          <div className="absolute bottom-0 left-0 right-0 p-8">
            <div className="container mx-auto">
              <h1 className="text-5xl font-bold mb-2">{movie.title}</h1>
              {movie.original_title && movie.original_title !== movie.title && (
                <p className="text-gray-300 text-xl mb-2">({movie.original_title})</p>
              )}
              <div className="flex items-center gap-4 text-lg">
                {movie.year && <span className="text-gray-300">{movie.year}</span>}
                {movie.runtime && <span className="text-gray-300">• {movie.runtime} min</span>}
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
              alt={movie.title}
              className="w-full rounded-lg shadow-2xl"
            />

            {/* IMDb Link */}
            {movie.imdb_id && (
              <a
                href={`https://www.imdb.com/title/${movie.imdb_id}`}
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
            {movie.genre && (
              <div className="mb-6">
                <div className="flex flex-wrap gap-2">
                  {movie.genre.split(',').map((g, i) => (
                    <span
                      key={i}
                      className="bg-blue-600 px-3 py-1 rounded-full text-sm"
                    >
                      {g.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Plot/Overview */}
            {(movie.plot || movie.overview) && (
              <div className="mb-6">
                <h2 className="text-2xl font-bold mb-3">Synopsis</h2>
                <p className="text-gray-300 text-lg leading-relaxed">
                  {movie.plot || movie.overview}
                </p>
              </div>
            )}

            {/* Additional Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              {movie.director && (
                <div>
                  <h3 className="text-gray-400 text-sm mb-1">Réalisateur</h3>
                  <p className="text-white">{movie.director}</p>
                </div>
              )}

              {movie.actors && (
                <div>
                  <h3 className="text-gray-400 text-sm mb-1">Acteurs</h3>
                  <p className="text-white">{movie.actors}</p>
                </div>
              )}

              {movie.released && (
                <div>
                  <h3 className="text-gray-400 text-sm mb-1">Date de sortie</h3>
                  <p className="text-white">{movie.released}</p>
                </div>
              )}

              {movie.country && (
                <div>
                  <h3 className="text-gray-400 text-sm mb-1">Pays</h3>
                  <p className="text-white">{movie.country}</p>
                </div>
              )}

              {movie.language && (
                <div>
                  <h3 className="text-gray-400 text-sm mb-1">Langue</h3>
                  <p className="text-white">{movie.language}</p>
                </div>
              )}

              {movie.box_office && (
                <div>
                  <h3 className="text-gray-400 text-sm mb-1">Box Office</h3>
                  <p className="text-white">{movie.box_office}</p>
                </div>
              )}

              {movie.production && (
                <div>
                  <h3 className="text-gray-400 text-sm mb-1">Production</h3>
                  <p className="text-white">{movie.production}</p>
                </div>
              )}

              {movie.awards && (
                <div className="md:col-span-2">
                  <h3 className="text-gray-400 text-sm mb-1">Récompenses</h3>
                  <p className="text-white">{movie.awards}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
