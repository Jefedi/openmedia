# Port Configuration - OpenMedia

## Overview

The `docker-compose.override.yml` file has been created to resolve port conflicts on your system. This file is automatically loaded by Docker Compose and takes precedence over the default configuration.

## Port Mappings

| Service | Default Port | Override Port | Reason |
|---------|--------------|---------------|--------|
| **Redis** | 6379 | **6380** | Port 6379 was already in use on the host |
| **Frontend** | 3000 | **3001** | Port 3000 was already in use on the host |
| PostgreSQL | 5432 | 5432 | No conflict |
| Meilisearch | 7700 | 7700 | No conflict |
| API | 8000 | 8000 | No conflict |

## How to Access Services

After starting the services with `docker compose up -d`, access them at:

- **Frontend**: http://localhost:3001 (changed from 3000)
- **API**: http://localhost:8000
- **Database**: localhost:5432
- **Redis**: localhost:6380 (changed from 6379)
- **Meilisearch**: http://localhost:7700

## Configuration Changes

### 1. Meilisearch Healthcheck Fix

The original configuration used `wget` for healthchecks, but the Meilisearch image doesn't include it. The override changes it to use `curl`:

```yaml
search:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:7700/health"]
```

### 2. Redis Port Mapping

```yaml
redis:
  ports:
    - "6380:6379"  # External port 6380 maps to internal port 6379
```

### 3. Frontend Port Mapping

```yaml
frontend:
  ports:
    - "3001:3000"  # External port 3001 maps to internal port 3000
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

3. **CORS Configuration**: If you're accessing the frontend on port 3001, you may need to update `BACKEND_CORS_ORIGINS` in your `.env`:
   ```env
   BACKEND_CORS_ORIGINS=["http://localhost:3001","http://localhost:8000"]
   ```

4. **Next.js API URL**: Update the frontend's API URL in `.env`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

## Troubleshooting

### All services are starting correctly
If all services show "Up (healthy)" status, you're good to go!

### Services still failing to start
1. Check if other processes are using the overridden ports:
   ```bash
   sudo lsof -i :6380
   sudo lsof -i :3001
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
