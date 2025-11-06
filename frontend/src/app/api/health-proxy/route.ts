import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Appeler l'API backend depuis le serveur Next.js
    // Dans Docker, "api" est le nom du service
    const apiHost = process.env.API_HOST || 'api';
    const apiPort = process.env.API_PORT || '8000';

    const response = await fetch(`http://${apiHost}:${apiPort}/health`, {
      cache: 'no-store',
    });

    const data = await response.json();

    return NextResponse.json(data);
  } catch (error) {
    console.error('Health check failed:', error);
    return NextResponse.json(
      { status: 'offline', error: 'Unable to reach API' },
      { status: 503 }
    );
  }
}
