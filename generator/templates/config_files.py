"""
Templates para archivos de configuración e infraestructura.
Incluye Docker, Alembic, linters, etc.
"""

from generator.templates.base import FileTemplate, dedent


def get_config_templates(
    project_name: str,
    include_docker: bool = True,
    include_cicd: bool = True
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
    """Variables de entorno documentadas."""
    return FileTemplate(
        ".env.example",
        dedent("""
        # Ejemplo de configuración para entorno local
        # Copia este archivo a .env y ajusta los valores
        
        # Aplicación
        PROJECT_NAME=Mi API
        VERSION=1.0.0
        
        # Base de datos PostgreSQL
        DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mi_api
        DB_POOL_SIZE=50
        DB_MAX_OVERFLOW=100
        
        # Redis (para cache)
        REDIS_URL=redis://localhost:6379/0
        REDIS_ENABLED=True
        
        # Seguridad JWT
        SECRET_KEY=changeme-generate-secure-key-here
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=30
        
        # CORS (lista separada por comas)
        CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
    """),
    )


# ==================== .gitignore ====================


def _create_gitignore_template() -> FileTemplate:
    """Gitignore completo para Python."""
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
    """Configuración completa con uv y ruff."""
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
            "pydantic>=2.10.0",
            "pydantic-settings>=2.6.0",
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
    """Requirements.txt para compatibilidad."""
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
        pydantic>=2.10.0
        pydantic-settings>=2.6.0
        passlib[bcrypt]>=1.7.4
        argon2-cffi>=23.1.0
        pyjwt>=2.10.0
        redis>=5.2.0
        python-dotenv>=1.0.0
    """),
    )


# ==================== .pre-commit-config.yaml ====================


def _create_pre_commit_config_template() -> FileTemplate:
    """Configuración de pre-commit con ruff."""
    return FileTemplate(
        ".pre-commit-config.yaml",
        dedent("""
        # Pre-commit hooks para mantener calidad de código
        # Instalación: pre-commit install
        # Ejecución manual: pre-commit run --all-files
        
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
    """Configuración base de Alembic."""
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
    """Configuración de Alembic con soporte async."""
    return FileTemplate(
        "alembic/env.py",
        dedent("""
        import asyncio
        from logging.config import fileConfig

        from sqlalchemy import pool
        from sqlalchemy.engine import Connection
        from sqlalchemy.ext.asyncio import async_engine_from_config

        from alembic import context

        from app.core.config import settings
        from app.db.base import Base

        # Configuración de Alembic
        config = context.config

        # Configurar logging
        if config.config_file_name is not None:
            fileConfig(config.config_file_name)

        # Sobrescribir sqlalchemy.url con la de settings
        config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

        # Metadata para autogenerar migraciones
        target_metadata = Base.metadata


        def run_migrations_offline() -> None:
            '''
            Run migrations in 'offline' mode.
            No requiere conexión activa a la BD.
            '''
            url = config.get_main_option("sqlalchemy.url")
            context.configure(
                url=url,
                target_metadata=target_metadata,
                literal_binds=True,
                dialect_opts={{"paramstyle": "named"}},
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()


        def do_run_migrations(connection: Connection) -> None:
            '''
            Helper para ejecutar migraciones con conexión.
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
            Ejecuta migraciones en modo async.
            '''
            connectable = async_engine_from_config(
                config.get_section(config.config_ini_section, {{}}),
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
            )

            async with connectable.connect() as connection:
                await connection.run_sync(do_run_migrations)

            await connectable.dispose()


        def run_migrations_online() -> None:
            '''
            Run migrations in 'online' mode.
            Requiere conexión activa a la BD (modo async).
            '''
            asyncio.run(run_async_migrations())


        if context.is_offline_mode():
            run_migrations_offline()
        else:
            run_migrations_online()
    """),
    )


# ==================== alembic/script.py.mako ====================


def _create_alembic_script_mako_template() -> FileTemplate:
    """Template Mako para archivos de migración."""
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
    """Dockerfile multi-stage optimizado."""
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
    """Docker Compose con API, Postgres y Redis."""
    return FileTemplate(
        "docker-compose.yml",
        dedent("""
        
        services:
          api:
            build: .
            container_name: mi-api
            restart: unless-stopped
            env_file:
              - .env
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
    """README completo con documentación."""
    return FileTemplate(
        "README.md",
        dedent(f"""
        # {project_name}
        
        API FastAPI con arquitectura limpia aplicando principios SOLID y patrones de diseño GoF/GRASP.
        
        ## 🚀 Stack Tecnológico
        
        - **Python**: 3.12+
        - **FastAPI**: 0.115+ (framework web async)
        - **SQLAlchemy**: 2.0+ (ORM async)
        - **PostgreSQL**: 16 (base de datos)
        - **Redis**: 7 (cache)
        - **Alembic**: 1.14+ (migraciones)
        - **Pydantic**: 2.10+ (validación de datos)
        - **Ruff**: 0.8+ (linter y formatter)
        
        ## 📁 Estructura del Proyecto
        
        ```
        {project_name}/
        ├── app/
        │   ├── api/              # Endpoints HTTP (capa de presentación)
        │   ├── core/             # Configuración, seguridad, eventos
        │   ├── db/               # Sesión y base SQLAlchemy
        │   ├── models/           # Modelos SQLAlchemy (tablas)
        │   ├── schemas/          # Schemas Pydantic (validación)
        │   ├── repositories/     # Repository pattern (acceso a datos)
        │   ├── services/         # Service layer (lógica de negocio)
        │   ├── factories/        # Factory pattern (creación de servicios)
        │   └── utils/            # Utilidades generales
        ├── tests/                # Tests unitarios e integración
        ├── alembic/              # Migraciones de base de datos
        └── docker-compose.yml    # Orquestación de servicios
        ```
        
        ## 🎨 Patrones de Diseño Aplicados
        
        ### SOLID
        - **S**ingle Responsibility: Cada módulo tiene una única responsabilidad
        - **O**pen/Closed: Extendible sin modificar código existente
        - **L**iskov Substitution: Subclases intercambiables con clases base
        - **I**nterface Segregation: Interfaces específicas y pequeñas
        - **D**ependency Inversion: Dependencias de abstracciones, no concreciones
        
        ### GoF (Gang of Four)
        - **Singleton**: Config, CacheService
        - **Factory**: ServiceFactory para creación de servicios
        - **Strategy**: PasswordHasher (Bcrypt/Argon2 intercambiables)
        - **Observer**: EventDispatcher para eventos del sistema
        - **Repository**: Abstracción de acceso a datos
        
        ### GRASP
        - **Creator**: Factories responsables de crear objetos
        - **Information Expert**: Cada clase conoce sus propios datos
        - **Controller**: Endpoints como controllers HTTP
        - **Low Coupling**: Módulos independientes
        - **High Cohesion**: Responsabilidades relacionadas juntas
        
        ## 🛠️ Instalación y Uso
        
        ### Opción 1: Con Docker (Recomendado)
        
        ```bash
        # 1. Clonar y entrar al directorio
        cd {project_name}
        
        # 2. Copiar variables de entorno
        cp .env.example .env
        
        # 3. Editar .env con tus configuraciones
        nano .env
        
        # 4. Levantar servicios
        docker-compose up -d
        
        # 5. Ejecutar migraciones
        docker-compose exec api alembic upgrade head
        ```
        
        ### Opción 2: Desarrollo Local
        
        ```bash
        # 1. Crear entorno virtual con uv (recomendado)
        uv venv
        source .venv/bin/activate  # Linux/Mac
        # o
        .venv\\Scripts\\activate  # Windows
        
        # 2. Instalar dependencias
        uv sync
        # o
        pip install -r requirements.txt
        
        # 3. Copiar y configurar .env
        cp .env.example .env
        
        # 4. Levantar PostgreSQL y Redis (con Docker)
        docker-compose up -d db redis
        
        # 5. Ejecutar migraciones
        alembic upgrade head
        
        # 6. Iniciar servidor de desarrollo
        uvicorn app.main:app --reload
        ```
        
        ## 📚 API Endpoints
        
        Una vez iniciado el servidor, la API está disponible en:
        
        - **API Base**: http://localhost:8000
        - **Documentación Interactiva (Swagger)**: http://localhost:8000/docs
        - **Documentación Alternativa (ReDoc)**: http://localhost:8000/redoc
        
        ### Endpoints Disponibles
        
        #### Users
        - `GET /api/v1/users` - Listar usuarios
        - `GET /api/v1/users/{{id}}` - Obtener usuario
        - `POST /api/v1/users` - Crear usuario
        - `PUT /api/v1/users/{{id}}` - Actualizar usuario
        - `DELETE /api/v1/users/{{id}}` - Eliminar usuario
        
        #### Products
        - `GET /api/v1/products` - Listar productos
        
        #### Orders
        - `GET /api/v1/orders` - Listar órdenes
        
        ## 🧪 Testing
        
        ```bash
        # Ejecutar todos los tests
        pytest
        
        # Con coverage
        pytest --cov=app --cov-report=html
        
        # Tests específicos
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
        
        ### Migraciones de Base de Datos
        
        ```bash
        # Crear nueva migración (autogenerar)
        alembic revision --autogenerate -m "descripción del cambio"
        
        # Aplicar migraciones
        alembic upgrade head
        
        # Revertir última migración
        alembic downgrade -1
        
        # Ver historial
        alembic history
        ```
        
        ## 🐛 Debugging
        
        ### Logs
        
        ```bash
        # Ver logs de la API
        docker-compose logs -f api
        
        # Ver logs de PostgreSQL
        docker-compose logs -f db
        
        # Ver logs de Redis
        docker-compose logs -f redis
        ```
        
        ### Acceso a Base de Datos
        
        ```bash
        # Conectar a PostgreSQL
        docker-compose exec db psql -U postgres -d mi_api
        
        # Conectar a Redis
        docker-compose exec redis redis-cli
        ```
        
        ## 📖 Documentación Adicional
        
        ### Agregar Nuevo Endpoint
        
        1. Crear modelo en `app/models/`
        2. Crear schema en `app/schemas/`
        3. Crear repository en `app/repositories/`
        4. Crear service en `app/services/`
        5. Agregar factory method en `app/factories/service_factory.py`
        6. Crear endpoint en `app/api/v1/endpoints/`
        7. Registrar router en `app/api/v1/router.py`
        8. Crear migración: `alembic revision --autogenerate -m "add nuevo_modelo"`
        9. Aplicar: `alembic upgrade head`
        
        ### Variables de Entorno Importantes
        
        - `DATABASE_URL`: URL de conexión a PostgreSQL
        - `REDIS_URL`: URL de conexión a Redis
        - `SECRET_KEY`: Clave secreta para JWT (cambiar en producción)
        - `CORS_ORIGINS`: Orígenes permitidos para CORS
        
        ## 🤝 Contribuir
        
        1. Fork el proyecto
        2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
        3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
        4. Push a la rama (`git push origin feature/AmazingFeature`)
        5. Abre un Pull Request
        
        ## 📝 Licencia
        
        Este proyecto usa una arquitectura base generada con principios de diseño profesional.
        
        ## 🙏 Agradecimientos
        
        - FastAPI por el excelente framework
        - SQLAlchemy por el poderoso ORM
        - Alembic por las migraciones
        - Ruff por el linting ultrarrápido
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
