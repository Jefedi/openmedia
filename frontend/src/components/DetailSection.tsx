interface DetailSectionProps {
  releaseDate?: string;
  firstAirDate?: string;
  lastAirDate?: string;
  runtime?: number;
  episodeRuntime?: number[];
  status?: string;
  creators?: string[];
  writers?: string[];
  originalLanguage?: string;
  productionCompanies?: string[];
  genres?: { id: number; name: string }[];
  numberOfSeasons?: number;
  numberOfEpisodes?: number;
}

export default function DetailSection({
  releaseDate,
  firstAirDate,
  lastAirDate,
  runtime,
  episodeRuntime,
  status,
  creators,
  writers,
  originalLanguage,
  productionCompanies,
  genres,
  numberOfSeasons,
  numberOfEpisodes,
}: DetailSectionProps) {

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const formatRuntime = (minutes?: number) => {
    if (!minutes) return null;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins > 0 ? mins + 'min' : ''}`;
    }
    return `${mins}min`;
  };

  const getStatusLabel = (status?: string) => {
    const statusMap: { [key: string]: string } = {
      'released': 'Sorti',
      'post_production': 'Post-production',
      'in_production': 'En production',
      'planned': 'Planifié',
      'canceled': 'Annulé',
      'returning': 'En cours',
      'ended': 'Terminée',
    };
    return status ? statusMap[status.toLowerCase()] || status : null;
  };

  const getLanguageName = (code?: string) => {
    const languages: { [key: string]: string } = {
      'en': 'Anglais',
      'fr': 'Français',
      'es': 'Espagnol',
      'de': 'Allemand',
      'it': 'Italien',
      'ja': 'Japonais',
      'ko': 'Coréen',
      'zh': 'Chinois',
      'pt': 'Portugais',
      'ru': 'Russe',
    };
    return code ? languages[code] || code.toUpperCase() : null;
  };

  return (
    <div className="bg-gray-800/50 rounded-lg p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">Détails</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

        {/* Date de sortie */}
        {(releaseDate || firstAirDate) && (
          <div>
            <div className="text-sm text-gray-400 mb-1">Date de sortie</div>
            <div className="font-semibold">{formatDate(releaseDate || firstAirDate)}</div>
          </div>
        )}

        {/* Dernière diffusion (séries) */}
        {lastAirDate && (
          <div>
            <div className="text-sm text-gray-400 mb-1">Dernière diffusion</div>
            <div className="font-semibold">{formatDate(lastAirDate)}</div>
          </div>
        )}

        {/* Durée */}
        {runtime && (
          <div>
            <div className="text-sm text-gray-400 mb-1">Durée</div>
            <div className="font-semibold">{formatRuntime(runtime)}</div>
          </div>
        )}

        {/* Durée moyenne des épisodes */}
        {episodeRuntime && episodeRuntime.length > 0 && (
          <div>
            <div className="text-sm text-gray-400 mb-1">Durée moyenne</div>
            <div className="font-semibold">
              {formatRuntime(episodeRuntime[0])} / épisode
            </div>
          </div>
        )}

        {/* Nombre de saisons/épisodes */}
        {numberOfSeasons !== undefined && (
          <div>
            <div className="text-sm text-gray-400 mb-1">Saisons / Épisodes</div>
            <div className="font-semibold">
              {numberOfSeasons} {numberOfSeasons > 1 ? 'saisons' : 'saison'}
              {numberOfEpisodes && ` / ${numberOfEpisodes} épisodes`}
            </div>
          </div>
        )}

        {/* Statut */}
        {status && (
          <div>
            <div className="text-sm text-gray-400 mb-1">Statut</div>
            <div className="font-semibold">
              <span className={`px-2 py-1 rounded-full text-sm ${
                status === 'released' || status === 'ended' ? 'bg-green-600/30 text-green-400' :
                status === 'in_production' || status === 'returning' ? 'bg-blue-600/30 text-blue-400' :
                status === 'canceled' ? 'bg-red-600/30 text-red-400' :
                'bg-gray-600/30 text-gray-400'
              }`}>
                {getStatusLabel(status)}
              </span>
            </div>
          </div>
        )}

        {/* Créateurs */}
        {creators && creators.length > 0 && (
          <div>
            <div className="text-sm text-gray-400 mb-1">
              {creators.length > 1 ? 'Créateurs' : 'Créateur'}
            </div>
            <div className="font-semibold">{creators.join(', ')}</div>
          </div>
        )}

        {/* Scénaristes */}
        {writers && writers.length > 0 && (
          <div>
            <div className="text-sm text-gray-400 mb-1">
              {writers.length > 1 ? 'Scénaristes' : 'Scénariste'}
            </div>
            <div className="font-semibold">{writers.slice(0, 2).join(', ')}</div>
          </div>
        )}

        {/* Langue originale */}
        {originalLanguage && (
          <div>
            <div className="text-sm text-gray-400 mb-1">Langue originale</div>
            <div className="font-semibold">{getLanguageName(originalLanguage)}</div>
          </div>
        )}

        {/* Studios */}
        {productionCompanies && productionCompanies.length > 0 && (
          <div className="md:col-span-2">
            <div className="text-sm text-gray-400 mb-1">
              {productionCompanies.length > 1 ? 'Studios' : 'Studio'}
            </div>
            <div className="font-semibold">{productionCompanies.join(', ')}</div>
          </div>
        )}

        {/* Genres */}
        {genres && genres.length > 0 && (
          <div className="md:col-span-2">
            <div className="text-sm text-gray-400 mb-1">Genres</div>
            <div className="font-semibold">{genres.map(g => g.name).join(', ')}</div>
          </div>
        )}
      </div>
    </div>
  );
}
