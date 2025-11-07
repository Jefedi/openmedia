# Database Migration Instructions

## Running the Migration

To create the new tables for cast, crew, and videos, you need to run the migration script inside the backend container.

### Option 1: Using docker compose exec

```bash
docker compose exec backend python run_migration.py
```

### Option 2: Using docker exec with container name

```bash
# First, find the container name
docker ps | grep backend

# Then run the migration
docker exec <backend-container-name> python run_migration.py
```

### Option 3: Manual SQL execution

Connect to your PostgreSQL database and execute the SQL file directly:

```bash
docker compose exec db psql -U your_db_user -d your_db_name -f /path/to/001_add_series_cast_crew_videos.sql
```

Or copy the SQL from `backend/alembic/versions/001_add_series_cast_crew_videos.sql` and execute it in your database client.

## What This Migration Does

This migration creates three new tables:

1. **series_cast** - Stores cast information (actors) for TV series
2. **series_crew** - Stores crew information (creators, writers, producers) for TV series
3. **videos** - Stores video content (trailers, teasers, clips) for both movies and series

## Verification

After running the migration, verify the tables were created:

```sql
-- Check if tables exist
SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('series_cast', 'series_crew', 'videos');

-- Check table structure
\d series_cast
\d series_crew
\d videos
```

## Rollback (if needed)

If you need to rollback the migration:

```sql
DROP TABLE IF EXISTS videos CASCADE;
DROP TABLE IF EXISTS series_crew CASCADE;
DROP TABLE IF EXISTS series_cast CASCADE;
```
