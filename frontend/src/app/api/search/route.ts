import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const q = searchParams.get('q');

    if (!q) {
      return NextResponse.json(
        { error: 'Query parameter "q" is required' },
        { status: 400 }
      );
    }

    const apiHost = process.env.API_HOST || 'api';
    const apiPort = process.env.API_PORT || '8000';

    const response = await fetch(
      `http://${apiHost}:${apiPort}/api/v1/search?q=${encodeURIComponent(q)}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store', // Always get fresh results
      }
    );

    if (!response.ok) {
      return NextResponse.json(
        {
          query: q,
          movies: [],
          series: [],
          from_cache: false,
          from_omdb: false,
          error: 'Search failed'
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Search API error:', error);
    return NextResponse.json(
      {
        query: '',
        movies: [],
        series: [],
        from_cache: false,
        from_omdb: false,
        error: 'Failed to perform search'
      },
      { status: 500 }
    );
  }
}
