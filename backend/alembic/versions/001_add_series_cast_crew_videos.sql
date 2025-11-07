-- Migration: Add SeriesCast, SeriesCrew, and Video tables
-- Date: 2025-11-07
-- Description: Add support for series cast/crew and videos for movies/series

-- ============================================================================
-- 1. Create series_cast table (similar to cast but for series)
-- ============================================================================
CREATE TABLE IF NOT EXISTS series_cast (
    id SERIAL PRIMARY KEY,
    series_id INTEGER NOT NULL REFERENCES series(id) ON DELETE CASCADE,
    person_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    character VARCHAR(500),
    "order" INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_series_cast UNIQUE (series_id, person_id, character)
);

CREATE INDEX IF NOT EXISTS idx_series_cast_series_id ON series_cast(series_id);
CREATE INDEX IF NOT EXISTS idx_series_cast_person_id ON series_cast(person_id);

-- ============================================================================
-- 2. Create series_crew table (similar to crew but for series)
-- ============================================================================
CREATE TABLE IF NOT EXISTS series_crew (
    id SERIAL PRIMARY KEY,
    series_id INTEGER NOT NULL REFERENCES series(id) ON DELETE CASCADE,
    person_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    job VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_series_crew UNIQUE (series_id, person_id, job)
);

CREATE INDEX IF NOT EXISTS idx_series_crew_series_id ON series_crew(series_id);
CREATE INDEX IF NOT EXISTS idx_series_crew_person_id ON series_crew(person_id);

-- ============================================================================
-- 3. Create videos table (for both movies and series)
-- ============================================================================
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    series_id INTEGER REFERENCES series(id) ON DELETE CASCADE,
    key VARCHAR(255) NOT NULL,
    name VARCHAR(500) NOT NULL,
    site VARCHAR(50) NOT NULL DEFAULT 'YouTube',
    type VARCHAR(50) NOT NULL,
    size INTEGER NOT NULL DEFAULT 1080,
    official BOOLEAN NOT NULL DEFAULT true,
    published_at TIMESTAMP,
    iso_639_1 VARCHAR(10),
    iso_3166_1 VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_video_media_key UNIQUE (movie_id, series_id, key),
    CONSTRAINT check_video_has_media CHECK (
        (movie_id IS NOT NULL AND series_id IS NULL) OR
        (movie_id IS NULL AND series_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_videos_movie_id ON videos(movie_id);
CREATE INDEX IF NOT EXISTS idx_videos_series_id ON videos(series_id);
CREATE INDEX IF NOT EXISTS idx_videos_type ON videos(type);

-- ============================================================================
-- ROLLBACK INSTRUCTIONS (if needed)
-- ============================================================================
-- DROP TABLE IF EXISTS videos CASCADE;
-- DROP TABLE IF EXISTS series_crew CASCADE;
-- DROP TABLE IF EXISTS series_cast CASCADE;
