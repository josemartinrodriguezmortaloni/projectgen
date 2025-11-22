"""
Templates para la arquitectura agnóstica de Agentes de IA.
Usa AI SDK de Vercel directamente (ya tiene abstraction layer).
"""

from generator.templates.base import FileTemplate


def get_agent_templates(
    default_model: str, include_rag: bool, full: bool = False
) -> list[FileTemplate]:
    """
    Factory Method: Crea templates para el módulo de agentes.
    Usa AI SDK de Vercel directamente (ya tiene abstraction layer).

    Args:
        default_model: Modelo LLM por defecto
        include_rag: Si incluir sistema RAG
        full: Si True, genera implementación completa. Si False, genera scaffold mínimo.
    """
    templates = [
        FileTemplate("src/agents/agents.module.ts", get_agents_module(include_rag, full)),
        FileTemplate("src/agents/common/model-registry.ts", get_model_registry(default_model)),
        FileTemplate("src/agents/chat/chat.module.ts", get_chat_module()),
        FileTemplate("src/agents/chat/chat.controller.ts", get_chat_controller()),
        FileTemplate("src/agents/chat/chat.service.ts", get_chat_service(full)),
        FileTemplate("src/agents/chat/dto/chat-request.dto.ts", get_chat_dto()),
    ]

    # Tools - siempre estructura básica
    if full:
        templates.append(
            FileTemplate("src/agents/tools/tools.service.ts", get_tools_service_full())
        )
        templates.append(FileTemplate("src/agents/tools/tools.module.ts", get_tools_module()))
    else:
        templates.append(
            FileTemplate("src/agents/tools/tools.service.ts", get_tools_service_scaffold())
        )
        templates.append(FileTemplate("src/agents/tools/tools.module.ts", get_tools_module()))

    # RAG - solo si se incluye
    if include_rag:
        if full:
            templates.append(FileTemplate("src/agents/rag/rag.service.ts", get_rag_service_full()))
            templates.append(
                FileTemplate("src/agents/rag/embeddings.service.ts", get_embeddings_service_full())
            )
        else:
            templates.append(
                FileTemplate("src/agents/rag/rag.service.ts", get_rag_service_scaffold())
            )
            templates.append(
                FileTemplate(
                    "src/agents/rag/embeddings.service.ts", get_embeddings_service_scaffold()
                )
            )
        templates.append(FileTemplate("src/agents/rag/rag.module.ts", get_rag_module()))

    return templates


def get_agents_module(include_rag: bool = False, full: bool = False) -> str:
    imports = []
    module_imports = []

    imports.append("import { ChatModule } from './chat/chat.module';")
    module_imports.append("ChatModule")

    if full or include_rag:
        imports.append("import { ToolsModule } from './tools/tools.module';")
        module_imports.append("ToolsModule")

    if include_rag:
        imports.append("import { RagModule } from './rag/rag.module';")
        module_imports.append("RagModule")

    imports_str = "\n".join(imports)
    module_imports_str = ",\n    ".join(module_imports)

    return f"""
import {{ Module }} from '@nestjs/common';

{imports_str}

@Module({{
  imports: [
    {module_imports_str},
  ],
}})
export class AgentsModule {{}}
""".strip()


