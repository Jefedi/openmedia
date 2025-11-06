import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization');
    if (!authHeader) {
      return NextResponse.json({ detail: 'No authorization header' }, { status: 401 });
    }

    const apiHost = process.env.API_HOST || 'api';
    const apiPort = process.env.API_PORT || '8000';

    const response = await fetch(`http://${apiHost}:${apiPort}/api/v1/auth/me`, {
      headers: {
        'Authorization': authHeader,
      },
    });

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Get user error:', error);
    return NextResponse.json(
      { detail: 'Failed to get user info' },
      { status: 500 }
    );
  }
}
