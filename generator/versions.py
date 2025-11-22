"""
Centralización de versiones de dependencias (Python y TypeScript).

Single Source of Truth (SSOT) para todas las versiones de paquetes.
Facilita actualizaciones y mantiene consistencia entre proyectos generados.

Patrón: Protected Variations (GRASP) - Protege el sistema de cambios en versiones.
"""

# ==================== TypeScript / NestJS Versions ====================

# Core NestJS
NESTJS_VERSION = "^10.0.0"
NESTJS_CORE_VERSION = "^10.0.0"
NESTJS_CONFIG_VERSION = "^3.2.0"
NESTJS_PLATFORM_EXPRESS_VERSION = "^10.0.0"
NESTJS_SWAGGER_VERSION = "^7.3.0"
NESTJS_THROTTLER_VERSION = "^5.1.2"

# NestJS Dev
NESTJS_CLI_VERSION = "^10.0.0"
NESTJS_SCHEMATICS_VERSION = "^10.0.0"
NESTJS_TESTING_VERSION = "^10.0.0"

# AI SDK
AI_SDK_VERSION = "^3.0.13"
AI_SDK_OPENAI_VERSION = "^0.0.14"
AI_SDK_ANTHROPIC_VERSION = "^0.0.15"
AI_SDK_GOOGLE_VERSION = "^0.0.13"

# Database
DRIZZLE_ORM_VERSION = "^0.30.4"
POSTGRES_VERSION = "^3.4.4"
DRIZZLE_KIT_VERSION = "^0.20.14"

# Validation & Config
ZOD_VERSION = "^3.22.4"
T3_ENV_CORE_VERSION = "^0.9.2"
CLASS_TRANSFORMER_VERSION = "^0.5.1"
CLASS_VALIDATOR_VERSION = "^0.14.1"

# Security & Middleware
HELMET_VERSION = "^7.1.0"
COMPRESSION_VERSION = "^1.7.4"

# Linting & Formatting
ESLINT_VERSION = "^9.17.0"
TYPESCRIPT_ESLINT_VERSION = "^8.20.0"
ESLINT_JS_VERSION = "^9.17.0"
ESLINT_CONFIG_PRETTIER_VERSION = "^9.1.0"
ESLINT_PLUGIN_PRETTIER_VERSION = "^6.0.0"
ESLINT_PLUGIN_IMPORT_VERSION = "^2.31.0"
PRETTIER_VERSION = "^3.4.2"

# Testing
JEST_VERSION = "^29.7.0"
SUPERTEST_VERSION = "^7.1.3"
TS_JEST_VERSION = "^29.1.0"

# TypeScript
TYPESCRIPT_VERSION = "^5.1.3"
TS_NODE_VERSION = "^10.9.1"
TS_LOADER_VERSION = "^9.4.3"
TSCONFIG_PATHS_VERSION = "^4.2.0"

# Type Definitions
TYPES_EXPRESS_VERSION = "^4.17.17"
TYPES_JEST_VERSION = "^29.5.2"
TYPES_NODE_VERSION = "^20.3.1"
TYPES_SUPERTEST_VERSION = "^6.0.0"

# Queue (BullMQ) - Optional
NESTJS_BULLMQ_VERSION = "^10.1.0"
BULLMQ_VERSION = "^5.4.1"

# Other
REFLECT_METADATA_VERSION = "^0.2.0"
RXJS_VERSION = "^7.8.1"
NESTJS_MAPPED_TYPES_VERSION = "*"
SOURCE_MAP_SUPPORT_VERSION = "^0.5.21"
DOTENV_VERSION = "^16.4.5"

# ==================== Python / FastAPI Versions ====================

FASTAPI_VERSION = "^0.115.0"
UVICORN_VERSION = "^0.32.0"
PYDANTIC_VERSION = "^2.9.0"
PYDANTIC_SETTINGS_VERSION = "^2.5.0"

# Database
SQLALCHEMY_VERSION = "^2.0.35"
ALEMBIC_VERSION = "^1.14.0"
PSYCOPG2_BINARY_VERSION = "^2.9.10"

# Auth & Security
PYJWT_VERSION = "^2.9.0"
PASSLIB_VERSION = "^1.7.4"
BCRYPT_VERSION = "^4.2.0"
ARGON2_CFFI_VERSION = "^23.1.0"

# Validation
EMAIL_VALIDATOR_VERSION = "^2.2.0"

# Monitoring & Logging
SENTRY_SDK_VERSION = "^2.20.0"

# ==================== TypeScript Dependencies Dict ====================


