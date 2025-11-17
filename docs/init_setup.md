# Initial Setup Guide

This guide will walk you through setting up the Store Front project using Docker Compose.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git** (for cloning the repository)

You can verify your installations by running:

```bash
docker --version
docker compose version
git --version
```

## Project Structure

This project uses a multi-container Docker setup with the following services:

- **Frontend**: React + TypeScript + Vite application
- **Backend**: Django REST Framework API
- **Database**: PostgreSQL 16
- **Cache**: Redis 7

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd store-front
```

### 2. Environment Variables (Optional)

The project uses default environment variables configured in `docker-compose.yml`. If you need to customize them, you can create a `.env` file in the root directory or set environment variables directly.

Default values:

- **Database**:
  - Name: `store_db`
  - User: `store_user`
  - Password: `storePassword123!`
  - Host: `db` (internal Docker network)
  - Port: `5432`
- **Redis**: `redis://redis:6379/1`
- **Frontend API URL**: `http://localhost:8000`
- **Backend Debug**: `1` (enabled)
- **Backend Secret Key**: `dev-secret`

### 3. Build and Start Services

From the project root directory, run:

```bash
docker compose build
docker compose up
# or

docker compose up --build
```

This command will:

- Build the Docker images for both frontend and backend
- Pull PostgreSQL and Redis images
- Start all services and their dependencies
- Run database migrations automatically
- Start the development servers

### 4. Access the Application

Once all containers are running, you can access:

- **Frontend**: <http://localhost:5173>
- **Backend API**: <http://localhost:8000>
- **Database**: localhost:5432 (if you need direct access)
- **Redis**: localhost:6379 (if you need direct access)

## Service Details

### Frontend Service

- **Port**: 5173
- **Technology**: React 19, TypeScript, Vite 7
- **Hot Reload**: Enabled (changes reflect automatically)
- **Working Directory**: `/app`
- **Node Modules**: Persisted in Docker volume `frontend_modules`

### Backend Service

- **Port**: 8000
- **Technology**: Django 5.1+, Django REST Framework, Python 3.13
- **Features**:
  - Automatic database migrations on startup
  - Database connection waiting (ensures DB is ready)
  - Development server with hot reload
  - Static/media files stored in `/vol/web`
- **Dependencies**: Installed using UV from `requirements.txt` and `requirements.dev.txt` (or `pyproject.toml` for modern Python projects)

### Database Service

- **Image**: PostgreSQL 16 Alpine
- **Port**: 5432
- **Data Persistence**: Docker volume `db-data`
- **Credentials**: See environment variables section above

### Redis Service

- **Image**: Redis 7 Alpine
- **Port**: 6379
- **Purpose**: Caching and session storage

## Common Commands

### Start services in detached mode

```bash
docker compose up -d
```

### Stop services

```bash
docker compose down
```

### Stop services and remove volumes (⚠️ deletes database data)

```bash
docker compose down -v
```

### View logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs api
docker compose logs frontend
docker compose logs db
```

### Follow logs in real-time

```bash
docker compose logs -f
```

### Execute commands in containers

```bash
# Backend (Django management commands)
docker compose exec api python manage.py createsuperuser
docker compose exec api python manage.py shell

# Frontend (npm commands)
docker compose exec frontend npm install <package>
```

### Rebuild specific service

```bash
docker compose build api
docker compose build frontend
```

## Development Workflow

### Backend Development

1. Create virtual environment and install python dependencies. The shell script in `scripts/` will handle both. The script uses UV for fast dependency management.
   ```bash
   cd scripts
   bash create_venv.sh
   ```
   
   **Note**: If UV is not installed, the script will automatically install it. Alternatively, you can install UV manually:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```   
2. Make changes to Python files in `app/backend/`
3. Changes are automatically reflected (volume mounting)
4. For new dependencies, add them to `requirements.txt` or `requirements.dev.txt`
5. Rebuild the container: `docker compose build api`
6. Restart: `docker compose restart api`

### Frontend Development

1. Make changes to files in `app/frontend/src/`
2. Vite hot module replacement will automatically reload the browser
3. For new dependencies, add them to `package.json`
4. Install: `docker compose exec frontend npm install`
5. Or rebuild: `docker compose build frontend`

### Database Migrations

Migrations run automatically on container startup. To manually run migrations:

```bash
docker compose exec api python manage.py migrate
```

### Creating a Superuser

```bash
docker compose exec api python manage.py createsuperuser
```

## Troubleshooting

### Port Already in Use

If ports 5173, 8000, 5432, or 6379 are already in use:

1. Stop the conflicting service, or
2. Modify the port mappings in `docker-compose.yml`

### Permission Issues

The frontend Dockerfile uses `USER_ID` and `GROUP_ID` build args that default to 1000. If you encounter permission issues:

```bash
# Set your user/group IDs
export UID=$(id -u)
export GID=$(id -g)
docker compose up --build
```

### Database Connection Errors

If the backend fails to connect to the database:

1. Ensure the `db` service is running: `docker compose ps`
2. Check database logs: `docker compose logs db`
3. Verify environment variables match in `docker-compose.yml`

### Frontend Cannot Reach Backend

1. Ensure `VITE_API_URL` in `docker-compose.yml` matches your backend URL
2. Check that the `api` service is running: `docker compose ps`
3. Verify CORS settings if applicable

### Clear Everything and Start Fresh

```bash
# Stop containers, remove volumes, and rebuild
docker compose down -v
docker compose build --no-cache
docker compose up
```

## Docker Volumes

The project uses the following named volumes:

- `db-data`: PostgreSQL data persistence
- `static-data`: Django static and media files
- `frontend_modules`: Node.js dependencies (prevents host/container conflicts)

To inspect volumes:

```bash
docker volume ls
docker volume inspect store-front_db-data
```

## Next Steps

After setup is complete:

1. Access the frontend at <http://localhost:5173>
2. Access the Django admin at <http://localhost:8000/admin> (after creating a superuser)
3. API documentation available via DRF Spectacular (check Django URLs configuration)
4. Start developing!

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Django Rest Framework Documentation](https://www.django-rest-framework.org/)
- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
