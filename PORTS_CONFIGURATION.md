# Port Configuration - OpenMedia

## Overview

The `docker-compose.override.yml` file has been created to resolve port conflicts on your system. This file is automatically loaded by Docker Compose and takes precedence over the default configuration.

## Port Mappings

| Service | Default Port | Override Port | Reason |
|---------|--------------|---------------|--------|
| **PostgreSQL** | 5432 | **15432** | Port 5432 was already in use on the host |
| **Redis** | 6379 | **16379** | Ports 6379, 6380, 6395 were already in use |
| **Meilisearch** | 7700 | **17700** | Port 7700 was already in use on the host |
| **API** | 8000 | **18000** | Port 8000 was already in use on the host |
| **Frontend** | 3000 | **13000** | Ports 3000, 3001 were already in use |

## How to Access Services

After starting the services with `docker compose up -d`, access them at:

- **Frontend**: http://localhost:13000 (changed from 3000)
- **API**: http://localhost:18000 (changed from 8000)
- **API Docs**: http://localhost:18000/docs
- **Database**: localhost:15432 (changed from 5432)
- **Redis**: localhost:16379 (changed from 6379)
- **Meilisearch**: http://localhost:17700 (changed from 7700)

## Configuration Changes

### 1. Meilisearch Healthcheck Fix

The original configuration used `wget` for healthchecks, but the Meilisearch image doesn't include it. The override changes it to use `curl`:

```yaml
search:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:7700/health"]
```

### 2. Port Mappings

All services have been remapped to use ports in the 10000+ range to avoid conflicts with existing services:

```yaml
services:
  db:
    ports:
      - "15432:5432"  # PostgreSQL external port

  redis:
    ports:
      - "16379:6379"  # Redis external port

  search:
    ports:
      - "17700:7700"  # Meilisearch external port

  api:
    ports:
      - "18000:8000"  # API external port

  frontend:
    ports:
      - "13000:3000"  # Frontend external port
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:18000
```

## Starting the Services

```bash
# Stop any running containers first
docker compose down

# Start all services with the override configuration
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f api
```

## Important Notes

1. **Internal Communication**: Services communicate with each other using the default internal ports (6379, 3000, etc.). Only external access uses the overridden ports.

2. **Environment Variables**: You don't need to change `REDIS_PORT` or `FRONTEND_PORT` in your `.env` file. These define the internal container ports.

3. **CORS Configuration**: Update `BACKEND_CORS_ORIGINS` in your `.env` to match the new ports:
   ```env
   BACKEND_CORS_ORIGINS=["http://localhost:13000","http://localhost:18000"]
   ```

4. **Next.js API URL**: Update the frontend's API URL in `.env`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:18000
   ```

5. **Database Connection**: If connecting externally to PostgreSQL, use port 15432:
   ```bash
   psql -h localhost -p 15432 -U openmedia -d openmedia
   ```

6. **Redis Connection**: If connecting externally to Redis, use port 16379:
   ```bash
   redis-cli -h localhost -p 16379
   ```

## Troubleshooting

### All services are starting correctly
If all services show "Up (healthy)" status, you're good to go!

### Services still failing to start
1. Check if other processes are using the overridden ports:
   ```bash
   sudo ss -ltnp | grep -E ":(15432|16379|17700|18000|13000)"
   ```

2. View detailed logs:
   ```bash
   docker compose logs
   ```

3. Rebuild if needed:
   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up -d
   ```

### Change ports further
If you need different ports, edit `docker-compose.override.yml` and modify the port mappings:
```yaml
services:
  redis:
    ports:
      - "YOUR_PORT:6379"
  frontend:
    ports:
      - "YOUR_PORT:3000"
```

## File Structure

```
.
├── docker-compose.yml              # Base configuration (don't modify)
├── docker-compose.prod.yml         # Production configuration
├── docker-compose.override.yml     # Local overrides (in .gitignore)
└── .env                            # Environment variables
```

The override file is in `.gitignore` so your local port customizations won't be committed to the repository.
