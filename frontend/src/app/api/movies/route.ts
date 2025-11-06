import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const apiHost = process.env.API_HOST || 'api';
    const apiPort = process.env.API_PORT || '8000';

    const response = await fetch(
      `http://${apiHost}:${apiPort}/api/v1/movies?page=1&page_size=20&sort_by=created_at&order=desc`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store', // Toujours récupérer les données fraîches
      }
    );

    if (!response.ok) {
      return NextResponse.json(
        { movies: [], total: 0, page: 1, page_size: 20 },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Movies API error:', error);
    return NextResponse.json(
      { movies: [], total: 0, page: 1, page_size: 20, error: 'Failed to fetch movies' },
      { status: 500 }
    );
  }
}
