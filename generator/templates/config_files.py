"""
Templates para archivos de configuración e infraestructura.
Incluye Docker, Alembic, linters, etc.
"""

from generator.templates.base import FileTemplate, dedent


def get_config_templates(
    project_name: str, include_docker: bool = True, include_cicd: bool = True
) -> list[FileTemplate]:
    """
    Factory Method (GoF): Crea conjunto de templates de configuración.

    Args:
        project_name: Nombre del proyecto.
        include_docker: Si incluir Dockerfile y docker-compose.yml.
        include_cicd: Si incluir archivos de CI/CD (.github/workflows/).

    Returns:
        Lista de FileTemplate con archivos de configuración.
    """
    templates = [
        _create_env_example_template(),
        _create_gitignore_template(),
        _create_pyproject_toml_template(project_name),
        _create_requirements_txt_template(),
        _create_pre_commit_config_template(),
        _create_alembic_ini_template(),
        _create_alembic_env_template(),
        _create_alembic_script_mako_template(),
        FileTemplate("alembic/versions/.gitkeep", "# Mantiene directorio versions en git\n"),
        _create_readme_template(project_name),
    ]

    if include_docker:
        templates.extend(
            [
                _create_dockerfile_template(),
                _create_docker_compose_template(),
            ]
        )

    if include_cicd:
        templates.extend(get_cicd_templates(project_name))

    return templates


# ==================== .env.example ====================


def _create_env_example_template() -> FileTemplate:
    """Documented environment variables."""
    return FileTemplate(
        ".env.example",
        dedent("""
        # Example configuration for local environment
        # Copy this file to .env and adjust the values

        # Application
        PROJECT_NAME=My API
        VERSION=1.0.0

        # PostgreSQL Database
        # For Docker: use 'db' as host
        # For local: use 'localhost'
        DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mi_api
        # DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/mi_api  # For Docker
        DB_POOL_SIZE=50
        DB_MAX_OVERFLOW=100

        # Redis (for caching)
        # For Docker: use 'redis' as host
        # For local: use 'localhost'
        REDIS_URL=redis://localhost:6379/0
        # REDIS_URL=redis://redis:6379/0  # For Docker
        REDIS_ENABLED=true

        # JWT Security
        # IMPORTANT: Change this in production with a secure random key
        SECRET_KEY=your-secret-key-change-in-production-please-use-a-long-random-string
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=30

        # CORS (JSON list of allowed origins)
        CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
        # CORS_ORIGINS=["*"]  # For development (allows all origins)
    """),
    )


# ==================== .gitignore ====================


def _create_gitignore_template() -> FileTemplate:
    """Complete gitignore for Python."""
    return FileTemplate(
        ".gitignore",
        dedent("""
        # Python
        __pycache__/
        *.py[cod]
        *$py.class
        *.so
        .Python

        # Entornos virtuales
        .venv/
        venv/
        env/
        ENV/

        # Variables de entorno
        .env
        .env.*
        !.env.example

        # Herramientas de desarrollo
        .pytest_cache/
        .mypy_cache/
        .ruff_cache/
        .coverage
        htmlcov/
        .tox/

        # IDEs
        .idea/
        .vscode/
        *.swp
        *.swo
        *~
        .DS_Store

        # Build y distribución
        build/
        dist/
        *.egg-info/
        .eggs/

        # Alembic
        alembic/versions/*.pyc

        # Logs
        *.log

        # Jupyter Notebook
        .ipynb_checkpoints

        # Database
        *.db
        *.sqlite
        *.sqlite3
    """),
    )


# ==================== pyproject.toml ====================


