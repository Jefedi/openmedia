'use client';

interface RatingSectionProps {
  tmdbRating?: number;
  tmdbVotes?: number;
  imdbRating?: string;
  imdbId?: string;
}

export default function RatingSection({ tmdbRating, tmdbVotes, imdbRating, imdbId }: RatingSectionProps) {
  const tmdbScore = tmdbRating ? Math.round(tmdbRating * 10) : null;
  const imdbScore = imdbRating ? parseFloat(imdbRating) : null;

  if (!tmdbScore && !imdbScore) return null;

  return (
    <div className="bg-gray-800/50 rounded-lg p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">Avis des spectateurs</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        {/* TMDB Rating */}
        {tmdbScore && (
          <div className="flex items-center gap-4">
            <div className="relative w-20 h-20 flex-shrink-0">
              {/* Circle background */}
              <svg className="transform -rotate-90 w-20 h-20">
                <circle
                  cx="40"
                  cy="40"
                  r="36"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                  className="text-gray-700"
                />
                <circle
                  cx="40"
                  cy="40"
                  r="36"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 36}`}
                  strokeDashoffset={`${2 * Math.PI * 36 * (1 - tmdbScore / 100)}`}
                  className={
                    tmdbScore >= 70 ? 'text-green-500' :
                    tmdbScore >= 50 ? 'text-yellow-500' :
                    'text-red-500'
                  }
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-bold">{tmdbScore}%</span>
              </div>
            </div>
            <div>
              <div className="font-bold text-lg">TMDB</div>
              {tmdbVotes && (
                <div className="text-sm text-gray-400">
                  {tmdbVotes.toLocaleString()} votes
                </div>
              )}
            </div>
          </div>
        )}

        {/* IMDb Rating */}
        {imdbScore && (
          <div className="flex items-center gap-4">
            <div className="bg-yellow-500 text-black rounded-lg w-20 h-20 flex items-center justify-center flex-col flex-shrink-0">
              <div className="text-2xl font-bold">{imdbScore.toFixed(1)}</div>
              <div className="text-xs font-semibold">/ 10</div>
            </div>
            <div>
              <div className="font-bold text-lg">IMDb</div>
              {imdbId && (
                <a
                  href={`https://www.imdb.com/title/${imdbId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-400 hover:text-blue-300 transition"
                >
                  Voir sur IMDb →
                </a>
              )}
            </div>
          </div>
        )}

        {/* Note moyenne calculée */}
        {tmdbScore && imdbScore && (
          <div className="flex items-center gap-4">
            <div className="bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg w-20 h-20 flex items-center justify-center flex-col flex-shrink-0">
              <div className="text-2xl font-bold">
                {((tmdbScore / 10 + imdbScore) / 2).toFixed(1)}
              </div>
              <div className="text-xs font-semibold">/ 10</div>
            </div>
            <div>
              <div className="font-bold text-lg">Moyenne</div>
              <div className="text-sm text-gray-400">TMDB + IMDb</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