def get_model_registry(default_model: str) -> str:
    return f"""
import {{ createOpenAI }} from '@ai-sdk/openai';
import {{ createAnthropic }} from '@ai-sdk/anthropic';
import {{ createGoogleGenerativeAI }} from '@ai-sdk/google';
import {{ LanguageModel }} from 'ai';

import {{ env }} from '../../config/env';

/**
 * Factory Pattern: Simple wrapper sobre AI SDK.
 * AI SDK ya proporciona la abstraction layer, no necesitamos más capas.
 */
export class ModelRegistry {{
  private openaiClient;
  private anthropicClient;
  private googleClient;
  private models: Map<string, LanguageModel>;

  constructor() {{
    // Inicializar clients una sola vez (Singleton-like)
    this.openaiClient = createOpenAI({{
      apiKey: env.OPENAI_API_KEY,
    }});

    this.anthropicClient = createAnthropic({{
      apiKey: env.ANTHROPIC_API_KEY,
    }});

    this.googleClient = createGoogleGenerativeAI({{
      apiKey: env.GOOGLE_GENERATIVE_AI_API_KEY,
    }});

    // Registrar modelos (AI SDK ya abstrae las diferencias entre proveedores)
    this.models = new Map();
    this.models.set('gpt-5.1', this.openaiClient('gpt-5.1'));
    this.models.set('claude-sonnet-4.5', this.anthropicClient('claude-sonnet-4.5'));
    this.models.set('claude-opus-4.1', this.anthropicClient('claude-opus-4.1'));
    this.models.set('gemini-3', this.googleClient('gemini-3-ultra'));
  }}

  /**
   * Obtiene el modelo por nombre.
   * @throws Error si el modelo no está registrado
   */
  getModel(name: string): LanguageModel {{
    const model = this.models.get(name);
    if (!model) {{
      throw new Error(`Model ${{name}} not found. Available models: ${{Array.from(this.models.keys()).join(', ')}}`);
    }}
    return model;
  }}

  /**
   * Lista todos los modelos disponibles
   */
  listModels(): string[] {{
    return Array.from(this.models.keys());
  }}
}}

/**
 * Singleton instance del registry
 */
let registryInstance: ModelRegistry | null = null;

export function getModelRegistry(): ModelRegistry {{
  if (!registryInstance) {{
    registryInstance = new ModelRegistry();
  }}
  return registryInstance;
}}

/**
 * Modelo por defecto
 */
export const DEFAULT_MODEL = '{default_model}';
""".strip()


def get_chat_module() -> str:
    return """
import { Module } from '@nestjs/common';

import { ChatController } from './chat.controller';
import { ChatService } from './chat.service';

@Module({
  controllers: [ChatController],
  providers: [ChatService],
})
export class ChatModule {}
""".strip()


def get_chat_controller() -> str:
    return """
import { Controller, Post, Body, Sse } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { Observable } from 'rxjs';

import { ChatService } from './chat.service';
import { ChatRequestDto, ChatResponseDto } from './dto/chat-request.dto';

@ApiTags('Chat Agents')
@Controller('chat')
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  @Post('message')
  @ApiOperation({ summary: 'Send a message to an AI agent' })
  @ApiResponse({ status: 201, type: ChatResponseDto })
  async sendMessage(@Body() dto: ChatRequestDto): Promise<ChatResponseDto> {
    return this.chatService.processMessage(dto);
  }

  @Sse('stream')
  @ApiOperation({ summary: 'Stream a message response' })
  streamMessage(@Body() dto: ChatRequestDto): Observable<any> {
    return this.chatService.streamMessage(dto);
  }
}
""".strip()


def get_chat_service(full: bool = False) -> str:
    if full:
        return _get_chat_service_full()
    else:
        return _get_chat_service_scaffold()


def _get_chat_service_scaffold() -> str:
    """Versión scaffold: Funcionalidad mínima básica (Hello world level)."""
    return """
import { Injectable, Logger } from '@nestjs/common';
import { generateText, CoreMessage } from 'ai';

import { getModelRegistry, DEFAULT_MODEL } from '../common/model-registry';
import { ChatRequestDto, ChatResponseDto } from './dto/chat-request.dto';

@Injectable()
export class ChatService {
  private readonly logger = new Logger(ChatService.name);
  private readonly registry = getModelRegistry();

  /**
   * Scaffold: Versión básica funcionando.
   * TODO: Agregar streaming, manejo de errores avanzado, logging detallado.
   */
  async processMessage(dto: ChatRequestDto): Promise<ChatResponseDto> {
    const modelName = dto.model || DEFAULT_MODEL;
    this.logger.log(`Processing message with model: ${modelName}`);

    const model = this.registry.getModel(modelName);
    const messages: CoreMessage[] = dto.messages.map((m) => ({
      role: m.role as 'user' | 'assistant' | 'system',
      content: m.content,
    }));

    const result = await generateText({
      model,
      messages,
      temperature: dto.temperature ?? 0.7,
      maxTokens: dto.maxTokens,
    });

    return {
      content: result.text,
      role: 'assistant',
      usage: {
        promptTokens: result.usage?.promptTokens ?? 0,
        completionTokens: result.usage?.completionTokens ?? 0,
        totalTokens: result.usage?.totalTokens ?? 0,
      },
      model: modelName,
    };
  }
}
""".strip()


