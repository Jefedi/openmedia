'use client';

interface Platform {
  name: string;
  logo?: string;
  type: 'streaming' | 'rent' | 'buy';
  url?: string;
}

interface StreamingPlatformsProps {
  platforms?: Platform[];
}

export default function StreamingPlatforms({ platforms }: StreamingPlatformsProps) {
  if (!platforms || platforms.length === 0) return null;

  const getPlatformBadgeColor = (type: string) => {
    switch (type) {
      case 'streaming':
        return 'bg-green-600/20 text-green-400 border-green-600/50';
      case 'rent':
        return 'bg-blue-600/20 text-blue-400 border-blue-600/50';
      case 'buy':
        return 'bg-purple-600/20 text-purple-400 border-purple-600/50';
      default:
        return 'bg-gray-600/20 text-gray-400 border-gray-600/50';
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'streaming':
        return 'Streaming';
      case 'rent':
        return 'Location';
      case 'buy':
        return 'Achat';
      default:
        return type;
    }
  };

  // Group platforms by type
  const groupedPlatforms = platforms.reduce((acc, platform) => {
    if (!acc[platform.type]) {
      acc[platform.type] = [];
    }
    acc[platform.type].push(platform);
    return acc;
  }, {} as Record<string, Platform[]>);

  return (
    <div className="bg-gray-800/50 rounded-lg p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">Où regarder</h2>

      {Object.entries(groupedPlatforms).map(([type, platformList]) => (
        <div key={type} className="mb-4 last:mb-0">
          <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold mb-3 border ${getPlatformBadgeColor(type)}`}>
            {getTypeLabel(type)}
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {platformList.map((platform, index) => (
              <a
                key={`${platform.name}-${index}`}
                href={platform.url || '#'}
                target={platform.url ? '_blank' : undefined}
                rel={platform.url ? 'noopener noreferrer' : undefined}
                className={`group relative bg-gray-700 hover:bg-gray-600 rounded-xl p-4 transition ${
                  platform.url ? 'cursor-pointer' : 'cursor-default'
                }`}
              >
                {/* Logo placeholder or actual logo */}
                {platform.logo ? (
                  <div className="aspect-square rounded-lg overflow-hidden mb-2 bg-white/10 flex items-center justify-center">
                    <img
                      src={platform.logo}
                      alt={platform.name}
                      className="w-full h-full object-contain"
                    />
                  </div>
                ) : (
                  <div className="aspect-square rounded-lg overflow-hidden mb-2 bg-gradient-to-br from-blue-600/30 to-purple-600/30 flex items-center justify-center">
                    <span className="text-2xl font-bold text-white/50">
                      {platform.name.charAt(0)}
                    </span>
                  </div>
                )}

                {/* Platform name */}
                <div className="text-sm font-semibold text-center truncate">
                  {platform.name}
                </div>

                {/* Hover effect */}
                {platform.url && (
                  <div className="absolute inset-0 bg-blue-600/0 group-hover:bg-blue-600/10 rounded-xl transition pointer-events-none" />
                )}
              </a>
            ))}
          </div>
        </div>
      ))}

      <div className="mt-4 text-sm text-gray-400">
        <p>
          💡 Les disponibilités peuvent varier selon votre région.
          Les liens vous redirigent vers les plateformes officielles.
        </p>
      </div>
    </div>
  );
}