def _create_pyproject_toml_template(project_name: str) -> FileTemplate:
    """Complete configuration with uv and ruff."""
    return FileTemplate(
        "pyproject.toml",
        dedent(f"""
        [project]
        name = "{project_name}"
        version = "0.1.0"
        description = "API FastAPI con arquitectura limpia"
        readme = "README.md"
        requires-python = ">=3.12"
        dependencies = [
            "fastapi>=0.115.0",
            "uvicorn[standard]>=0.32.0",
            "sqlalchemy[asyncio]>=2.0.36",
            "asyncpg>=0.30.0",
            "alembic>=1.14.0",
            "pydantic[email]>=2.10.0",
            "pydantic-settings>=2.6.0",
            "email-validator>=2.0.0",
            "passlib[bcrypt]>=1.7.4",
            "argon2-cffi>=23.1.0",
            "pyjwt>=2.10.0",
            "redis>=5.2.0",
            "python-dotenv>=1.0.0",
        ]

        [project.optional-dependencies]
        dev = [
            "ruff>=0.8.4",
            "pytest>=8.3.0",
            "pytest-asyncio>=0.24.0",
            "httpx>=0.28.0",
            "pre-commit>=4.0.0",
        ]

        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.build"

        [tool.hatch.build.targets.wheel]
        packages = ["app"]

        # Configuración de Ruff (linter + formatter)
        [tool.ruff]
        line-length = 100
        target-version = "py312"

        [tool.ruff.lint]
        select = [
            "E",    # pycodestyle errors
            "F",    # pyflakes
            "I",    # isort
            "N",    # pep8-naming
            "W",    # pycodestyle warnings
            "UP",   # pyupgrade
            "B",    # flake8-bugbear
            "C4",   # flake8-comprehensions
            "SIM",  # flake8-simplify
        ]
        ignore = [
            "E501",  # line too long (manejado por formatter)
        ]

        [tool.ruff.format]
        quote-style = "double"
        indent-style = "space"
        skip-magic-trailing-comma = false
        line-ending = "auto"

        [tool.ruff.lint.isort]
        known-first-party = ["{project_name.replace("-", "_")}"]

        # Configuración de Pytest
        [tool.pytest.ini_options]
        minversion = "8.0"
        addopts = "-ra -q --strict-markers"
        testpaths = ["tests"]
        asyncio_mode = "auto"
        pythonpath = ["."]

        # Configuración de Coverage
        [tool.coverage.run]
        source = ["app"]
        omit = [
            "*/tests/*",
            "*/__init__.py",
        ]

        [tool.coverage.report]
        exclude_lines = [
            "pragma: no cover",
            "def __repr__",
            "raise AssertionError",
            "raise NotImplementedError",
            "if __name__ == .__main__.:",
            "if TYPE_CHECKING:",
        ]
    """),
    )


# ==================== requirements.txt ====================


def _create_requirements_txt_template() -> FileTemplate:
    """Requirements.txt for compatibility."""
    return FileTemplate(
        "requirements.txt",
        dedent("""
        # Generado desde pyproject.toml para compatibilidad
        # Usar: uv sync (recomendado) o pip install -r requirements.txt

        fastapi>=0.115.0
        uvicorn[standard]>=0.32.0
        sqlalchemy[asyncio]>=2.0.36
        asyncpg>=0.30.0
        alembic>=1.14.0
        pydantic[email]>=2.10.0
        pydantic-settings>=2.6.0
        email-validator>=2.0.0
        passlib[bcrypt]>=1.7.4
        argon2-cffi>=23.1.0
        pyjwt>=2.10.0
        redis>=5.2.0
        python-dotenv>=1.0.0
    """),
    )


# ==================== .pre-commit-config.yaml ====================


def _create_pre_commit_config_template() -> FileTemplate:
    """Pre-commit configuration with ruff."""
    return FileTemplate(
        ".pre-commit-config.yaml",
        dedent("""
        # Pre-commit hooks to maintain code quality
        # Installation: pre-commit install
        # Manual execution: pre-commit run --all-files

        repos:
          - repo: https://github.com/pre-commit/pre-commit-hooks
            rev: v4.6.0
            hooks:
              - id: trailing-whitespace
              - id: end-of-file-fixer
              - id: check-yaml
              - id: check-added-large-files
              - id: check-merge-conflict
              - id: debug-statements

          - repo: https://github.com/astral-sh/ruff-pre-commit
            rev: v0.8.4
            hooks:
              # Linter
              - id: ruff
                args: [--fix]
              # Formatter
              - id: ruff-format
    """),
    )