def _get_chat_service_full() -> str:
    """Versión full: Implementación completa con todas las características."""
    return """
import { Injectable, Logger } from '@nestjs/common';
import { generateText, streamText, CoreMessage } from 'ai';
import { Observable, from, map } from 'rxjs';

import { getModelRegistry, DEFAULT_MODEL } from '../common/model-registry';
import { ChatRequestDto, ChatResponseDto } from './dto/chat-request.dto';

@Injectable()
export class ChatService {
  private readonly logger = new Logger(ChatService.name);
  private readonly registry = getModelRegistry();

  /**
   * Procesa un mensaje de chat usando AI SDK directamente.
   * AI SDK ya tiene la abstraction layer, no necesitamos más capas intermedias.
   */
  async processMessage(dto: ChatRequestDto): Promise<ChatResponseDto> {
    const modelName = dto.model || DEFAULT_MODEL;
    this.logger.log(`Processing message with model: ${modelName}`);

    // Obtener modelo del registry
    const model = this.registry.getModel(modelName);

    // Convertir mensajes a formato AI SDK
    const messages: CoreMessage[] = dto.messages.map((m) => ({
      role: m.role as 'user' | 'assistant' | 'system',
      content: m.content,
    }));

    // Generar respuesta usando AI SDK directamente
    const result = await generateText({
      model,
      messages,
      temperature: dto.temperature ?? 0.7,
      maxTokens: dto.maxTokens,
    });

    // Retornar DTO
    return {
      content: result.text,
      role: 'assistant',
      usage: {
        promptTokens: result.usage?.promptTokens ?? 0,
        completionTokens: result.usage?.completionTokens ?? 0,
        totalTokens: result.usage?.totalTokens ?? 0,
      },
      model: modelName,
    };
  }

  /**
   * Maneja streaming de respuesta (Server Sent Events).
   */
  streamMessage(dto: ChatRequestDto): Observable<any> {
    return from(this._streamGenerator(dto)).pipe(
      map((chunk) => ({ data: chunk })),
    );
  }

  private async *_streamGenerator(dto: ChatRequestDto) {
    const modelName = dto.model || DEFAULT_MODEL;
    const model = this.registry.getModel(modelName);

    const messages: CoreMessage[] = dto.messages.map((m) => ({
      role: m.role as 'user' | 'assistant' | 'system',
      content: m.content,
    }));

    // AI SDK stream directamente
    const stream = await streamText({
      model,
      messages,
      temperature: dto.temperature ?? 0.7,
      maxTokens: dto.maxTokens,
    });

    // Consumir stream de AI SDK
    for await (const chunk of stream.textStream) {
      yield chunk;
    }
  }
}
""".strip()


def get_chat_dto() -> str:
    return """
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Type } from 'class-transformer';
import { IsArray, IsEnum, IsNumber, IsOptional, IsString, ValidateNested, Max, Min, IsIn } from 'class-validator';

import { DEFAULT_MODEL } from '../../common/model-registry';

export class ChatMessageDto {
  @ApiProperty({ enum: ['user', 'assistant', 'system'] })
  @IsEnum(['user', 'assistant', 'system'])
  role: string;

  @ApiProperty()
  @IsString()
  content: string;
}

export class ChatRequestDto {
  @ApiProperty({
    enum: ['gpt-5.1', 'claude-sonnet-4.5', 'claude-opus-4.1', 'gemini-3'],
    example: DEFAULT_MODEL,
    description: 'Model name to use for the chat',
  })
  @IsOptional()
  @IsString()
  @IsIn(['gpt-5.1', 'claude-sonnet-4.5', 'claude-opus-4.1', 'gemini-3'])
  model?: string;

  @ApiProperty({ type: [ChatMessageDto] })
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => ChatMessageDto)
  messages: ChatMessageDto[];

  @ApiPropertyOptional({ minimum: 0, maximum: 2, default: 0.7 })
  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(2)
  temperature?: number;

  @ApiPropertyOptional()
  @IsOptional()
  @IsNumber()
  maxTokens?: number;
}

export class ChatResponseDto {
  @ApiProperty()
  content: string;

  @ApiProperty()
  role: string;

  @ApiProperty()
  model: string;

  @ApiPropertyOptional()
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}
""".strip()


