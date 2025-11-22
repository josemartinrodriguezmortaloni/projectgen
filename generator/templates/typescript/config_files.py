"""
Templates para archivos de configuración e infraestructura (TypeScript).
"""

from generator.templates.base import FileTemplate, dedent


def get_config_templates(
    project_name: str,
    package_manager: str,
    include_docker: bool,
    include_tests: bool,
    include_cicd: bool,
    include_queue: bool,
) -> list[FileTemplate]:
    """
    Factory Method: Crea templates de configuración para TypeScript.
    """
    templates = [
        _create_package_json_template(project_name, include_queue),
        _create_env_example_template(),
        _create_readme_template(project_name, package_manager),
        _create_gitignore_template(),
        _create_monitoring_module_template(),
        FileTemplate("src/monitoring/metrics.service.ts", _create_metrics_service_content()),
    ]

    if include_docker:
        templates.extend(
            [
                _create_dockerfile_template(package_manager),
                _create_docker_compose_template(project_name),
            ]
        )

    if include_cicd:
        templates.append(_create_github_workflow_template(package_manager))

    if include_queue:
        templates.append(FileTemplate("src/queue/.gitkeep", ""))

    return templates


def _create_package_json_template(project_name: str, include_queue: bool) -> FileTemplate:
    """package.json with NestJS and AI dependencies."""
    dependencies = [
        '"@nestjs/common": "^10.0.0"',
        '"@nestjs/core": "^10.0.0"',
        '"@nestjs/config": "^3.2.0"',
        '"@nestjs/platform-express": "^10.0.0"',
        '"@nestjs/swagger": "^7.3.0"',
        '"@nestjs/throttler": "^5.1.2"',
        '"reflect-metadata": "^0.2.0"',
        '"rxjs": "^7.8.1"',
        '"class-transformer": "^0.5.1"',
        '"class-validator": "^0.14.1"',
        '"helmet": "^7.1.0"',
        '"compression": "^1.7.4"',
        '"zod": "^3.22.4"',
        '"@t3-oss/env-core": "^0.9.2"',
        # AI SDKs
        '"ai": "^3.0.13"',
        '"@ai-sdk/openai": "^0.0.14"',
        '"@ai-sdk/anthropic": "^0.0.15"',
        '"@ai-sdk/google": "^0.0.13"',
        # Database
        '"drizzle-orm": "^0.30.4"',
        '"postgres": "^3.4.4"',
        '"@nestjs/mapped-types": "*"',
    ]

    if include_queue:
        dependencies.extend(
            [
                '"@nestjs/bullmq": "^10.1.0"',
                '"bullmq": "^5.4.1"',
            ]
        )

    devDependencies = [
        '"@nestjs/cli": "^10.0.0"',
        '"@nestjs/schematics": "^10.0.0"',
        '"@nestjs/testing": "^10.0.0"',
        '"@types/express": "^4.17.17"',
        '"@types/jest": "^29.5.2"',
        '"@types/node": "^20.3.1"',
        '"@types/supertest": "^6.0.0"',
        '"@typescript-eslint/eslint-plugin": "^6.0.0"',
        '"@typescript-eslint/parser": "^6.0.0"',
        '"eslint": "^8.42.0"',
        '"eslint-config-prettier": "^9.0.0"',
        '"eslint-plugin-prettier": "^5.0.0"',
        '"eslint-plugin-import": "^2.29.1"',
        '"jest": "^29.5.0"',
        '"prettier": "^3.0.0"',
        '"source-map-support": "^0.5.21"',
        '"supertest": "^6.3.3"',
        '"ts-jest": "^29.1.0"',
        '"ts-loader": "^9.4.3"',
        '"ts-node": "^10.9.1"',
        '"tsconfig-paths": "^4.2.0"',
        '"typescript": "^5.1.3"',
        '"drizzle-kit": "^0.20.14"',
        '"dotenv": "^16.4.5"',
    ]

    deps_str = ",\n    ".join(sorted(dependencies))
    dev_deps_str = ",\n    ".join(sorted(devDependencies))

    return FileTemplate(
        "package.json",
        dedent(f"""
        {{
          "name": "{project_name}",
          "version": "0.0.1",
          "description": "Enterprise AI Agents Platform",
          "author": "",
          "private": true,
          "license": "UNLICENSED",
          "scripts": {{
            "build": "nest build",
            "format": "prettier --write \\"src/**/*.ts\\" \\"test/**/*.ts\\"",
            "start": "nest start",
            "start:dev": "nest start --watch",
            "start:debug": "nest start --debug --watch",
            "start:prod": "node dist/main",
            "lint": "eslint \\"{{src,apps,libs,test}}/**/*.ts\\" --fix",
            "test": "jest",
            "test:watch": "jest --watch",
            "test:cov": "jest --coverage",
            "test:debug": "node --inspect-brk -r tsconfig-paths/register -r ts-node/register node_modules/.bin/jest --runInBand",
            "test:e2e": "jest --config ./test/jest-e2e.json",
            "db:generate": "drizzle-kit generate:pg",
            "db:push": "drizzle-kit push:pg",
            "db:studio": "drizzle-kit studio"
          }},
          "dependencies": {{
            {deps_str}
          }},
          "devDependencies": {{
            {dev_deps_str}
          }},
          "jest": {{
            "moduleFileExtensions": [
              "js",
              "json",
              "ts"
            ],
            "rootDir": "src",
            "testRegex": ".*\\\\.spec\\\\.ts$",
            "transform": {{
              "^.+\\\\.ts$": "ts-jest"
            }},
            "collectCoverageFrom": [
              "**/*.(t|j)s"
            ],
            "coverageDirectory": "../coverage",
            "testEnvironment": "node"
          }}
        }}
        """),
    )


