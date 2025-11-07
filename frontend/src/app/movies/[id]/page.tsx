'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import LibraryActions from '@/components/LibraryActions';
import GenreList from '@/components/GenreList';
import CastList from '@/components/CastList';
import RatingSection from '@/components/RatingSection';
import DetailSection from '@/components/DetailSection';
import StreamingPlatforms from '@/components/StreamingPlatforms';
import SupplementsSection from '@/components/SupplementsSection';

interface Genre {
  id: number;
  name: string;
  slug: string;
}

interface Person {
  id: number;
  name: string;
  profile_path?: string;
}

interface CastMember {
  character?: string;
  order: number;
  person: Person;
}

interface Platform {
  name: string;
  logo?: string;
  type: 'streaming' | 'rent' | 'buy';
  url?: string;
}

interface Video {
  key: string;
  name: string;
  type: 'Trailer' | 'Teaser' | 'Clip' | 'Behind the Scenes' | 'Featurette';
  site: 'YouTube' | 'Vimeo';
}

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
  genres?: Genre[];
  cast?: CastMember[];
  // New fields for components
  status?: string;
  original_language?: string;
  production_companies?: string[];
  platforms?: Platform[];
  videos?: Video[];
  creators?: string[];
  writers?: string[];
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
        console.log('Fetching movie with ID:', params.id);
        const response = await fetch(`/api/movies/${params.id}`);
        console.log('Movie API response status:', response.status);

        if (!response.ok) {
          const errorText = await response.text();
          console.error('Movie API error response:', errorText);
          if (response.status === 404) {
            setError('Film non trouvé');
          } else {
            setError('Erreur lors du chargement du film');
          }
          return;
        }

        const data = await response.json();
        console.log('Movie data received:', data);
        setMovie(data);
      } catch (err) {
        console.error('Error fetching movie:', err);
        console.error('Error details:', err instanceof Error ? err.message : String(err));
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

              {/* Genres */}
              {movie.genres && movie.genres.length > 0 && (
                <GenreList genres={movie.genres} />
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
              {movie.director && (
                <div className="mb-4">
                  <p className="text-sm text-gray-400 mb-1">Réalisateur</p>
                  <p className="font-semibold text-lg">{movie.director}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Additional Information */}
      <div className="bg-gray-800/50 border-t border-gray-700">
        <div className="container mx-auto px-4 py-8">
          {/* Ratings Section */}
          <RatingSection
            tmdbRating={movie.vote_average}
            tmdbVotes={movie.vote_count}
            imdbRating={movie.imdb_rating?.toString()}
            imdbId={movie.imdb_id}
          />

          {/* Detail Section */}
          <DetailSection
            releaseDate={movie.released}
            runtime={movie.runtime}
            status={movie.status}
            creators={movie.creators}
            writers={movie.writers}
            originalLanguage={movie.original_language}
            productionCompanies={movie.production_companies}
            genres={movie.genres}
          />

          {/* Streaming Platforms */}
          <StreamingPlatforms platforms={movie.platforms} />

          {/* Cast List */}
          {movie.cast && movie.cast.length > 0 && (
            <CastList cast={movie.cast} limit={10} />
          )}

          {/* Supplemental Videos */}
          <SupplementsSection videos={movie.videos} />

          {/* Legacy Awards Section */}
          {movie.awards && (
            <div className="bg-gray-800/50 rounded-lg p-6 mb-6">
              <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <span>🏆</span> Récompenses
              </h3>
              <p className="text-gray-300">{movie.awards}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