# ==================== alembic.ini ====================


def _create_alembic_ini_template() -> FileTemplate:
    """Base Alembic configuration."""
    return FileTemplate(
        "alembic.ini",
        dedent("""
        # Configuración de Alembic para migraciones de base de datos

        [alembic]
        script_location = alembic
        prepend_sys_path = .
        version_path_separator = os

        # Template para archivos de migración
        file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

        # Timezone para timestamps
        timezone = UTC

        # Truncate slugs más allá de 40 chars
        truncate_slug_length = 40

        # Prefijo de revisión
        revision_environment = false

        # SQLAlchemy URL (se sobrescribe desde env.py con .env)
        sqlalchemy.url = driver://user:pass@localhost/dbname

        [post_write_hooks]

        [loggers]
        keys = root,sqlalchemy,alembic

        [handlers]
        keys = console

        [formatters]
        keys = generic

        [logger_root]
        level = WARN
        handlers = console
        qualname =

        [logger_sqlalchemy]
        level = WARN
        handlers =
        qualname = sqlalchemy.engine

        [logger_alembic]
        level = INFO
        handlers =
        qualname = alembic

        [handler_console]
        class = StreamHandler
        args = (sys.stderr,)
        level = NOTSET
        formatter = generic

        [formatter_generic]
        format = %(levelname)-5.5s [%(name)s] %(message)s
        datefmt = %H:%M:%S
    """),
    )


# ==================== alembic/env.py ====================