def get_typescript_dependencies(include_queue: bool = False) -> dict[str, str]:
    """
    Retorna diccionario de dependencias TypeScript.

    Args:
        include_queue: Si incluir dependencias de BullMQ

    Returns:
        Dict con nombre de paquete y versión
    """
    deps = {
        "@nestjs/common": NESTJS_VERSION,
        "@nestjs/core": NESTJS_CORE_VERSION,
        "@nestjs/config": NESTJS_CONFIG_VERSION,
        "@nestjs/platform-express": NESTJS_PLATFORM_EXPRESS_VERSION,
        "@nestjs/swagger": NESTJS_SWAGGER_VERSION,
        "@nestjs/throttler": NESTJS_THROTTLER_VERSION,
        "reflect-metadata": REFLECT_METADATA_VERSION,
        "rxjs": RXJS_VERSION,
        "class-transformer": CLASS_TRANSFORMER_VERSION,
        "class-validator": CLASS_VALIDATOR_VERSION,
        "helmet": HELMET_VERSION,
        "compression": COMPRESSION_VERSION,
        "zod": ZOD_VERSION,
        "@t3-oss/env-core": T3_ENV_CORE_VERSION,
        # AI SDKs
        "ai": AI_SDK_VERSION,
        "@ai-sdk/openai": AI_SDK_OPENAI_VERSION,
        "@ai-sdk/anthropic": AI_SDK_ANTHROPIC_VERSION,
        "@ai-sdk/google": AI_SDK_GOOGLE_VERSION,
        # Database
        "drizzle-orm": DRIZZLE_ORM_VERSION,
        "postgres": POSTGRES_VERSION,
        "@nestjs/mapped-types": NESTJS_MAPPED_TYPES_VERSION,
    }

    if include_queue:
        deps["@nestjs/bullmq"] = NESTJS_BULLMQ_VERSION
        deps["bullmq"] = BULLMQ_VERSION

    return deps


def get_typescript_dev_dependencies() -> dict[str, str]:
    """
    Retorna diccionario de dependencias de desarrollo TypeScript.

    Returns:
        Dict con nombre de paquete y versión
    """
    return {
        "@nestjs/cli": NESTJS_CLI_VERSION,
        "@nestjs/schematics": NESTJS_SCHEMATICS_VERSION,
        "@nestjs/testing": NESTJS_TESTING_VERSION,
        "@types/express": TYPES_EXPRESS_VERSION,
        "@types/jest": TYPES_JEST_VERSION,
        "@types/node": TYPES_NODE_VERSION,
        "@types/supertest": TYPES_SUPERTEST_VERSION,
        "@eslint/js": ESLINT_JS_VERSION,
        "typescript-eslint": TYPESCRIPT_ESLINT_VERSION,
        "eslint": ESLINT_VERSION,
        "eslint-config-prettier": ESLINT_CONFIG_PRETTIER_VERSION,
        "eslint-plugin-prettier": ESLINT_PLUGIN_PRETTIER_VERSION,
        "eslint-plugin-import": ESLINT_PLUGIN_IMPORT_VERSION,
        "jest": JEST_VERSION,
        "prettier": PRETTIER_VERSION,
        "source-map-support": SOURCE_MAP_SUPPORT_VERSION,
        "supertest": SUPERTEST_VERSION,
        "ts-jest": TS_JEST_VERSION,
        "ts-loader": TS_LOADER_VERSION,
        "ts-node": TS_NODE_VERSION,
        "tsconfig-paths": TSCONFIG_PATHS_VERSION,
        "typescript": TYPESCRIPT_VERSION,
        "drizzle-kit": DRIZZLE_KIT_VERSION,
        "dotenv": DOTENV_VERSION,
    }


# ==================== Model Registry Configuration ====================

AVAILABLE_MODELS = {
    "gpt-5.1": {
        "provider": "openai",
        "context": 128000,
        "model_id": "gpt-5.1",
    },
    "claude-sonnet-4.5": {
        "provider": "anthropic",
        "context": 200000,
        "model_id": "claude-sonnet-4.5",
    },
    "claude-opus-4.1": {
        "provider": "anthropic",
        "context": 200000,
        "model_id": "claude-opus-4.1",
    },
    "gemini-3": {
        "provider": "google",
        "context": 1000000,
        "model_id": "gemini-3-ultra",
    },
}

# Modelos futuros (para extensibilidad)
FUTURE_MODELS = {
    "llama-3.3-70b": {
        "provider": "groq",
        "context": 128000,
        "model_id": "llama-3.3-70b",
        "note": "Requiere @ai-sdk/groq package",
    },
    "deepseek-v3": {
        "provider": "deepseek",
        "context": 64000,
        "model_id": "deepseek-v3",
        "note": "Requiere @ai-sdk/deepseek package",
    },
}
