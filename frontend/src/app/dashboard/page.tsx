'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_superuser: boolean;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    // Fetch user info
    fetch('/api/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error('Unauthorized');
        return res.json();
      })
      .then((data) => {
        setUser(data);
        setLoading(false);
      })
      .catch(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/login');
      });
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    router.push('/');
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🎬</div>
          <p className="text-xl text-gray-400">Loading...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      {/* Header */}
      <header className="border-b border-gray-700 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <span className="text-3xl">🎬</span>
              <h1 className="text-2xl font-bold">OpenMedia</h1>
            </Link>
            <div className="flex items-center gap-4">
              <span className="text-gray-400">
                {user?.full_name || user?.username}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold mb-6">
            Welcome, {user?.full_name || user?.username}! 👋
          </h2>

          {user?.is_superuser && (
            <div className="bg-purple-900/20 border border-purple-600/50 rounded-xl p-6 mb-8">
              <div className="flex items-center space-x-3">
                <span className="text-3xl">👑</span>
                <div>
                  <h3 className="text-xl font-bold text-purple-400">Admin Account</h3>
                  <p className="text-gray-400">You have full access to all features</p>
                </div>
              </div>
            </div>
          )}

          {/* User Info Card */}
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-8 mb-8">
            <h3 className="text-2xl font-bold mb-6">Account Information</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <p className="text-gray-400 text-sm mb-1">Email</p>
                <p className="text-white font-medium">{user?.email}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Username</p>
                <p className="text-white font-medium">{user?.username}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Full Name</p>
                <p className="text-white font-medium">{user?.full_name || 'Not set'}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Account Type</p>
                <p className="text-white font-medium">
                  {user?.is_superuser ? 'Administrator' : 'Regular User'}
                </p>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-xl p-6 transition cursor-pointer">
              <div className="text-4xl mb-4">🎯</div>
              <h4 className="text-lg font-bold mb-2">My Watchlist</h4>
              <p className="text-gray-400 text-sm">Track movies and series you want to watch</p>
            </div>

            <div className="bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-xl p-6 transition cursor-pointer">
              <div className="text-4xl mb-4">📊</div>
              <h4 className="text-lg font-bold mb-2">Progress</h4>
              <p className="text-gray-400 text-sm">View your watching progress</p>
            </div>

            <div className="bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700 rounded-xl p-6 transition cursor-pointer">
              <div className="text-4xl mb-4">⭐</div>
              <h4 className="text-lg font-bold mb-2">My Ratings</h4>
              <p className="text-gray-400 text-sm">See all your ratings and reviews</p>
            </div>
          </div>

          {/* Coming Soon */}
          <div className="mt-8 text-center">
            <p className="text-gray-500 text-sm">
              More features coming soon! This is a demo dashboard.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}
