import Link from 'next/link';
import Image from 'next/image';

interface MediaCardProps {
  id: number;
  title: string;
  year?: number;
  posterPath?: string;
  voteAverage?: number;
  type: 'movie' | 'series';
  overview?: string;
}

export default function MediaCard({
  id,
  title,
  year,
  posterPath,
  voteAverage,
  type,
  overview
}: MediaCardProps) {
  const href = type === 'movie' ? `/movies/${id}` : `/series/${id}`;
  const placeholderImage = '/placeholder-poster.jpg';

  return (
    <Link href={href}>
      <div className="group relative bg-gray-800 rounded-lg overflow-hidden hover:ring-2 hover:ring-blue-500 transition-all duration-300 cursor-pointer">
        {/* Poster */}
        <div className="relative aspect-[2/3] bg-gray-700">
          {posterPath ? (
            <Image
              src={posterPath}
              alt={title}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-300"
              sizes="(max-width: 768px) 50vw, (max-width: 1200px) 33vw, 25vw"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-500">
              <svg
                className="w-16 h-16"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"
                />
              </svg>
            </div>
          )}

          {/* Rating Badge */}
          {voteAverage && voteAverage > 0 && (
            <div className="absolute top-2 right-2 bg-black/80 backdrop-blur-sm px-2 py-1 rounded-full">
              <div className="flex items-center gap-1">
                <svg
                  className="w-4 h-4 text-yellow-400"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <span className="text-sm font-semibold text-white">
                  {voteAverage.toFixed(1)}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="p-3">
          <h3 className="font-semibold text-white line-clamp-2 mb-1 group-hover:text-blue-400 transition-colors">
            {title}
          </h3>

          <div className="flex items-center gap-2 text-sm text-gray-400">
            {year && <span>{year}</span>}
            {year && type && <span>"</span>}
            {type && (
              <span className="capitalize">
                {type === 'series' ? 'Série' : 'Film'}
              </span>
            )}
          </div>

          {overview && (
            <p className="text-sm text-gray-400 mt-2 line-clamp-2">
              {overview}
            </p>
          )}
        </div>
      </div>
    </Link>
  );
}
