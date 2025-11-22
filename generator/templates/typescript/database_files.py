"""
Templates para la capa de persistencia con Drizzle ORM y Supabase (PostgreSQL).
"""

from generator.templates.base import FileTemplate


def get_database_templates(include_pgvector: bool) -> list[FileTemplate]:
    """
    Factory Method: Crea templates de base de datos.
    """
    return [
        FileTemplate("src/database/database.module.ts", get_database_module()),
        FileTemplate("src/database/schema.ts", get_schema(include_pgvector)),
        FileTemplate("drizzle.config.ts", get_drizzle_config()),
        # Placeholders
        FileTemplate("src/database/repositories/.gitkeep", ""),
        FileTemplate("src/database/migrations/.gitkeep", ""),
        FileTemplate("src/database/seeds/.gitkeep", ""),
    ]


def get_database_module() -> str:
    return """
import { Module, Global } from '@nestjs/common';
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';

import { env } from '../config/env';
import * as schema from './schema';

export const DRIZZLE_PROVIDER = 'DRIZZLE_PROVIDER';

@Global()
@Module({
  providers: [
    {
      provide: DRIZZLE_PROVIDER,
      // Factory (GoF): Crea la conexión de base de datos
      useFactory: () => {
        const client = postgres(env.DATABASE_URL, {
          max: 10,
          prepare: false,
        });
        return drizzle(client, { schema });
      },
    },
  ],
  exports: [DRIZZLE_PROVIDER],
})
export class DatabaseModule {}
""".strip()


def get_schema(include_pgvector: bool) -> str:
    vector_import = ""
    vector_column = ""

    if include_pgvector:
        vector_import = "import { vector } from 'drizzle-orm/pg-core';"
        vector_column = "embedding: vector('embedding', { dimensions: 1536 }),"

    return f"""
import {{ pgTable, serial, text, timestamp, uuid, boolean, jsonb }} from 'drizzle-orm/pg-core';
{vector_import}

/**
 * Schema Definition (Drizzle ORM)
 * Information Expert (GRASP): Define la estructura de los datos.
 */

export const users = pgTable('users', {{
  id: uuid('id').defaultRandom().primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  role: text('role', {{ enum: ['user', 'admin'] }}).default('user'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
}});

export const conversations = pgTable('conversations', {{
  id: uuid('id').defaultRandom().primaryKey(),
  userId: uuid('user_id').references(() => users.id).notNull(),
  title: text('title').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
}});

export const messages = pgTable('messages', {{
  id: uuid('id').defaultRandom().primaryKey(),
  conversationId: uuid('conversation_id').references(() => conversations.id).notNull(),
  role: text('role', {{ enum: ['user', 'assistant', 'system'] }}).notNull(),
  content: text('content').notNull(),
  tokenCount: serial('token_count'), // Using serial as integer placeholder
  metadata: jsonb('metadata'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
}});

// Ejemplo de tabla para RAG (Embeddings)
export const documents = pgTable('documents', {{
  id: uuid('id').defaultRandom().primaryKey(),
  content: text('content').notNull(),
  metadata: jsonb('metadata'),
  {vector_column}
  createdAt: timestamp('created_at').defaultNow().notNull(),
}});
""".strip()


def get_drizzle_config() -> str:
    return """
import { defineConfig } from 'drizzle-kit';

// No podemos importar env.ts aquí porque Drizzle Kit no usa ts-node runtime completo a veces
// Así que usamos process.env directo o dotenv si es necesario
import 'dotenv/config';

export default defineConfig({
  schema: './src/database/schema.ts',
  out: './src/database/migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
  verbose: true,
  strict: true,
});
""".strip()