def _create_alembic_env_template() -> FileTemplate:
    """Alembic configuration with async support."""
    return FileTemplate(
        "alembic/env.py",
        dedent("""
import asyncio
import sys
from logging.config import fileConfig

# Windows: configure ProactorEventLoop to avoid issues with asyncpg
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.core.config import settings
# Import base.py to execute model imports
# This registers all models in Base.metadata
import app.db.base  # noqa: F401
# Then import Base from base_class to access metadata
from app.db.base_class import Base

# Alembic configuration
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url with settings URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Metadata for autogenerating migrations
# Base.metadata contains all models imported in base.py
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    '''
    Run migrations in 'offline' mode.
    Does not require active DB connection.
    '''
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    '''
    Helper to run migrations with connection.
    '''
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    '''
    Run migrations in async mode.
    '''
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    try:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    except Exception as e:
        # Provide clearer error message
        url = config.get_main_option("sqlalchemy.url")
        raise RuntimeError(
            f"Error connecting to database: {e}\n"
            f"Connection URL: {url}\n"
            f"Make sure the database is running and accessible."
        ) from e
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    '''
    Run migrations in 'online' mode.
    Requires active DB connection (async mode).
    Robust event loop handling for Windows.
    '''
    # Create a new event loop explicitly to avoid issues on Windows
    # when there are existing or closed event loops
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_async_migrations())
    finally:
        loop.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""),
    )


# ==================== alembic/script.py.mako ====================


def _create_alembic_script_mako_template() -> FileTemplate:
    """Mako template for migration files."""
    return FileTemplate(
        "alembic/script.py.mako",
        dedent('''
        """${message}

        Revision ID: ${up_revision}
        Revises: ${down_revision | comma,n}
        Create Date: ${create_date}

        """
        from typing import Sequence, Union

        from alembic import op
        import sqlalchemy as sa
        ${imports if imports else ""}

        # revision identifiers, used by Alembic.
        revision: str = ${repr(up_revision)}
        down_revision: Union[str, None] = ${repr(down_revision)}
        branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
        depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


        def upgrade() -> None:
            ${upgrades if upgrades else "pass"}


        def downgrade() -> None:
            ${downgrades if downgrades else "pass"}
    '''),
    )


# ==================== Dockerfile ====================


def _create_dockerfile_template() -> FileTemplate:
    """Optimized multi-stage Dockerfile."""
    return FileTemplate(
        "Dockerfile",
        dedent("""
        # Multi-stage build para optimizar tamaño de imagen

        # Stage 1: Builder
        FROM python:3.12-slim as builder

        WORKDIR /app

        # Instalar dependencias del sistema
        RUN apt-get update && apt-get install -y \\
            build-essential \\
            libpq-dev \\
            && rm -rf /var/lib/apt/lists/*

        # Copiar archivos de dependencias
        COPY requirements.txt .

        # Instalar dependencias Python
        RUN pip install --no-cache-dir --user -r requirements.txt

        # Stage 2: Runtime
        FROM python:3.12-slim

        WORKDIR /app

        # Instalar solo runtime dependencies
        RUN apt-get update && apt-get install -y \\
            libpq5 \\
            && rm -rf /var/lib/apt/lists/*

        # Copiar dependencias instaladas desde builder
        COPY --from=builder /root/.local /root/.local

        # Agregar binarios al PATH
        ENV PATH=/root/.local/bin:$PATH

        # Copiar código de la aplicación
        COPY . .

        # Variables de entorno
        ENV PYTHONUNBUFFERED=1
        ENV PYTHONDONTWRITEBYTECODE=1

        # Exponer puerto
        EXPOSE 8000

        # Healthcheck
        HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
            CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/users')"

        # Comando por defecto
        CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    """),
    )


# ==================== docker-compose.yml ====================


def _create_docker_compose_template() -> FileTemplate:
    """Docker Compose with API, Postgres, and Redis."""
    return FileTemplate(
        "docker-compose.yml",
        dedent("""

        services:
          api:
            build: .
            container_name: mi-api
            restart: unless-stopped
            environment:
              DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/mi_api
              REDIS_URL: redis://redis:6379/0
              REDIS_ENABLED: "true"
              SECRET_KEY: your-secret-key-change-in-production-please-use-a-long-random-string
              ALGORITHM: HS256
              ACCESS_TOKEN_EXPIRE_MINUTES: 30
            ports:
              - "8000:8000"
            depends_on:
              - db
              - redis
            command: >
              uvicorn app.main:app
              --host 0.0.0.0
              --port 8000
              --reload
            volumes:
              - .:/app
            networks:
              - app-network

          db:
            image: postgres:16-alpine
            container_name: mi-api-db
            restart: unless-stopped
            environment:
              POSTGRES_USER: postgres
              POSTGRES_PASSWORD: postgres
              POSTGRES_DB: mi_api
            ports:
              - "5432:5432"
            volumes:
              - postgres_data:/var/lib/postgresql/data
            networks:
              - app-network
            healthcheck:
              test: ["CMD-SHELL", "pg_isready -U postgres"]
              interval: 10s
              timeout: 5s
              retries: 5

          redis:
            image: redis:7-alpine
            container_name: mi-api-redis
            restart: unless-stopped
            ports:
              - "6379:6379"
            volumes:
              - redis_data:/data
            networks:
              - app-network
            healthcheck:
              test: ["CMD", "redis-cli", "ping"]
              interval: 10s
              timeout: 5s
              retries: 5

        volumes:
          postgres_data:
            driver: local
          redis_data:
            driver: local

        networks:
          app-network:
            driver: bridge
    """),
    )


# ==================== README.md ====================


def _create_readme_template(project_name: str) -> FileTemplate:
    """Complete README with documentation."""
    return FileTemplate(
        "README.md",
        dedent(f"""
        # {project_name}

        FastAPI Clean Architecture API applying SOLID principles and GoF/GRASP design patterns.

        ## 🚀 Tech Stack

        - **Python**: 3.12+
        - **FastAPI**: 0.115+ (async web framework)
        - **SQLAlchemy**: 2.0+ (async ORM)
        - **PostgreSQL**: 16 (database)
        - **Redis**: 7 (cache)
        - **Alembic**: 1.14+ (migrations)
        - **Pydantic**: 2.10+ (data validation)
        - **Ruff**: 0.8+ (linter and formatter)

        ## 📁 Project Structure

        ```
        {project_name}/
        ├── app/
        │   ├── api/              # HTTP Endpoints (presentation layer)
        │   ├── core/             # Configuration, security, events
        │   ├── db/               # SQLAlchemy session and base
        │   ├── models/           # SQLAlchemy models (tables)
        │   ├── schemas/          # Pydantic schemas (validation)
        │   ├── repositories/     # Repository pattern (data access)
        │   ├── services/         # Service layer (business logic)
        │   ├── factories/        # Factory pattern (service creation)
        │   └── utils/            # General utilities
        ├── tests/                # Unit and integration tests
        ├── alembic/              # Database migrations
        └── docker-compose.yml    # Service orchestration
        ```

        ## 🎨 Applied Design Patterns

        ### SOLID
        - **S**ingle Responsibility: Each module has a single responsibility
        - **O**pen/Closed: Extendable without modifying existing code
        - **L**iskov Substitution: Subclasses interchangeable with base classes
        - **I**nterface Segregation: Specific and small interfaces
        - **D**ependency Inversion: Dependencies on abstractions, not concretions

        ### GoF (Gang of Four)
        - **Singleton**: Config, CacheService
        - **Factory**: ServiceFactory for service creation
        - **Strategy**: PasswordHasher (Bcrypt/Argon2 interchangeable)
        - **Observer**: EventDispatcher for system events
        - **Repository**: Data access abstraction

        ### GRASP
        - **Creator**: Factories responsible for creating objects
        - **Information Expert**: Each class knows its own data
        - **Controller**: Endpoints as HTTP controllers
        - **Low Coupling**: Independent modules
        - **High Cohesion**: Related responsibilities together

        ## 🛠️ Installation and Usage

        ### Option 1: With Docker (Recommended)

        ```bash
        # 1. Clone and enter directory
        cd {project_name}

        # 2. Copy environment variables
        cp .env.example .env

        # 3. Edit .env with your settings
        nano .env

        # 4. Start services
        docker-compose up -d

        # 5. Run migrations
        docker-compose exec api alembic upgrade head
        ```

        ### Option 2: Local Development

        ```bash
        # 1. Create virtual environment with uv (recommended)
        uv venv
        source .venv/bin/activate  # Linux/Mac
        # or
        .venv\\Scripts\\activate  # Windows

        # 2. Install dependencies
        uv sync
        # or
        pip install -r requirements.txt

        # Note: If you see a warning about VIRTUAL_ENV not matching,
        # it's safe to ignore. UV will create the correct virtual environment.

        # 3. Copy and configure .env
        cp .env.example .env

        # 4. Start PostgreSQL and Redis (with Docker)
        docker-compose up -d db redis

        # 5. Run migrations
        alembic upgrade head

        # 6. Start development server
        uvicorn app.main:app --reload
        ```

        ## 📚 API Endpoints

        Once the server is started, the API is available at:

        - **API Base**: http://localhost:8000
        - **Interactive Documentation (Swagger)**: http://localhost:8000/docs
        - **Alternative Documentation (ReDoc)**: http://localhost:8000/redoc

        ### Available Endpoints

        #### Users
        - `GET /api/v1/users` - List users
        - `GET /api/v1/users/{{id}}` - Get user
        - `POST /api/v1/users` - Create user
        - `PUT /api/v1/users/{{id}}` - Update user
        - `DELETE /api/v1/users/{{id}}` - Delete user

        #### Products
        - `GET /api/v1/products` - List products

        #### Orders
        - `GET /api/v1/orders` - List orders

        ## 🧪 Testing

        ```bash
        # Run all tests
        pytest

        # With coverage
        pytest --cov=app --cov-report=html

        # Specific tests
        pytest tests/unit/
        pytest tests/integration/
        ```

        ## 🔧 Herramientas de Desarrollo

        ### Linting y Formateo

        ```bash
        # Lint con ruff
        ruff check .

        # Formato con ruff
        ruff format .

        # Pre-commit hooks (automático antes de cada commit)
        pre-commit install
        pre-commit run --all-files
        ```

        ### Database Migrations

        ```bash
        # Create new migration (autogenerate)
        alembic revision --autogenerate -m "change description"

        # Apply migrations
        alembic upgrade head

        # Rollback last migration
        alembic downgrade -1

        # View history
        alembic history
        ```

        ## 🐛 Debugging

        ### Logs

        ```bash
        # View API logs (docker-compose)
        docker-compose logs -f api

        # View API logs (docker)
        docker logs mi-api

        # View PostgreSQL logs
        docker-compose logs -f db

        # View Redis logs
        docker-compose logs -f redis
        ```

        ### Database Access

        ```bash
        # Connect to PostgreSQL (docker-compose)
        docker-compose exec db psql -U postgres -d mi_api

        # Connect to PostgreSQL (docker)
        docker exec -it mi-api-db psql -U postgres -d mi_api

        # Connect to Redis
        docker-compose exec redis redis-cli
        ```

        ### Docker Management

        ```bash
        # Run migrations
        docker exec mi-api alembic upgrade head

        # Create new migration
        docker exec mi-api alembic revision --autogenerate -m "description"

        # Restart services
        docker-compose restart

        # View service status
        docker ps

        # Stop all services
        docker-compose down

        # Stop and remove volumes
        docker-compose down -v
        ```

        ## 📖 Additional Documentation

        ### Adding a New Endpoint

        1. Create model in `app/models/`
        2. Create schema in `app/schemas/`
        3. Create repository in `app/repositories/`
        4. Create service in `app/services/`
        5. Add factory method in `app/factories/service_factory.py`
        6. Create endpoint in `app/api/v1/endpoints/`
        7. Register router in `app/api/v1/router.py`
        8. Create migration: `alembic revision --autogenerate -m "add new_model"`
        9. Apply: `alembic upgrade head`

        ### Important Environment Variables

        - `DATABASE_URL`: PostgreSQL connection URL
        - `REDIS_URL`: Redis connection URL
        - `SECRET_KEY`: Secret key for JWT (change in production)
        - `CORS_ORIGINS`: Allowed origins for CORS

        ## 🤝 Contributing

        1. Fork the project
        2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
        3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
        4. Push to the branch (`git push origin feature/AmazingFeature`)
        5. Open a Pull Request

        ## 📝 License

        This project uses a base architecture generated with professional design principles.

        ## 🙏 Acknowledgments

        - FastAPI for the excellent framework
        - SQLAlchemy for the powerful ORM
        - Alembic for migrations
        - Ruff for ultra-fast linting
    """),
    )


# ==================== GitHub Actions CI/CD ====================


def _create_github_ci_workflow_template(project_name: str) -> FileTemplate:
    """Workflow de CI con uv."""
    return FileTemplate(
        ".github/workflows/ci.yml",
        dedent("""
            name: CI

            on:
              push:
                branches: [ main, develop ]
              pull_request:
                branches: [ main, develop ]

            jobs:
              lint:
                name: Lint Code
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4

                  - name: Install uv
                    uses: astral-sh/setup-uv@v7
                    with:
                      enable-cache: true

                  - name: Set up Python
                    run: uv python install 3.12

                  - name: Install dependencies
                    run: uv sync --all-extras

                  - name: Run Ruff (Linter)
                    run: uv run ruff check .

                  - name: Run Ruff (Formatter check)
                    run: uv run ruff format --check .

              test:
                name: Test on Python ${{ matrix.python-version }}
                runs-on: ubuntu-latest
                strategy:
                  matrix:
                    python-version: ["3.12", "3.13"]

                steps:
                  - uses: actions/checkout@v4

                  - name: Install uv
                    uses: astral-sh/setup-uv@v7
                    with:
                      enable-cache: true
                      cache-dependency-glob: "uv.lock"

                  - name: Set up Python ${{ matrix.python-version }}
                    run: uv python install ${{ matrix.python-version }}

                  - name: Install dependencies
                    run: uv sync --all-extras

                  - name: Run tests
                    run: uv run pytest -v --tb=short

              build:
                name: Build Package
                runs-on: ubuntu-latest
                needs: [lint, test]

                steps:
                  - uses: actions/checkout@v4

                  - name: Install uv
                    uses: astral-sh/setup-uv@v7
                    with:
                      enable-cache: true

                  - name: Set up Python
                    run: uv python install 3.12

                  - name: Build package
                    run: uv build

                  - name: Upload artifacts
                    uses: actions/upload-artifact@v4
                    with:
                      name: dist
                      path: dist/
        """),
    )


def _create_github_release_workflow_template(project_name: str) -> FileTemplate:
    """Workflow de publicación a PyPI."""
    return FileTemplate(
        ".github/workflows/release.yml",
        dedent(f"""
            name: Publish to PyPI

            on:
              release:
                types: [published]

            jobs:
              deploy:
                name: Publish to PyPI
                runs-on: ubuntu-latest
                environment:
                  name: pypi
                  url: https://pypi.org/p/{project_name}
                permissions:
                  id-token: write  # IMPORTANT: mandatory for trusted publishing

                steps:
                  - uses: actions/checkout@v4

                  - name: Install uv
                    uses: astral-sh/setup-uv@v7
                    with:
                      enable-cache: true

                  - name: Set up Python
                    run: uv python install 3.12

                  - name: Build package
                    run: uv build

                  - name: Publish to PyPI
                    uses: pypa/gh-action-pypi-publish@release/v1
                    with:
                      verbose: true
        """),
    )


def _create_github_testpypi_workflow_template(project_name: str) -> FileTemplate:
    """Workflow de publicación a TestPyPI."""
    return FileTemplate(
        ".github/workflows/test-pypi.yml",
        dedent(f"""
            name: Publish to TestPyPI

            on:
              push:
                tags:
                  - 'test-v*'

            jobs:
              deploy:
                name: Publish to TestPyPI
                runs-on: ubuntu-latest
                environment:
                  name: testpypi
                  url: https://test.pypi.org/p/{project_name}
                permissions:
                  id-token: write

                steps:
                  - uses: actions/checkout@v4

                  - name: Install uv
                    uses: astral-sh/setup-uv@v7
                    with:
                      enable-cache: true

                  - name: Set up Python
                    run: uv python install 3.12

                  - name: Build package
                    run: uv build

                  - name: Publish to TestPyPI
                    uses: pypa/gh-action-pypi-publish@release/v1
                    with:
                      repository-url: https://test.pypi.org/legacy/
                      verbose: true
        """),
    )


def get_cicd_templates(project_name: str) -> list[FileTemplate]:
    """
    Factory Method: Crea templates de CI/CD para GitHub Actions.

    Args:
        project_name: Nombre del proyecto para URLs de PyPI.

    Returns:
        Lista de FileTemplate con workflows de GitHub Actions.
    """
    return [
        _create_github_ci_workflow_template(project_name),
        _create_github_release_workflow_template(project_name),
        _create_github_testpypi_workflow_template(project_name),
    ]
