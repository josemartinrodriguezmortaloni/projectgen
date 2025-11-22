"""
Templates para archivos de configuración e infraestructura (TypeScript).
"""

import json

from generator.templates.base import FileTemplate
from generator.versions import (
    get_typescript_dependencies,
    get_typescript_dev_dependencies,
)


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
        FileTemplate("package.json", get_package_json(project_name, include_queue)),
        FileTemplate(".env.example", get_env_example()),
        FileTemplate("README.md", get_readme(project_name, package_manager)),
        FileTemplate(".gitignore", get_gitignore()),
        FileTemplate("src/monitoring/monitoring.module.ts", get_monitoring_module()),
        FileTemplate("src/monitoring/metrics.service.ts", get_metrics_service()),
    ]

    if include_docker:
        templates.extend(
            [
                FileTemplate("Dockerfile", get_dockerfile(package_manager)),
                FileTemplate("docker-compose.yml", get_docker_compose(project_name)),
            ]
        )

    if include_cicd:
        templates.append(
            FileTemplate(".github/workflows/ci.yml", get_github_workflow(package_manager))
        )

    if include_queue:
        templates.append(FileTemplate("src/queue/.gitkeep", ""))

    return templates


def get_package_json(project_name: str, include_queue: bool) -> str:
    """package.json with NestJS and AI dependencies using json.dumps()."""
    # Usar versiones centralizadas desde versions.py
    dependencies = get_typescript_dependencies(include_queue=include_queue)
    devDependencies = get_typescript_dev_dependencies()

    package_json = {
        "name": project_name,
        "version": "0.0.1",
        "description": "Enterprise AI Agents Platform",
        "author": "",
        "private": True,
        "license": "UNLICENSED",
        "scripts": {
            "build": "nest build",
            "format": 'prettier --write "src/**/*.ts" "test/**/*.ts"',
            "start": "nest start",
            "start:dev": "nest start --watch",
            "start:debug": "nest start --debug --watch",
            "start:prod": "node dist/main",
            "lint": 'eslint "{src,apps,libs,test}/**/*.ts" --fix',
            "test": "jest",
            "test:watch": "jest --watch",
            "test:cov": "jest --coverage",
            "test:debug": "node --inspect-brk -r tsconfig-paths/register -r ts-node/register node_modules/.bin/jest --runInBand",
            "test:e2e": "jest --config ./test/jest-e2e.json",
            "db:generate": "drizzle-kit generate:pg",
            "db:push": "drizzle-kit push:pg",
            "db:studio": "drizzle-kit studio",
        },
        "dependencies": dependencies,
        "devDependencies": devDependencies,
        "jest": {
            "moduleFileExtensions": ["js", "json", "ts"],
            "rootDir": "src",
            "testRegex": ".*\\.spec\\.ts$",
            "transform": {
                "^.+\\.ts$": "ts-jest",
            },
            "collectCoverageFrom": ["**/*.(t|j)s"],
            "coverageDirectory": "../coverage",
            "testEnvironment": "node",
        },
    }

    return json.dumps(package_json, indent=2).strip()


def get_env_example() -> str:
    return """
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
""".strip()


def get_gitignore() -> str:
    return """
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
""".strip()


def get_dockerfile(package_manager: str) -> str:
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

    return f"""
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
""".strip()


def get_docker_compose(project_name: str) -> str:
    return f"""
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
""".strip()


def get_github_workflow(package_manager: str) -> str:
    install_cmd = "npm ci"
    if package_manager == "pnpm":
        install_cmd = "pnpm install --frozen-lockfile"
    elif package_manager == "yarn":
        install_cmd = "yarn install --frozen-lockfile"

    pm_cmd = package_manager if package_manager != "npm" else "npm"

    pnpm_setup = ""
    if package_manager == "pnpm":
        pnpm_setup = """
    - name: Install pnpm
      uses: pnpm/action-setup@v2
      with:
        version: 8"""

    return f"""
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
        cache: '{pm_cmd}'{pnpm_setup}

    - name: Install dependencies
      run: {install_cmd}

    - name: Lint
      run: {pm_cmd} run lint

    - name: Test
      run: {pm_cmd} run test

    - name: Build
      run: {pm_cmd} run build
""".strip()


def get_monitoring_module() -> str:
    return """
import { Module, Global } from '@nestjs/common';
import { MetricsService } from './metrics.service';

@Global()
@Module({
  providers: [MetricsService],
  exports: [MetricsService],
})
export class MonitoringModule {}
""".strip()


def get_metrics_service() -> str:
    return """
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
""".strip()


def get_readme(project_name: str, package_manager: str) -> str:
    run_cmd = "npm run"
    if package_manager == "pnpm":
        run_cmd = "pnpm"
    elif package_manager == "yarn":
        run_cmd = "yarn"

    return f"""
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
- **Factory**: `ModelRegistry` instantiates AI SDK providers
- **Protected Variations**: The system is protected from API changes in specific LLM providers.
- **Singleton**: Configuration and Database connections.

### Directory Structure
```
src/
├── agents/           # AI Logic (The Core)
│   ├── common/       # Model Registry
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
""".strip()
