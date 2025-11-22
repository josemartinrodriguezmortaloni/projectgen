"""
Templates para el núcleo de la aplicación NestJS (TypeScript).
Incluye configuración, bootstrapping y módulos principales.
"""

import json

from generator.templates.base import FileTemplate


def get_core_templates(_project_name: str) -> list[FileTemplate]:
    """
    Factory Method: Crea templates del core de NestJS.
    """
    return [
        FileTemplate("src/main.ts", get_main_ts()),
        FileTemplate("src/app.module.ts", get_app_module()),
        FileTemplate("src/config/env.ts", get_env_config()),
        FileTemplate("tsconfig.json", get_tsconfig()),
        FileTemplate("nest-cli.json", get_nest_cli()),
        FileTemplate("eslint.config.mjs", get_eslint_config()),
        FileTemplate(".prettierrc", get_prettierrc()),
        # Estructura de directorios base (vacíos con gitkeep)
        FileTemplate("src/common/decorators/.gitkeep", ""),
        FileTemplate("src/common/filters/.gitkeep", ""),
        FileTemplate("src/common/guards/.gitkeep", ""),
        FileTemplate("src/common/interceptors/.gitkeep", ""),
        FileTemplate("src/common/middleware/.gitkeep", ""),
        FileTemplate("src/common/pipes/.gitkeep", ""),
        FileTemplate("src/utils/.gitkeep", ""),
    ]


def get_main_ts() -> str:
    return """
import { ValidationPipe, Logger } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import helmet from 'helmet';
import compression from 'compression';

import { AppModule } from './app.module';
import { env } from './config/env';

async function bootstrap() {
  const logger = new Logger('Bootstrap');
  
  // Factory Method (GoF): NestFactory crea la instancia de la aplicación
  const app = await NestFactory.create(AppModule);

  // Configuración de Seguridad (Helmet)
  app.use(helmet());
  
  // Compresión Gzip
  app.use(compression());

  // CORS
  app.enableCors({
    origin: env.CORS_ORIGINS,
    credentials: true,
  });

  // Validation Pipe Global
  // Single Responsibility (SOLID): Validación separada de controladores
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // Elimina propiedades no decoradas
      forbidNonWhitelisted: true, // Error si hay propiedades extra
      transform: true, // Transforma payloads a tipos DTO
      transformOptions: {
        enableImplicitConversion: true,
      },
    }),
  );

  // Configuración Swagger (OpenAPI)
  if (env.NODE_ENV !== 'production') {
    const config = new DocumentBuilder()
      .setTitle('AI Agents Platform API')
      .setDescription('Enterprise grade AI Agents platform with NestJS')
      .setVersion('1.0')
      .addBearerAuth()
      .build();
      
    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup('api/docs', app, document);
    logger.log('Swagger documentation running at /api/docs');
  }

  // Prefijo global para API
  app.setGlobalPrefix('api/v1');

  const port = env.PORT || 3000;
  await app.listen(port);
  
  logger.log(`Application is running on: ${await app.getUrl()}`);
  logger.log(`Environment: ${env.NODE_ENV}`);
}

// Bootstrap con manejo de errores
bootstrap().catch((err) => {
  console.error('Fatal error during bootstrap:', err);
  process.exit(1);
});
""".strip()


def get_app_module() -> str:
    return """
import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
        
import { AgentsModule } from './agents/agents.module';
import { DatabaseModule } from './database/database.module';
import { MonitoringModule } from './monitoring/monitoring.module';

@Module({
  imports: [
    // Configuración Global
    // Singleton (GoF): ConfigModule provee configuración única
    ConfigModule.forRoot({
      isGlobal: true,
      cache: true,
      // Validación vía env.ts (Zod) en lugar de Joi aquí
    }),

    // Módulos de Infraestructura
    DatabaseModule,
    MonitoringModule,

    // Módulos de Dominio (Feature Modules)
    // High Cohesion (GRASP): Lógica de agentes agrupada
    AgentsModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}
""".strip()


def get_env_config() -> str:
    return """
import { createEnv } from '@t3-oss/env-core';
import { z } from 'zod';

// Protected Variations (GRASP): Protege el sistema de variables de entorno inválidas
// Singleton (GoF): Provee acceso único y validado a la config
export const env = createEnv({
  server: {
    // App
    NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
    PORT: z.coerce.number().default(3000),
    CORS_ORIGINS: z.string().transform((s) => s.split(',')).default('*'),

    // Database (Supabase/Postgres)
    DATABASE_URL: z.string().url(),

    // Redis
    REDIS_URL: z.string().url().optional(),

    // LLM Providers (Protected Variations for API Keys)
    OPENAI_API_KEY: z.string().min(1).optional(),
    ANTHROPIC_API_KEY: z.string().min(1).optional(),
    GOOGLE_GENERATIVE_AI_API_KEY: z.string().min(1).optional(),
    
    // Config
    DEFAULT_LLM_PROVIDER: z.enum(['openai', 'anthropic', 'google']).default('openai'),
    
    // Monitoring
    SENTRY_DSN: z.string().url().optional(),
  },
  runtimeEnv: process.env,
  emptyStringAsUndefined: true,
});
""".strip()


def get_tsconfig() -> str:
    config = {
        "compilerOptions": {
            "module": "commonjs",
            "declaration": True,
            "removeComments": True,
            "emitDecoratorMetadata": True,
            "experimentalDecorators": True,
            "allowSyntheticDefaultImports": True,
            "target": "ES2021",
            "sourceMap": True,
            "outDir": "./dist",
            "baseUrl": "./",
            "incremental": True,
            "skipLibCheck": True,
            "strictNullChecks": True,
            "noImplicitAny": False,
            "strictBindCallApply": False,
            "forceConsistentCasingInFileNames": False,
            "noFallthroughCasesInSwitch": False,
            "resolveJsonModule": True,
        },
    }
    return json.dumps(config, indent=2).strip()


def get_nest_cli() -> str:
    config = {
        "$schema": "https://json.schemastore.org/nest-cli",
        "collection": "@nestjs/schematics",
        "sourceRoot": "src",
        "compilerOptions": {
            "deleteOutDir": True,
        },
    }
    return json.dumps(config, indent=2).strip()


def get_eslint_config() -> str:
    return """
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import prettier from 'eslint-config-prettier';
import importPlugin from 'eslint-plugin-import';
import prettierPlugin from 'eslint-plugin-prettier';

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  prettier,
  {
    ignores: ['dist/**', 'node_modules/**', 'coverage/**', '*.config.js', '*.config.mjs'],
  },
  {
    files: ['**/*.ts'],
    plugins: {
      import: importPlugin,
      prettier: prettierPlugin,
    },
    languageOptions: {
      globals: {
        NodeJS: 'readonly',
        jest: 'readonly',
      },
    },
    rules: {
      '@typescript-eslint/interface-name-prefix': 'off',
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      'prettier/prettier': 'error',
      'import/order': [
        'error',
        {
          groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
          'newlines-between': 'always',
          alphabetize: { order: 'asc', caseInsensitive: true },
        },
      ],
    },
  },
);
""".strip()


def get_prettierrc() -> str:
    config = {
        "singleQuote": True,
        "trailingComma": "all",
        "printWidth": 100,
        "tabWidth": 2,
        "semi": True,
        "endOfLine": "lf",
    }
    return json.dumps(config, indent=2).strip()
