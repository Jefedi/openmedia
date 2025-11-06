import { NextResponse } from 'next/server';

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const apiHost = process.env.API_HOST || 'api';
    const apiPort = process.env.API_PORT || '8000';

    const response = await fetch(
      `http://${apiHost}:${apiPort}/api/v1/series/${params.id}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      }
    );

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Series not found' },
          { status: 404 }
        );
      }
      throw new Error(`API responded with status ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Series detail API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch series details' },
      { status: 500 }
    );
  }
}