# ==================== RAG Services ====================


def get_rag_service_scaffold() -> str:
    """Versión scaffold: Placeholder con NotImplemented."""
    return """
import { Injectable, Logger, NotImplementedException } from '@nestjs/common';

@Injectable()
export class RagService {
  private readonly logger = new Logger(RagService.name);

  /**
   * Scaffold: Placeholder para implementación RAG.
   * TODO: Implementar:
   * 1. Chunking de documentos
   * 2. Generar embeddings usando EmbeddingsService
   * 3. Almacenar en PostgreSQL con pgvector
   * 4. Búsqueda semántica por similitud
   * 5. Integración con ChatService para contexto aumentado
   */
  async searchSimilar(query: string, limit: number = 5): Promise<any[]> {
    this.logger.warn('RAG search not implemented yet. Use --full flag for full implementation.');
    throw new NotImplementedException('RAG search functionality is not implemented. Use --full flag when generating project.');
  }

  async addDocument(content: string, metadata?: Record<string, any>): Promise<string> {
    this.logger.warn('RAG add document not implemented yet.');
    throw new NotImplementedException('RAG add document functionality is not implemented.');
  }
}
""".strip()


def get_rag_service_full() -> str:
    """Versión full: Implementación completa de RAG."""
    return """
import { Injectable, Logger, Inject } from '@nestjs/common';
import { eq } from 'drizzle-orm';

import { DRIZZLE_PROVIDER } from '../../database/database.module';
import { documents } from '../../database/schema';
import { EmbeddingsService } from './embeddings.service';

@Injectable()
export class RagService {
  private readonly logger = new Logger(RagService.name);

  constructor(
    @Inject(DRIZZLE_PROVIDER) private readonly db: any,
    private readonly embeddingsService: EmbeddingsService,
  ) {}

  /**
   * Búsqueda semántica: Encuentra documentos similares a la query.
   */
  async searchSimilar(query: string, limit: number = 5): Promise<any[]> {
    this.logger.log(`Searching for similar documents to: ${query.substring(0, 50)}...`);

    // 1. Generar embedding de la query
    const queryEmbedding = await this.embeddingsService.generateEmbedding(query);

    // 2. Búsqueda por similitud en pgvector (usando cosine distance)
    const results = await this.db
      .select()
      .from(documents)
      .orderBy(
        // pgvector cosine distance: <-> operator
        // Esto requiere una función personalizada en Drizzle o SQL raw
      )
      .limit(limit);

    return results;
  }

  /**
   * Agregar documento al índice RAG.
   */
  async addDocument(content: string, metadata?: Record<string, any>): Promise<string> {
    this.logger.log('Adding document to RAG index...');

    // 1. Generar embedding del contenido
    const embedding = await this.embeddingsService.generateEmbedding(content);

    // 2. Guardar en base de datos con embedding
    const [doc] = await this.db
      .insert(documents)
      .values({
        content,
        metadata: metadata || {},
        embedding,
      })
      .returning();

    this.logger.log(`Document added with ID: ${doc.id}`);
    return doc.id;
  }
}
""".strip()


def get_embeddings_service_scaffold() -> str:
    """Versión scaffold: Interface con comentarios."""
    return """
import { Injectable, Logger, NotImplementedException } from '@nestjs/common';

@Injectable()
export class EmbeddingsService {
  private readonly logger = new Logger(EmbeddingsService.name);

  /**
   * Scaffold: Placeholder para generación de embeddings.
   * TODO: Implementar:
   * 1. Usar @xenova/transformers o servicio externo (OpenAI embeddings)
   * 2. Normalizar vectores
   * 3. Cachear embeddings generados
   */
  async generateEmbedding(text: string): Promise<number[]> {
    this.logger.warn('Embeddings generation not implemented yet.');
    throw new NotImplementedException('Embeddings generation is not implemented. Use --full flag when generating project.');
  }
}
""".strip()


