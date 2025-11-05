-- Script d'initialisation de la base de données OpenMedia
-- Exécuté automatiquement au premier démarrage de PostgreSQL

-- Créer les extensions nécessaires
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Pour la recherche full-text
CREATE EXTENSION IF NOT EXISTS "unaccent"; -- Pour ignorer les accents dans la recherche

-- Configurer la timezone
SET timezone = 'UTC';

-- Log
DO $$
BEGIN
    RAISE NOTICE 'OpenMedia database initialized successfully';
END $$;
