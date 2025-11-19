# FastAPI Template Generator

Professional CLI generator for FastAPI projects with clean architecture applying **SOLID** principles and **GoF** and **GRASP** design patterns.

## 🚀 Features

- ✅ **Clean architecture** with clear separation of concerns
- ✅ **FastAPI 0.115+** with full async support
- ✅ **SQLAlchemy 2.0** async + PostgreSQL 16
- ✅ **Redis 7** for caching
- ✅ **Alembic** for async migrations
- ✅ **Pydantic v2** for validation
- ✅ **Ruff** for ultra-fast linting and formatting
- ✅ **Docker** and docker-compose pre-configured
- ✅ **Unit and integration tests** with pytest-asyncio
- ✅ **Pre-commit hooks** for code quality
- ✅ **Functional examples** with complete **CRUD**

## 📐 Design Patterns Applied

### Generator (template-proyects)

**SOLID:**

- **S**ingle Responsibility: Each module has a clear responsibility
- **O**pen/Closed: Extensible without modifying existing code
- **L**iskov Substitution: Interchangeable validators/templates
- **I**nterface Segregation: Small and specific interfaces
- **D**ependency Inversion: Depends on abstractions

**GoF:**

- **Singleton**: Config via lru_cache
- **Factory Method**: `get_*_templates()`, `create_validator_chain()`
- **Template Method**: `CLI.run()`, `ProjectCreator.create()`, `Validator.validate()`
- **Chain of Responsibility**: Validator chain
- **Strategy**: Callable content in FileTemplate
- **Facade**: CLI simplifies access to subsystems

**GRASP:**

- **Creator**: ProjectCreator, factory functions
- **Information Expert**: Each module knows its domain
- **Controller**: CLI coordinates without doing heavy work
- **Low Coupling**: Independent modules
- **High Cohesion**: Clear responsibilities
- **Pure Fabrication**: FileTemplate, validators
- **Protected Variations**: Stable abstractions

### Generated Project (FastAPI app)

**Implemented patterns:**

- **Singleton**: Config, CacheService
****- **Factory**: **ServiceFactory** for service creation
- **Strategy**: PasswordHasher (interchangeable Bcrypt/Argon2)
- **Observer**: EventDispatcher for system events
- **Repository**: Complete data access abstraction
- **Service Layer**: Separated business logic
- **Dependency Injection**: FastAPI Depends + Factory

## 📦 Installation

### With uv (Recommended)

```bash
# Clone or download the repository
cd template-proyects

# Install dependencies
uv sync

# The generator is ready to use
python -m template-proyects --help
```

### With pip

```bash
cd template-proyects
pip install -r requirements.txt
python -m template-proyects --help
```

## 🎯 Usage

### Basic Syntax

```bash
python -m template-proyects <project-name> [options]
```

### Examples

```bash
# Generate basic project with all features
python -m template-proyects my-api

# Use Argon2 for hashing (recommended, default)
python -m template-proyects my-api --hash-algo argon2

# Use Bcrypt for hashing
python -m template-proyects my-api --hash-algo bcrypt

# Without Docker
python -m template-proyects my-api --no-docker

# Without tests
python -m template-proyects my-api --no-tests

# Specify output directory
python -m template-proyects my-api --output-dir ~/projects

# Overwrite existing project
python -m template-proyects my-api --overwrite
```

### Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `project_name` | Project name (required) | - |
| `--output-dir` | Directory where to create the project | Current directory |
| `--hash-algo` | Hash algorithm (`bcrypt` or `argon2`) | `argon2` |
| `--no-docker` | Don't generate Dockerfile or docker-compose | `False` |
| `--no-tests` | Don't generate tests/ directory | `False` |
| `--overwrite` | Overwrite existing project | `False` |

## 📁 Generated Project Structure

