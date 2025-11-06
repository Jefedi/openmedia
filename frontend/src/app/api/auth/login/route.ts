import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const apiHost = process.env.API_HOST || 'api';
    const apiPort = process.env.API_PORT || '8000';

    const response = await fetch(`http://${apiHost}:${apiPort}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { detail: 'Login failed' },
      { status: 500 }
    );
  }
}
