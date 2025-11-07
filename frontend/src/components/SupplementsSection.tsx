'use client';

interface Video {
  key: string; // YouTube video ID
  name: string;
  type: 'Trailer' | 'Teaser' | 'Clip' | 'Behind the Scenes' | 'Featurette';
  site: 'YouTube' | 'Vimeo';
}

interface SupplementsSectionProps {
  videos?: Video[];
}

export default function SupplementsSection({ videos }: SupplementsSectionProps) {
  if (!videos || videos.length === 0) return null;

  const getVideoTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      'Trailer': 'Bande-annonce',
      'Teaser': 'Teaser',
      'Clip': 'Extrait',
      'Behind the Scenes': 'Coulisses',
      'Featurette': 'Featurette',
    };
    return labels[type] || type;
  };

  const getVideoTypeColor = (type: string) => {
    switch (type) {
      case 'Trailer':
        return 'bg-red-600/20 text-red-400 border-red-600/50';
      case 'Teaser':
        return 'bg-orange-600/20 text-orange-400 border-orange-600/50';
      case 'Behind the Scenes':
        return 'bg-purple-600/20 text-purple-400 border-purple-600/50';
      default:
        return 'bg-blue-600/20 text-blue-400 border-blue-600/50';
    }
  };

  // Prioriser les trailers
  const sortedVideos = [...videos].sort((a, b) => {
    const priority = { 'Trailer': 0, 'Teaser': 1, 'Clip': 2, 'Behind the Scenes': 3, 'Featurette': 4 };
    return (priority[a.type] || 99) - (priority[b.type] || 99);
  });

  return (
    <div className="bg-gray-800/50 rounded-lg p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">Suppléments</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sortedVideos.map((video, index) => (
          <div key={`${video.key}-${index}`} className="group">
            <div className="relative aspect-video rounded-lg overflow-hidden bg-gray-900 mb-2">
              {video.site === 'YouTube' ? (
                <iframe
                  src={`https://www.youtube.com/embed/${video.key}`}
                  title={video.name}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  className="absolute inset-0 w-full h-full"
                />
              ) : (
                <div className="absolute inset-0 flex items-center justify-center">
                  <a
                    href={`https://www.youtube.com/watch?v=${video.key}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-white hover:text-red-500 transition"
                  >
                    <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M10 16.5l6-4.5-6-4.5v9zM12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                    </svg>
                  </a>
                  <img
                    src={`https://img.youtube.com/vi/${video.key}/hqdefault.jpg`}
                    alt={video.name}
                    className="absolute inset-0 w-full h-full object-cover -z-10"
                  />
                </div>
              )}
            </div>

            <div className="flex items-start gap-2">
              <span className={`px-2 py-1 rounded text-xs font-semibold border whitespace-nowrap ${getVideoTypeColor(video.type)}`}>
                {getVideoTypeLabel(video.type)}
              </span>
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-sm truncate" title={video.name}>
                  {video.name}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
