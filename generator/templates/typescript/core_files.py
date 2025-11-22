"""
Templates para el núcleo de la aplicación NestJS (TypeScript).
Incluye configuración, bootstrapping y módulos principales.
"""

from generator.templates.base import FileTemplate, dedent


def get_core_templates(project_name: str) -> list[FileTemplate]:
    """
    Factory Method: Crea templates del core de NestJS.
    """
    return [
        _create_main_ts_template(),
        _create_app_module_template(),
        _create_env_config_template(),
        _create_tsconfig_template(),
        _create_nest_cli_template(),
        _create_eslintrc_template(),
        _create_prettierrc_template(),
        # Estructura de directorios base (vacíos con gitkeep)
        FileTemplate("src/common/decorators/.gitkeep", ""),
        FileTemplate("src/common/filters/.gitkeep", ""),
        FileTemplate("src/common/guards/.gitkeep", ""),
        FileTemplate("src/common/interceptors/.gitkeep", ""),
        FileTemplate("src/common/middleware/.gitkeep", ""),
        FileTemplate("src/common/pipes/.gitkeep", ""),
        FileTemplate("src/utils/.gitkeep", ""),
    ]


def _create_main_ts_template() -> FileTemplate:
    """src/main.ts: Entry point con configuración robusta."""
    return FileTemplate(
        "src/main.ts",
        dedent("""
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
        """),
    )


def _create_app_module_template() -> FileTemplate:
    """src/app.module.ts: Root module."""
    return FileTemplate(
        "src/app.module.ts",
        dedent("""
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
        """),
    )


def _create_env_config_template() -> FileTemplate:
    """src/config/env.ts: Type-safe environment variables with Zod."""
    return FileTemplate(
        "src/config/env.ts",
        dedent("""
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
        """),
    )


def _create_tsconfig_template() -> FileTemplate:
    """tsconfig.json: Strict TypeScript configuration."""
    return FileTemplate(
        "tsconfig.json",
        dedent("""
        {
          "compilerOptions": {
            "module": "commonjs",
            "declaration": true,
            "removeComments": true,
            "emitDecoratorMetadata": true,
            "experimentalDecorators": true,
            "allowSyntheticDefaultImports": true,
            "target": "ES2021",
            "sourceMap": true,
            "outDir": "./dist",
            "baseUrl": "./",
            "incremental": true,
            "skipLibCheck": true,
            "strictNullChecks": true,
            "noImplicitAny": false,
            "strictBindCallApply": false,
            "forceConsistentCasingInFileNames": false,
            "noFallthroughCasesInSwitch": false,
            "resolveJsonModule": true
          }
        }
        """),
    )


def _create_nest_cli_template() -> FileTemplate:
    """nest-cli.json configuration."""
    return FileTemplate(
        "nest-cli.json",
        dedent("""
        {
          "$schema": "https://json.schemastore.org/nest-cli",
          "collection": "@nestjs/schematics",
          "sourceRoot": "src",
          "compilerOptions": {
            "deleteOutDir": true
          }
        }
        """),
    )


def _create_eslintrc_template() -> FileTemplate:
    """.eslintrc.js: Linter configuration."""
    return FileTemplate(
        ".eslintrc.js",
        dedent("""
        module.exports = {
          parser: '@typescript-eslint/parser',
          parserOptions: {
            project: 'tsconfig.json',
            tsconfigRootDir: __dirname,
            sourceType: 'module',
          },
          plugins: ['@typescript-eslint/eslint-plugin', 'import'],
          extends: [
            'plugin:@typescript-eslint/recommended',
            'plugin:prettier/recommended',
          ],
          root: true,
          env: {
            node: true,
            jest: true,
          },
          ignorePatterns: ['.eslintrc.js'],
          rules: {
            '@typescript-eslint/interface-name-prefix': 'off',
            '@typescript-eslint/explicit-function-return-type': 'off',
            '@typescript-eslint/explicit-module-boundary-types': 'off',
            '@typescript-eslint/no-explicit-any': 'off',
            'import/order': [
              'error',
              {
                'groups': ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
                'newlines-between': 'always',
                'alphabetize': { 'order': 'asc', 'caseInsensitive': true }
              }
            ]
          },
        };
        """),
    )


def _create_prettierrc_template() -> FileTemplate:
    """.prettierrc: Formatter configuration."""
    return FileTemplate(
        ".prettierrc",
        dedent("""
        {
          "singleQuote": true,
          "trailingComma": "all",
          "printWidth": 100,
          "tabWidth": 2,
          "semi": true,
          "endOfLine": "lf"
        }
        """),
    )

