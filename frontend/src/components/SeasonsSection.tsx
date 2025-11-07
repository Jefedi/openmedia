'use client';

import { useState } from 'react';

interface Episode {
  id: number;
  name: string;
  episode_number: number;
  season_number: number;
  overview?: string;
  air_date?: string;
  still_path?: string;
  runtime?: number;
  vote_average?: number;
}

interface Season {
  id: number;
  name: string;
  season_number: number;
  episode_count: number;
  overview?: string;
  air_date?: string;
  poster_path?: string;
  episodes?: Episode[];
}

interface SeasonsSectionProps {
  seasons: Season[];
  seriesId: number;
}

export default function SeasonsSection({ seasons, seriesId }: SeasonsSectionProps) {
  const [selectedSeason, setSelectedSeason] = useState<number | null>(null);
  const [loadingEpisodes, setLoadingEpisodes] = useState(false);
  const [episodes, setEpisodes] = useState<Episode[]>([]);

  if (!seasons || seasons.length === 0) return null;

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:18000';

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Date inconnue';
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const loadEpisodes = async (seasonNumber: number) => {
    if (selectedSeason === seasonNumber) {
      setSelectedSeason(null);
      setEpisodes([]);
      return;
    }

    setSelectedSeason(seasonNumber);
    setLoadingEpisodes(true);

    try {
      const response = await fetch(`/api/series/${seriesId}/seasons/${seasonNumber}/episodes`);
      if (response.ok) {
        const data = await response.json();
        setEpisodes(data || []);
      } else {
        setEpisodes([]);
      }
    } catch (error) {
      console.error('Error loading episodes:', error);
      setEpisodes([]);
    } finally {
      setLoadingEpisodes(false);
    }
  };

  // Filtrer la saison 0 (Specials) si elle n'a pas d'épisodes
  const displaySeasons = seasons.filter(s => s.season_number > 0 || s.episode_count > 0);

  return (
    <div className="bg-gray-800/50 rounded-lg p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">Saisons</h2>

      <div className="space-y-4">
        {displaySeasons.map((season) => (
          <div key={season.id} className="border border-gray-700 rounded-lg overflow-hidden">
            {/* Season Header */}
            <button
              onClick={() => loadEpisodes(season.season_number)}
              className="w-full flex items-center gap-4 p-4 hover:bg-gray-700/50 transition cursor-pointer"
            >
              {/* Season Poster */}
              <div className="w-24 h-36 flex-shrink-0 rounded-lg overflow-hidden bg-gray-700">
                {season.poster_path ? (
                  <img
                    src={season.poster_path.startsWith('http') ? season.poster_path : `https://image.tmdb.org/t/p/w185${season.poster_path}`}
                    alt={season.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const img = e.target as HTMLImageElement;
                      img.src = '/images/no-poster.png';
                    }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-500">
                    <span className="text-3xl">S{season.season_number}</span>
                  </div>
                )}
              </div>

              {/* Season Info */}
              <div className="flex-1 text-left">
                <h3 className="text-xl font-bold mb-1">{season.name}</h3>
                <div className="text-sm text-gray-400 mb-2">
                  {season.episode_count} épisode{season.episode_count > 1 ? 's' : ''}
                  {season.air_date && ` • ${formatDate(season.air_date)}`}
                </div>
                {season.overview && (
                  <p className="text-sm text-gray-300 line-clamp-2">{season.overview}</p>
                )}
              </div>

              {/* Expand Icon */}
              <div className="flex-shrink-0">
                <svg
                  className={`w-6 h-6 transition-transform ${selectedSeason === season.season_number ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>

            {/* Episodes List */}
            {selectedSeason === season.season_number && (
              <div className="border-t border-gray-700 bg-gray-900/30">
                {loadingEpisodes ? (
                  <div className="p-8 text-center">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                    <p className="mt-2 text-gray-400">Chargement des épisodes...</p>
                  </div>
                ) : episodes.length > 0 ? (
                  <div className="divide-y divide-gray-700">
                    {episodes.map((episode) => (
                      <div key={episode.id} className="p-4 hover:bg-gray-700/30 transition">
                        <div className="flex gap-4">
                          {/* Episode Still */}
                          <div className="w-40 h-24 flex-shrink-0 rounded-lg overflow-hidden bg-gray-700">
                            {episode.still_path ? (
                              <img
                                src={episode.still_path.startsWith('http') ? episode.still_path : `https://image.tmdb.org/t/p/w300${episode.still_path}`}
                                alt={episode.name}
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                  const img = e.target as HTMLImageElement;
                                  img.src = '/images/no-image.png';
                                }}
                              />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center text-gray-500">
                                <span className="text-xs">Ep {episode.episode_number}</span>
                              </div>
                            )}
                          </div>

                          {/* Episode Info */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-2 mb-1">
                              <h4 className="font-semibold">
                                {episode.episode_number}. {episode.name}
                              </h4>
                              {episode.runtime && (
                                <span className="text-sm text-gray-400 whitespace-nowrap">
                                  {episode.runtime}min
                                </span>
                              )}
                            </div>

                            {episode.air_date && (
                              <div className="text-xs text-gray-400 mb-2">
                                {formatDate(episode.air_date)}
                              </div>
                            )}

                            {episode.overview && (
                              <p className="text-sm text-gray-300 line-clamp-2">
                                {episode.overview}
                              </p>
                            )}

                            {episode.vote_average && episode.vote_average > 0 && (
                              <div className="flex items-center gap-1 mt-2">
                                <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                </svg>
                                <span className="text-sm text-gray-400">
                                  {episode.vote_average.toFixed(1)}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center text-gray-400">
                    Aucun épisode disponible pour cette saison.
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
