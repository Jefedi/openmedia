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
import SeasonsSection from '@/components/SeasonsSection';

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

interface Season {
  id: number;
  name: string;
  season_number: number;
  episode_count: number;
  overview?: string;
  air_date?: string;
  poster_path?: string;
}

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
  genres?: Genre[];
  // New fields for components
  status?: string;
  original_language?: string;
  production_companies?: string[];
  platforms?: Platform[];
  videos?: Video[];
  creators?: string[];
  writers?: string[];
  cast?: CastMember[];
  seasons?: Season[];
  first_air_date?: string;
  last_air_date?: string;
  episode_runtime?: number[];
  number_of_seasons?: number;
  number_of_episodes?: number;
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
        console.log('Fetching series with ID:', params.id);
        const response = await fetch(`/api/series/${params.id}`);
        console.log('Series API response status:', response.status);

        if (!response.ok) {
          const errorText = await response.text();
          console.error('Series API error response:', errorText);
          if (response.status === 404) {
            setError('Série non trouvée');
          } else {
            setError('Erreur lors du chargement de la série');
          }
          return;
        }

        const data = await response.json();
        console.log('Series data received:', data);
        setSeries(data);
      } catch (err) {
        console.error('Error fetching series:', err);
        console.error('Error details:', err instanceof Error ? err.message : String(err));
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
            <img src={backdropUrl} alt={series?.name || ""} className="object-cover opacity-30" />
            <div className="absolute inset-0 bg-gradient-to-r from-gray-900 via-gray-900/95 to-gray-900/80"></div>
          </div>
        )}

        {/* Content */}
        <div className="relative container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-[300px,1fr] gap-8">
            {/* Poster */}
            <div className="flex flex-col items-center md:items-start">
              <div className="relative w-full max-w-[300px] aspect-[2/3] rounded-lg overflow-hidden shadow-2xl">
                <img src={posterUrl} alt={series?.name || ""} className="w-full h-full object-cover" />
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

              {/* Genres */}
              {series.genres && series.genres.length > 0 && (
                <GenreList genres={series.genres} />
              )}


              {/* Library Actions */}
              <div className="mb-6">
                <LibraryActions
                  mediaType="series"
                  mediaId={series.id}
                  mediaTitle={series.name}
                />
              </div>

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
              {series.director && (
                <div className="mb-4">
                  <p className="text-sm text-gray-400 mb-1">Créateur</p>
                  <p className="font-semibold text-lg">{series.director}</p>
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
            tmdbRating={series.vote_average}
            tmdbVotes={series.vote_count}
            imdbRating={series.imdb_rating?.toString()}
            imdbId={series.imdb_id}
          />

          {/* Detail Section */}
          <DetailSection
            firstAirDate={series.first_air_date || series.released}
            lastAirDate={series.last_air_date}
            episodeRuntime={series.episode_runtime}
            status={series.status}
            creators={series.creators}
            writers={series.writers}
            originalLanguage={series.original_language}
            productionCompanies={series.production_companies}
            genres={series.genres}
            numberOfSeasons={series.number_of_seasons || series.total_seasons}
            numberOfEpisodes={series.number_of_episodes}
          />

          {/* Streaming Platforms */}
          <StreamingPlatforms platforms={series.platforms} />

          {/* Seasons Section */}
          {series.seasons && series.seasons.length > 0 && (
            <SeasonsSection seasons={series.seasons} seriesId={series.id} />
          )}

          {/* Cast List */}
          {series.cast && series.cast.length > 0 && (
            <CastList cast={series.cast} limit={10} />
          )}

          {/* Supplemental Videos */}
          <SupplementsSection videos={series.videos} />

          {/* Legacy Awards Section */}
          {series.awards && (
            <div className="bg-gray-800/50 rounded-lg p-6 mb-6">
              <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <span>🏆</span> Récompenses
              </h3>
              <p className="text-gray-300">{series.awards}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
