interface Genre {
  id: number;
  name: string;
  slug: string;
}

interface GenreListProps {
  genres: Genre[];
}

export default function GenreList({ genres }: GenreListProps) {
  if (!genres || genres.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {genres.map((genre) => (
        <span
          key={genre.id}
          className="px-3 py-1 bg-gray-700/50 border border-gray-600 rounded-full text-sm font-medium"
        >
          {genre.name}
        </span>
      ))}
    </div>
  );
}