```
my-api/
├── app/
│   ├── api/              # Presentation layer (HTTP)
│   │   ├── dependencies.py
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── users.py      # Complete CRUD
│   │           ├── products.py
│   │           └── orders.py
│   ├── core/             # Application core
│   │   ├── config.py     # Singleton with pydantic-settings
│   │   ├── security.py   # Strategy (Bcrypt/Argon2) + JWT
│   │   ├── events.py     # Async Observer pattern
│   │   └── exceptions.py
│   ├── db/
│   │   ├── session.py    # AsyncSession factory
│   │   └── base.py
│   ├── models/           # SQLAlchemy models (async)
│   │   ├── user.py
│   │   ├── product.py
│   │   └── order.py
│   ├── schemas/          # Pydantic v2 schemas
│   │   ├── user.py
│   │   ├── product.py
│   │   └── order.py
│   ├── repositories/     # Repository pattern (async)
│   │   ├── base.py       # Generic BaseRepository
│   │   ├── user_repository.py
│   │   ├── product_repository.py
│   │   └── order_repository.py
│   ├── services/         # Service layer (business logic)
│   │   ├── cache_service.py  # Async Redis
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   └── order_service.py
│   ├── factories/
│   │   └── service_factory.py  # Factory pattern
│   └── utils/
├── tests/
│   ├── conftest.py       # Async fixtures
│   ├── unit/
│   │   ├── test_services.py
│   │   └── test_repositories.py
│   └── integration/
│       └── test_users_endpoint.py
├── alembic/              # Async migrations
│   ├── env.py
│   └── versions/
├── docker-compose.yml    # Postgres + Redis + API
├── Dockerfile
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
└── README.md
```

## 🔧 Using the Generated Project

### 1. Configure Environment Variables

```bash
cd my-api
cp .env.example .env
# Edit .env with your configurations
```

### 2. With Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head
```

### 3. Local Development

```bash
# Install dependencies
uv sync

# Start only Postgres and Redis
docker-compose up -d db redis

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### 4. Access the API

- **API Base**: <http://localhost:8000>
- **Swagger Documentation**: <http://localhost:8000/docs>
- **ReDoc Documentation**: <http://localhost:8000/redoc>

### 5. Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/
```

## 🛠️ Generated Project Tech Stack

| Category | Technology | Version |
|----------|-----------|---------|
| **Framework** | FastAPI | 0.115+ |
| **Python** | Python | 3.12+ |
| **ORM** | SQLAlchemy | 2.0.36+ (async) |
| **Database** | PostgreSQL | 16 |
| **Driver** | asyncpg | 0.30+ |
| **Migrations** | Alembic | 1.14+ |
| **Cache** | Redis | 5.2+ (native async) |
| **Validation** | Pydantic | 2.10+ |
| **Server** | Uvicorn | 0.32+ |
| **Hash** | passlib + bcrypt/argon2 | Latest |
| **JWT** | PyJWT | 2.10+ |
| **Linter** | Ruff | 0.8+ |
| **Testing** | pytest + pytest-asyncio | 8.3+ |
| **HTTP Client (tests)** | httpx | 0.28+ |
| **Hooks** | pre-commit | 4.0+ |

## 📚 Additional Documentation

### Adding a New Resource

To add a new resource (e.g., `category`):

1. **Model**: `app/models/category.py`
2. **Schema**: `app/schemas/category.py`
3. **Repository**: `app/repositories/category_repository.py`
4. **Service**: `app/services/category_service.py`
5. **Factory**: Add `create_category_service()` in `service_factory.py`
6. **Endpoint**: `app/api/v1/endpoints/categories.py`
7. **Router**: Register in `app/api/v1/router.py`
8. **Migration**: `alembic revision --autogenerate -m "add category"`
9. **Tests**: Add tests in `tests/`

### Useful Commands

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1

# View history
alembic history

# Lint
ruff check .

# Format
ruff format .

# Install pre-commit
pre-commit install
```

## 🎓 Usage Examples

The generated project includes a complete user CRUD that demonstrates:

- ✅ Validation with Pydantic v2
- ✅ Async Repository pattern
- ✅ Service layer with business logic
- ✅ Redis caching
- ✅ Observer pattern events
- ✅ Secure password hashing (Argon2/Bcrypt)
- ✅ Custom exception handling
- ✅ Unit tests with mocks
- ✅ E2E integration tests

## 🤝 Contributing

Contributions are welcome. Please:

1. Fork the project
2. Create a branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is designed as a professional development tool.

## 🙏 Acknowledgements

- FastAPI for the excellent framework
- SQLAlchemy for the powerful ORM
- Rich for the beautiful CLI
- Ruff for ultra-fast linting
- Python community for the amazing tools

---

**Generated with ❤️ following clean architecture principles**
