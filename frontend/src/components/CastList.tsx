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

interface CastListProps {
  cast: CastMember[];
  limit?: number;
}

export default function CastList({ cast, limit = 10 }: CastListProps) {
  if (!cast || cast.length === 0) return null;

  const displayCast = limit ? cast.slice(0, limit) : cast;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:18000';

  // Fonction pour construire l'URL de l'image TMDB
  const getProfileImageUrl = (profilePath?: string) => {
    if (!profilePath) return '/images/no-profile.png';

    // Si c'est déjà une URL complète TMDB
    if (profilePath.startsWith('http')) return profilePath;

    // Si c'est un chemin TMDB (commence par /)
    if (profilePath.startsWith('/')) {
      return `https://image.tmdb.org/t/p/w185${profilePath}`;
    }

    // Sinon, utiliser notre API
    return `${apiUrl}${profilePath}`;
  };

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4">Distribution</h2>
      <div className="overflow-x-auto pb-2 cast-scroll-container">
        <div className="flex gap-4 min-w-min">
          {displayCast.map((member) => (
            <div key={`${member.person.id}-${member.order}`} className="flex flex-col items-center flex-shrink-0" style={{ width: '150px' }}>
              <div className="relative w-full aspect-[2/3] rounded-lg overflow-hidden bg-gray-800 mb-2">
                <img
                  src={getProfileImageUrl(member.person.profile_path)}
                  alt={member.person.name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    const img = e.target as HTMLImageElement;
                    img.src = '/images/no-profile.png';
                  }}
                />
              </div>
              <div className="text-center w-full">
                <p className="font-semibold text-sm truncate" title={member.person.name}>
                  {member.person.name}
                </p>
                {member.character && (
                  <p className="text-xs text-gray-400 truncate" title={member.character}>
                    {member.character}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
      {cast.length > limit && (
        <p className="text-sm text-gray-400 mt-4 text-center">
          +{cast.length - limit} autres acteurs
        </p>
      )}
      <style dangerouslySetInnerHTML={{
        __html: `
          .cast-scroll-container {
            scrollbar-width: thin;
            scrollbar-color: #4B5563 #1F2937;
          }
          .cast-scroll-container::-webkit-scrollbar {
            height: 8px;
          }
          .cast-scroll-container::-webkit-scrollbar-track {
            background: #1F2937;
            border-radius: 4px;
          }
          .cast-scroll-container::-webkit-scrollbar-thumb {
            background: #4B5563;
            border-radius: 4px;
          }
          .cast-scroll-container::-webkit-scrollbar-thumb:hover {
            background: #6B7280;
          }
        `
      }} />
    </div>
  );
}
