'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface LibraryActionsProps {
  mediaType: 'movie' | 'series';
  mediaId: number;
  mediaTitle: string;
}

export default function LibraryActions({ mediaType, mediaId, mediaTitle }: LibraryActionsProps) {
  const [inWatchlist, setInWatchlist] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();

  // Check if user is authenticated and get library status
  useEffect(() => {
    const checkStatus = async () => {
      const token = localStorage.getItem('access_token');

      if (!token) {
        setIsAuthenticated(false);
        return;
      }

      setIsAuthenticated(true);

      try {
        const response = await fetch(`/api/library/check/${mediaType}/${mediaId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setInWatchlist(data.in_watchlist || false);
        }
      } catch (error) {
        console.error('Failed to check library status:', error);
      }
    };

    checkStatus();
  }, [mediaType, mediaId]);

  const handleWatchlistToggle = async () => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem('access_token');

      if (inWatchlist) {
        // Remove from watchlist
        const response = await fetch(
          `/api/library/watchlist?media_type=${mediaType}&media_id=${mediaId}`,
          {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (response.ok) {
          setInWatchlist(false);
        } else {
          console.error('Failed to remove from watchlist');
        }
      } else {
        // Add to watchlist
        const response = await fetch('/api/library/watchlist', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            media_type: mediaType,
            media_id: mediaId,
          }),
        });

        if (response.ok) {
          setInWatchlist(true);
        } else {
          const error = await response.json();
          console.error('Failed to add to watchlist:', error);
        }
      }
    } catch (error) {
      console.error('Watchlist toggle error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center gap-3">
      {/* Add to Watchlist Button */}
      <button
        onClick={handleWatchlistToggle}
        disabled={loading}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition ${
          inWatchlist
            ? 'bg-green-600 hover:bg-green-700 text-white'
            : 'bg-gray-700 hover:bg-gray-600 text-white'
        } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        title={inWatchlist ? 'Retirer de ma liste' : 'Ajouter à ma liste'}
      >
        {loading ? (
          <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        ) : inWatchlist ? (
          <>
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            <span>Dans ma liste</span>
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <span>Ajouter à ma liste</span>
          </>
        )}
      </button>

      {/* View Library Button */}
      {isAuthenticated && (
        <button
          onClick={() => router.push('/library')}
          className="flex items-center gap-2 px-4 py-2 rounded-lg font-semibold bg-blue-600 hover:bg-blue-700 text-white transition"
          title="Voir ma bibliothèque"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <span className="hidden sm:inline">Ma Bibliothèque</span>
        </button>
      )}
    </div>
  );
}
