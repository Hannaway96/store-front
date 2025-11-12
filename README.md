# Store Front

A modern e-commerce store front application built with Django REST Framework and React.

## Overview

Store Front is a full-stack web application featuring a Django backend API and a React frontend. The project uses Docker Compose for containerized development, making it easy to set up and run locally.

## Tech Stack

### Backend

- **Python 3.13** - Programming language
- **Django 5.1+** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL 16** - Database
- **Redis 7** - Caching and session storage
- **DRF Spectacular** - API documentation

### Frontend

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite 7** - Build tool and dev server
- **ESLint** - Code linting

### Infrastructure

- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## Features

- Custom user authentication with email-based login
- RESTful API with automatic documentation
- Hot module replacement for rapid development
- PostgreSQL database with automated migrations
- Redis caching for improved performance
- Containerized development environment

## Quick Start

### Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- Git

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd store-front
   ```

2. Start all services:

   ```bash
   docker compose up --build
   ```

3. Access the application:
   - Frontend: <http://localhost:5173>
   - Backend API: <http://localhost:8000>
   - Django Admin: <http://localhost:8000/admin>

For detailed setup instructions, see [docs/init_setup.md](docs/init_setup.md).

## Project Structure

```
store-front/
├── app/
│   ├── backend/          # Django backend application
│   │   ├── app/          # Django project settings
│   │   ├── core/         # Core app with User model
│   │   ├── Dockerfile    # Backend container definition
│   │   └── requirements.txt
│   └── frontend/         # React frontend application
│       ├── src/          # React source code
│       ├── Dockerfile    # Frontend container definition
│       └── package.json
├── docs/                 # Documentation
├── docker-compose.yml    # Multi-container orchestration
└── README.md
```

## Development

### Running Services

Start all services:

```bash
docker compose up
```

Start in detached mode:

```bash
docker compose up -d
```

Stop services:

```bash
docker compose down
```

### Database Operations

Run migrations:

```bash
docker compose exec api python manage.py migrate
```

Create superuser:

```bash
docker compose exec api python manage.py createsuperuser
```

### Viewing Logs

All services:

```bash
docker compose logs -f
```

Specific service:

```bash
docker compose logs -f api
docker compose logs -f frontend
```

## API Documentation

API documentation is automatically generated using DRF Spectacular.
Endpoint is reachable after runner the api through docker
```bash
docker compose up -d
```
To view the interactive docs, navigate to <http://localhost:8000/docs>

## Contributing

1. Create a feature branch
2. Make your changes
3. Ensure tests pass
4. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.

## Authors

- Jack Hannaway
- Daniel O Doherty

## Additional Resources

- [Setup Guide](docs/init_setup.md) - Detailed setup instructions
- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)
