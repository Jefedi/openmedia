'use client';

import { Suspense } from 'react';
import SearchPageContent from './SearchPageContent';
import Header from '@/components/Header';

export default function SearchPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      {/* Header with Search Bar */}
      <Header />

      {/* Search Section - Wrapped in Suspense for useSearchParams */}
      <Suspense fallback={
        <section className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto">
            <div className="animate-pulse">
              <div className="h-10 bg-gray-700 rounded w-1/3 mb-8"></div>
              <div className="h-14 bg-gray-700 rounded mb-8"></div>
              <div className="h-8 bg-gray-700 rounded w-1/4"></div>
            </div>
          </div>
        </section>
      }>
        <SearchPageContent />
      </Suspense>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 text-center text-gray-500 mt-12">
        <p>OpenMedia v0.1.0 - Plateforme Open Source de Films & Séries</p>
        <p className="text-sm mt-2">Propulsé par FastAPI, Next.js, PostgreSQL & OMDb</p>
      </footer>
    </main>
  );
}
