'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import MediaCard from '@/components/MediaCard';
import Header from '@/components/Header';

interface Movie {
  id: number;
  title: string;
  year?: number;
  poster_path?: string;
  vote_average?: number;
  overview?: string;
}

interface Series {
  id: number;
  name: string;
  year?: number;
  poster_path?: string;
  vote_average?: number;
  overview?: string;
}

export default function Home() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [series, setSeries] = useState<Series[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Charger les films et séries depuis l'API
    Promise.all([
      fetch('/api/movies').then(res => res.ok ? res.json() : { movies: [] }),
      fetch('/api/series').then(res => res.ok ? res.json() : { series: [] })
    ])
      .then(([moviesData, seriesData]) => {
        setMovies(moviesData.movies || []);
        setSeries(seriesData.series || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Failed to load data:', error);
        setLoading(false);
      });
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      {/* Header with Search Bar */}
      <Header />

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-600 text-transparent bg-clip-text">
            Votre Plateforme de Films & Séries
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Découvrez, suivez et gérez vos films et séries préférés avec OpenMedia
          </p>
        </div>
      </section>

      {/* Films Récents */}
      <section className="container mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold">🎥 Films Récents</h2>
          <Link
            href="/movies"
            className="text-blue-400 hover:text-blue-300 transition flex items-center gap-2"
          >
            Voir tout
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-gray-800 rounded-lg aspect-[2/3] animate-pulse"></div>
            ))}
          </div>
        ) : movies.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {movies.slice(0, 6).map((movie) => (
              <MediaCard
                key={movie.id}
                id={movie.id}
                title={movie.title}
                year={movie.year}
                posterPath={movie.poster_path}
                voteAverage={movie.vote_average}
                type="movie"
                overview={movie.overview}
              />
            ))}
          </div>
        ) : (
          <div className="bg-gray-800/50 rounded-lg p-12 text-center">
            <p className="text-gray-400 mb-4">Aucun film disponible pour le moment</p>
            <Link
              href="/search"
              className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition"
            >
              Rechercher des films
            </Link>
          </div>
        )}
      </section>

      {/* Séries Récentes */}
      <section className="container mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold">📺 Séries Récentes</h2>
          <Link
            href="/series"
            className="text-blue-400 hover:text-blue-300 transition flex items-center gap-2"
          >
            Voir tout
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-gray-800 rounded-lg aspect-[2/3] animate-pulse"></div>
            ))}
          </div>
        ) : series.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {series.slice(0, 6).map((show) => (
              <MediaCard
                key={show.id}
                id={show.id}
                title={show.name}
                year={show.year}
                posterPath={show.poster_path}
                voteAverage={show.vote_average}
                type="series"
                overview={show.overview}
              />
            ))}
          </div>
        ) : (
          <div className="bg-gray-800/50 rounded-lg p-12 text-center">
            <p className="text-gray-400 mb-4">Aucune série disponible pour le moment</p>
            <Link
              href="/search"
              className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition"
            >
              Rechercher des séries
            </Link>
          </div>
        )}
      </section>

      {/* Call to Action */}
      <section className="container mx-auto px-4 py-16">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center">
          <h2 className="text-4xl font-bold mb-4">Prêt à commencer ?</h2>
          <p className="text-xl mb-8 text-blue-100">
            Créez votre compte et commencez à suivre vos films et séries préférés
          </p>
          <Link
            href="/register"
            className="inline-block px-8 py-4 bg-white text-blue-600 rounded-lg font-bold hover:bg-gray-100 transition text-lg"
          >
            Créer un compte gratuitement
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 text-center text-gray-500">
        <p>OpenMedia v0.1.0 - Plateforme Open Source de Films & Séries</p>
        <p className="text-sm mt-2">Propulsé par FastAPI, Next.js, PostgreSQL & OMDb</p>
      </footer>
    </main>
  );
}