def _create_env_example_template() -> FileTemplate:
    return FileTemplate(
        ".env.example",
        dedent("""
        # App
        NODE_ENV=development
        PORT=3000
        CORS_ORIGINS=*

        # Database (PostgreSQL)
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_platform
        
        # Redis
        REDIS_URL=redis://localhost:6379

        # LLM Providers
        # OpenAI
        OPENAI_API_KEY=sk-your-openai-key
        
        # Anthropic
        ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
        
        # Google Gemini
        GOOGLE_GENERATIVE_AI_API_KEY=your-google-key

        # Config
        DEFAULT_LLM_PROVIDER=openai

        # Monitoring (Sentry)
        SENTRY_DSN=
        """),
    )


def _create_gitignore_template() -> FileTemplate:
    return FileTemplate(
        ".gitignore",
        dedent("""
        # compiled output
        /dist
        /node_modules

        # logs
        logs
        *.log
        npm-debug.log*
        yarn-debug.log*
        yarn-error.log*
        lerna-debug.log*

        # OS
        .DS_Store

        # Tests
        /coverage
        /.nyc_output

        # IDEs and editors
        /.idea
        .project
        .classpath
        .c9/
        *.launch
        .settings/
        *.sublime-workspace

        # IDE - VSCode
        .vscode/*
        !.vscode/settings.json
        !.vscode/tasks.json
        !.vscode/launch.json
        !.vscode/extensions.json

        # dotenv
        .env
        .env.test
        .env.production
        """),
    )


def _create_dockerfile_template(package_manager: str) -> FileTemplate:
    """Multi-stage Dockerfile for Node.js."""
    install_cmd = "npm install"
    if package_manager == "pnpm":
        install_cmd = "npm install -g pnpm && pnpm install"
    elif package_manager == "yarn":
        install_cmd = "yarn install"

    build_cmd = "npm run build"
    if package_manager == "pnpm":
        build_cmd = "pnpm run build"
    elif package_manager == "yarn":
        build_cmd = "yarn build"

    prod_install_cmd = "npm ci --only=production"
    if package_manager == "pnpm":
        prod_install_cmd = "npm install -g pnpm && pnpm install --prod --frozen-lockfile"
    elif package_manager == "yarn":
        prod_install_cmd = "yarn install --production --frozen-lockfile"

    return FileTemplate(
        "Dockerfile",
        dedent(f"""
        # Stage 1: Builder
        FROM node:20-alpine AS builder

        WORKDIR /app

        COPY package*.json ./
        # Copiar lockfiles si existen
        COPY pnpm-lock.yaml* yarn.lock* ./

        RUN {install_cmd}

        COPY . .

        RUN {build_cmd}

        # Stage 2: Production
        FROM node:20-alpine

        WORKDIR /app

        ENV NODE_ENV=production

        COPY package*.json ./
        COPY pnpm-lock.yaml* yarn.lock* ./

        RUN {prod_install_cmd}

        COPY --from=builder /app/dist ./dist

        EXPOSE 3000

        CMD ["node", "dist/main"]
        """),
    )


def _create_docker_compose_template(project_name: str) -> FileTemplate:
    return FileTemplate(
        "docker-compose.yml",
        dedent(f"""
        services:
          api:
            build:
              context: .
              dockerfile: Dockerfile
            container_name: {project_name}-api
            restart: unless-stopped
            ports:
              - "3000:3000"
            environment:
              - DATABASE_URL=postgresql://postgres:postgres@db:5432/ai_platform
              - REDIS_URL=redis://redis:6379
              - NODE_ENV=development
            depends_on:
              - db
              - redis
            volumes:
              - .:/app
              - /app/node_modules

          db:
            image: postgres:15-alpine
            container_name: {project_name}-db
            restart: always
            environment:
              - POSTGRES_USER=postgres
              - POSTGRES_PASSWORD=postgres
              - POSTGRES_DB=ai_platform
            ports:
              - "5432:5432"
            volumes:
              - postgres_data:/var/lib/postgresql/data

          redis:
            image: redis:7-alpine
            container_name: {project_name}-redis
            restart: always
            ports:
              - "6379:6379"
            volumes:
              - redis_data:/data

        volumes:
          postgres_data:
          redis_data:
        """),
    )