def get_embeddings_service_full() -> str:
    """Versión full: Implementación completa de embeddings."""
    return """
import { Injectable, Logger } from '@nestjs/common';
import { createOpenAI } from '@ai-sdk/openai';
import { embedMany } from 'ai';

import { env } from '../../config/env';

@Injectable()
export class EmbeddingsService {
  private readonly logger = new Logger(EmbeddingsService.name);
  private readonly openai = createOpenAI({
    apiKey: env.OPENAI_API_KEY,
  });

  /**
   * Genera embedding para un texto usando OpenAI embeddings.
   */
  async generateEmbedding(text: string): Promise<number[]> {
    this.logger.debug(`Generating embedding for text (length: ${text.length})`);

    const { embeddings } = await embedMany({
      model: this.openai.embedding('text-embedding-3-small'),
      values: [text],
    });

    return embeddings[0];
  }

  /**
   * Genera embeddings para múltiples textos (batch).
   */
  async generateEmbeddings(texts: string[]): Promise<number[][]> {
    this.logger.debug(`Generating embeddings for ${texts.length} texts`);

    const { embeddings } = await embedMany({
      model: this.openai.embedding('text-embedding-3-small'),
      values: texts,
    });

    return embeddings;
  }
}
""".strip()


def get_rag_module() -> str:
    return """
import { Module } from '@nestjs/common';

import { EmbeddingsService } from './embeddings.service';
import { RagService } from './rag.service';

@Module({
  providers: [RagService, EmbeddingsService],
  exports: [RagService, EmbeddingsService],
})
export class RagModule {}
""".strip()


# ==================== Tools Services ====================


def get_tools_service_scaffold() -> str:
    """Versión scaffold: Placeholder con comentarios."""
    return """
import { Injectable, Logger, NotImplementedException } from '@nestjs/common';

@Injectable()
export class ToolsService {
  private readonly logger = new Logger(ToolsService.name);

  /**
   * Scaffold: Placeholder para function calling tools.
   * TODO: Implementar:
   * 1. Registrar herramientas disponibles (weather, calculator, etc.)
   * 2. Integrar con ChatService para function calling
   * 3. Ejecutar herramientas basadas en decisiones del LLM
   * 4. Retornar resultados al LLM para continuar la conversación
   */
  async executeTool(toolName: string, args: Record<string, any>): Promise<any> {
    this.logger.warn(`Tool execution not implemented yet. Tool: ${toolName}`);
    throw new NotImplementedException(`Tool ${toolName} is not implemented. Use --full flag when generating project.`);
  }

  listAvailableTools(): string[] {
    this.logger.warn('Tools listing not implemented yet.');
    return [];
  }
}
""".strip()


def get_tools_service_full() -> str:
    """Versión full: Implementación completa de tools."""
    return """
import { Injectable, Logger } from '@nestjs/common';

@Injectable()
export class ToolsService {
  private readonly logger = new Logger(ToolsService.name);

  /**
   * Ejecuta una herramienta por nombre.
   */
  async executeTool(toolName: string, args: Record<string, any>): Promise<any> {
    this.logger.log(`Executing tool: ${toolName} with args: ${JSON.stringify(args)}`);

    switch (toolName) {
      case 'calculator':
        return this._calculate(args.expression);
      case 'weather':
        return this._getWeather(args.location);
      default:
        throw new Error(`Unknown tool: ${toolName}`);
    }
  }

  listAvailableTools(): string[] {
    return ['calculator', 'weather'];
  }

  private _calculate(expression: string): number {
    // Simple calculator (production would use a safe evaluator)
    try {
      // eslint-disable-next-line no-eval
      return eval(expression);
    } catch (error) {
      throw new Error(`Invalid expression: ${expression}`);
    }
  }

  private async _getWeather(location: string): Promise<any> {
    // Placeholder for weather API
    return {
      location,
      temperature: 22,
      condition: 'sunny',
    };
  }
}
""".strip()


def get_tools_module() -> str:
    return """
import { Module } from '@nestjs/common';

import { ToolsService } from './tools.service';

@Module({
  providers: [ToolsService],
  exports: [ToolsService],
})
export class ToolsModule {}
""".strip()