def _create_github_workflow_template(package_manager: str) -> FileTemplate:
    install_cmd = "npm ci"
    if package_manager == "pnpm":
        install_cmd = "pnpm install --frozen-lockfile"
    elif package_manager == "yarn":
        install_cmd = "yarn install --frozen-lockfile"

    return FileTemplate(
        ".github/workflows/ci.yml",
        dedent(f"""
        name: CI

        on:
          push:
            branches: [ main ]
          pull_request:
            branches: [ main ]

        jobs:
          build:
            runs-on: ubuntu-latest

            steps:
            - uses: actions/checkout@v4

            - name: Use Node.js 20
              uses: actions/setup-node@v4
              with:
                node-version: '20'
                cache: '{package_manager if package_manager != "npm" else "npm"}'
            
            {"- name: Install pnpm\\n      uses: pnpm/action-setup@v2\\n      with:\\n        version: 8" if package_manager == "pnpm" else ""}

            - name: Install dependencies
              run: {install_cmd}

            - name: Lint
              run: {package_manager if package_manager != "npm" else "npm"} run lint

            - name: Test
              run: {package_manager if package_manager != "npm" else "npm"} run test

            - name: Build
              run: {package_manager if package_manager != "npm" else "npm"} run build
        """),
    )


def _create_monitoring_module_template() -> FileTemplate:
    return FileTemplate(
        "src/monitoring/monitoring.module.ts",
        dedent("""
        import { Module, Global } from '@nestjs/common';
        import { MetricsService } from './metrics.service';

        @Global()
        @Module({
          providers: [MetricsService],
          exports: [MetricsService],
        })
        export class MonitoringModule {}
        """),
    )


def _create_metrics_service_content() -> str:
    return dedent("""
    import { Injectable, Logger } from '@nestjs/common';

    @Injectable()
    export class MetricsService {
      private readonly logger = new Logger(MetricsService.name);

      /**
       * Placeholder for Sentry/Datadog integration.
       * Adapter Pattern would be useful here too.
       */
      trackEvent(eventName: string, properties: Record<string, any>) {
        this.logger.log(`[Metric] ${eventName}: ${JSON.stringify(properties)}`);
        // Implementation for real metrics provider
      }

      trackError(error: Error, context?: Record<string, any>) {
        this.logger.error(`[Error Metric] ${error.message}`, error.stack);
        // Sentry.captureException(error, { extra: context });
      }
    }
    """)


def _create_readme_template(project_name: str, package_manager: str) -> FileTemplate:
    run_cmd = "npm run"
    if package_manager == "pnpm":
        run_cmd = "pnpm"
    elif package_manager == "yarn":
        run_cmd = "yarn"

    return FileTemplate(
        "README.md",
        dedent(f"""
        # {project_name}

        Enterprise AI Agents Platform built with NestJS, following SOLID principles and Clean Architecture.

        ## 🚀 Stack

        - **Framework**: NestJS 10
        - **Language**: TypeScript 5
        - **Database**: PostgreSQL + Drizzle ORM
        - **AI**: Vercel AI SDK (Agnostic provider architecture)
        - **Providers**: OpenAI, Anthropic, Google Gemini
        - **Queues**: BullMQ (Redis)
        - **Validation**: Zod + Class Validator
        - **Docs**: Swagger / OpenAPI

        ## 🏗 Architecture

        ### Design Patterns
        - **Strategy**: `LLMProvider` interface allows switching between OpenAI, Anthropic, etc.
        - **Adapter**: Each AI provider has its own adapter class.
        - **Factory**: `ProviderFactory` instantiates the correct provider based on model configuration.
        - **Protected Variations**: The system is protected from API changes in specific LLM providers.
        - **Singleton**: Configuration and Database connections.

        ### Directory Structure
        ```
        src/
        ├── agents/           # AI Logic (The Core)
        │   ├── common/       # Interfaces and Registry
        │   ├── providers/    # LLM Adapters (OpenAI, Anthropic...)
        │   ├── chat/         # Chat business logic
        │   └── tools/        # Function calling tools
        ├── config/           # Environment config (Zod)
        ├── database/         # Drizzle setup & Schema
        └── monitoring/       # Metrics & Logging
        ```

        ## 🛠 Setup

        1. Install dependencies:
           ```bash
           {package_manager} install
           ```

        2. Setup Environment:
           ```bash
           cp .env.example .env
           # Edit .env with your API keys
           ```

        3. Start Infrastructure (DB + Redis):
           ```bash
           docker-compose up -d db redis
           ```

        4. Run Migrations:
           ```bash
           {run_cmd} db:push
           ```

        5. Start Server:
           ```bash
           {run_cmd} start:dev
           ```

        ## 📚 API Documentation

        Access Swagger UI at: http://localhost:3000/api/docs

        ### Example Endpoint
        **POST** `/api/v1/chat/message`
        ```json
        {{
          "model": "gpt-5.1",
          "messages": [
            {{ "role": "user", "content": "Hello, how are you?" }}
          ]
        }}
        ```
        """),
    )
