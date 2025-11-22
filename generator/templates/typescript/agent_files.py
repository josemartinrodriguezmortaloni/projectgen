"""
Templates para la arquitectura agnóstica de Agentes de IA.
Incluye patrones Strategy, Adapter, Factory y Protected Variations.
"""

from generator.templates.base import FileTemplate, dedent


def get_agent_templates(default_model: str, include_rag: bool) -> list[FileTemplate]:
    """
    Factory Method: Crea templates para el módulo de agentes.
    """
    templates = [
        _create_agents_module_template(),
        # Common
        _create_llm_provider_interface_template(),
        _create_model_registry_template(default_model),
        # Providers (Adapters)
        _create_openai_provider_template(),
        _create_anthropic_provider_template(),
        _create_google_provider_template(),
        _create_provider_factory_template(),
        # Chat Module (Implementation)
        _create_chat_module_template(),
        _create_chat_controller_template(),
        _create_chat_service_template(),
        _create_chat_dto_template(),
        # Placeholders for RAG and Tools
        FileTemplate("src/agents/tools/.gitkeep", ""),
    ]

    if include_rag:
        templates.append(FileTemplate("src/agents/rag/.gitkeep", ""))

    return templates


def _create_agents_module_template() -> FileTemplate:
    return FileTemplate(
        "src/agents/agents.module.ts",
        dedent("""
        import { Module } from '@nestjs/common';

        import { ChatModule } from './chat/chat.module';
        import { ProviderFactory } from './providers/provider.factory';

        @Module({
          imports: [ChatModule],
          providers: [
            // Factory global para crear proveedores
            ProviderFactory,
          ],
          exports: [ProviderFactory],
        })
        export class AgentsModule {}
        """),
    )


# ==================== Common (Interfaces & Registry) ====================


def _create_llm_provider_interface_template() -> FileTemplate:
    return FileTemplate(
        "src/agents/common/llm-provider.interface.ts",
        dedent("""
        import { CoreMessage, LanguageModelV1 } from 'ai';

        /**
         * Estrategia (Strategy Pattern): Define contrato común para todos los LLMs.
         * Protected Variations (GRASP): Protege el sistema de cambios en proveedores específicos.
         */
        export interface LLMProvider {
          /**
           * Nombre del proveedor (e.g., 'openai', 'anthropic')
           */
          providerName: string;

          /**
           * Genera una respuesta de texto simple.
           */
          generateResponse(messages: CoreMessage[], options?: GenerationOptions): Promise<GenerationResponse>;

          /**
           * Genera una respuesta en stream.
           */
          streamResponse(messages: CoreMessage[], options?: GenerationOptions): Promise<any>; // Retorna stream compatible con AI SDK

          /**
           * Verifica estado del proveedor.
           */
          healthCheck(): Promise<boolean>;
        }

        export interface GenerationOptions {
          temperature?: number;
          maxTokens?: number;
          topP?: number;
          modelId?: string;
        }

        export interface GenerationResponse {
          content: string;
          usage: {
            promptTokens: number;
            completionTokens: number;
            totalTokens: number;
          };
          finishReason: string;
        }
        """),
    )


def _create_model_registry_template(default_model: str) -> FileTemplate:
    return FileTemplate(
        "src/agents/common/model-registry.ts",
        dedent(f"""
        /**
         * Registro centralizado de modelos (Single Source of Truth).
         * Configuración específica de cada modelo soportado.
         */
        export enum ModelName {{
          GPT_5_1 = 'gpt-5.1',
          CLAUDE_SONNET_4_5 = 'claude-sonnet-4.5',
          CLAUDE_OPUS_4_1 = 'claude-opus-4.1',
          GEMINI_3 = 'gemini-3',
        }}

        export interface ModelConfig {{
          modelId: string; // ID real de la API del proveedor
          provider: 'openai' | 'anthropic' | 'google';
          contextWindow: number;
          costPer1kInput: number; // en USD
          costPer1kOutput: number; // en USD
        }}

        export const MODEL_REGISTRY: Record<ModelName, ModelConfig> = {{
          [ModelName.GPT_5_1]: {{
            modelId: 'gpt-5.1-preview', // ID hipotético
            provider: 'openai',
            contextWindow: 128000,
            costPer1kInput: 0.01,
            costPer1kOutput: 0.03,
          }},
          [ModelName.CLAUDE_SONNET_4_5]: {{
            modelId: 'claude-4-5-sonnet-20250620', // ID hipotético
            provider: 'anthropic',
            contextWindow: 200000,
            costPer1kInput: 0.003,
            costPer1kOutput: 0.015,
          }},
          [ModelName.CLAUDE_OPUS_4_1]: {{
            modelId: 'claude-4-1-opus-20250620', // ID hipotético
            provider: 'anthropic',
            contextWindow: 200000,
            costPer1kInput: 0.015,
            costPer1kOutput: 0.075,
          }},
          [ModelName.GEMINI_3]: {{
            modelId: 'gemini-3.0-pro', // ID hipotético
            provider: 'google',
            contextWindow: 1000000, // 1M context
            costPer1kInput: 0.001,
            costPer1kOutput: 0.004,
          }},
        }};

        export const DEFAULT_MODEL = ModelName.{default_model.upper().replace("-", "_").replace(".", "_")};

        export function getModelConfig(modelName: ModelName): ModelConfig {{
          const config = MODEL_REGISTRY[modelName];
          if (!config) {{
            throw new Error(`Model configuration for ${{modelName}} not found`);
          }}
          return config;
        }}
        """),
    )


# ==================== Providers (Adapters) ====================


def _create_openai_provider_template() -> FileTemplate:
    return FileTemplate(
        "src/agents/providers/openai.provider.ts",
        dedent("""
        import { createOpenAI } from '@ai-sdk/openai';
        import { generateText, streamText, CoreMessage } from 'ai';

        import { env } from '../../config/env';
        import { LLMProvider, GenerationOptions, GenerationResponse } from '../common/llm-provider.interface';

        /**
         * Adapter Pattern: Adapta la SDK de OpenAI a nuestra interfaz LLMProvider.
         */
        export class OpenAIProvider implements LLMProvider {
          providerName = 'openai';
          private client;

          constructor() {
            this.client = createOpenAI({
              apiKey: env.OPENAI_API_KEY,
            });
          }

          async generateResponse(messages: CoreMessage[], options?: GenerationOptions): Promise<GenerationResponse> {
            const modelId = options?.modelId || 'gpt-4o'; // Fallback safe

            const { text, usage, finishReason } = await generateText({
              model: this.client(modelId),
              messages,
              temperature: options?.temperature,
              maxTokens: options?.maxTokens,
            });

            return {
              content: text,
              usage: {
                promptTokens: usage.promptTokens,
                completionTokens: usage.completionTokens,
                totalTokens: usage.totalTokens,
              },
              finishReason,
            };
          }

          async streamResponse(messages: CoreMessage[], options?: GenerationOptions): Promise<any> {
            const modelId = options?.modelId || 'gpt-4o';
            
            return streamText({
              model: this.client(modelId),
              messages,
              temperature: options?.temperature,
              maxTokens: options?.maxTokens,
            });
          }

          async healthCheck(): Promise<boolean> {
            try {
              // Simple call to verify api key validity
              await this.generateResponse([{ role: 'user', content: 'ping' }], { maxTokens: 1 });
              return true;
            } catch (error) {
              console.error('OpenAI Health Check Failed:', error);
              return false;
            }
          }
        }
        """),
    )


def _create_anthropic_provider_template() -> FileTemplate:
    return FileTemplate(
        "src/agents/providers/anthropic.provider.ts",
        dedent("""
        import { createAnthropic } from '@ai-sdk/anthropic';
        import { generateText, streamText, CoreMessage } from 'ai';

        import { env } from '../../config/env';
        import { LLMProvider, GenerationOptions, GenerationResponse } from '../common/llm-provider.interface';

        /**
         * Adapter Pattern: Adapta la SDK de Anthropic.
         */
        export class AnthropicProvider implements LLMProvider {
          providerName = 'anthropic';
          private client;

          constructor() {
            this.client = createAnthropic({
              apiKey: env.ANTHROPIC_API_KEY,
            });
          }

          async generateResponse(messages: CoreMessage[], options?: GenerationOptions): Promise<GenerationResponse> {
            const modelId = options?.modelId || 'claude-3-5-sonnet-20240620';

            const { text, usage, finishReason } = await generateText({
              model: this.client(modelId),
              messages,
              temperature: options?.temperature,
              maxTokens: options?.maxTokens,
            });

            return {
              content: text,
              usage: {
                promptTokens: usage.promptTokens,
                completionTokens: usage.completionTokens,
                totalTokens: usage.totalTokens,
              },
              finishReason,
            };
          }

          async streamResponse(messages: CoreMessage[], options?: GenerationOptions): Promise<any> {
            const modelId = options?.modelId || 'claude-3-5-sonnet-20240620';
            
            return streamText({
              model: this.client(modelId),
              messages,
              temperature: options?.temperature,
              maxTokens: options?.maxTokens,
            });
          }

          async healthCheck(): Promise<boolean> {
            try {
              await this.generateResponse([{ role: 'user', content: 'ping' }], { maxTokens: 1 });
              return true;
            } catch (error) {
              console.error('Anthropic Health Check Failed:', error);
              return false;
            }
          }
        }
        """),
    )


def _create_google_provider_template() -> FileTemplate:
    return FileTemplate(
        "src/agents/providers/google.provider.ts",
        dedent("""
        import { createGoogleGenerativeAI } from '@ai-sdk/google';
        import { generateText, streamText, CoreMessage } from 'ai';

        import { env } from '../../config/env';
        import { LLMProvider, GenerationOptions, GenerationResponse } from '../common/llm-provider.interface';

        /**
         * Adapter Pattern: Adapta la SDK de Google Gemini.
         */
        export class GoogleProvider implements LLMProvider {
          providerName = 'google';
          private client;

          constructor() {
            this.client = createGoogleGenerativeAI({
              apiKey: env.GOOGLE_GENERATIVE_AI_API_KEY,
            });
          }

          async generateResponse(messages: CoreMessage[], options?: GenerationOptions): Promise<GenerationResponse> {
            const modelId = options?.modelId || 'gemini-1.5-pro';

            const { text, usage, finishReason } = await generateText({
              model: this.client(modelId),
              messages,
              temperature: options?.temperature,
              maxTokens: options?.maxTokens,
            });

            return {
              content: text,
              usage: {
                promptTokens: usage.promptTokens,
                completionTokens: usage.completionTokens,
                totalTokens: usage.totalTokens,
              },
              finishReason,
            };
          }

          async streamResponse(messages: CoreMessage[], options?: GenerationOptions): Promise<any> {
            const modelId = options?.modelId || 'gemini-1.5-pro';
            
            return streamText({
              model: this.client(modelId),
              messages,
              temperature: options?.temperature,
              maxTokens: options?.maxTokens,
            });
          }

          async healthCheck(): Promise<boolean> {
            try {
              await this.generateResponse([{ role: 'user', content: 'ping' }], { maxTokens: 1 });
              return true;
            } catch (error) {
              console.error('Google Health Check Failed:', error);
              return false;
            }
          }
        }
        """),
    )


def _create_provider_factory_template() -> FileTemplate:
    return FileTemplate(
        "src/agents/providers/provider.factory.ts",
        dedent("""
        import { Injectable } from '@nestjs/common';

        import { LLMProvider } from '../common/llm-provider.interface';
        import { ModelName, getModelConfig } from '../common/model-registry.ts';
        import { AnthropicProvider } from './anthropic.provider';
        import { GoogleProvider } from './google.provider';
        import { OpenAIProvider } from './openai.provider';

        @Injectable()
        export class ProviderFactory {
          private providers: Map<string, LLMProvider> = new Map();

          constructor() {
            // Inicializar providers (Lazy initialization podría ser otra opción)
            // Flyweight Pattern: Reusar instancias de providers
            this.providers.set('openai', new OpenAIProvider());
            this.providers.set('anthropic', new AnthropicProvider());
            this.providers.set('google', new GoogleProvider());
          }

          /**
           * Factory Method: Retorna el provider correcto y su configuración específica basado en el nombre del modelo.
           */
          create(modelName: ModelName): { provider: LLMProvider; modelId: string } {
            const config = getModelConfig(modelName);
            const provider = this.providers.get(config.provider);

            if (!provider) {
              throw new Error(`Provider ${config.provider} not implemented`);
            }

            return {
              provider,
              modelId: config.modelId,
            };
          }
        }
        """),
    )


# ==================== Chat Implementation (Example) ====================


def _create_chat_module_template() -> FileTemplate:
    return FileTemplate(
        "src/agents/chat/chat.module.ts",
        dedent("""
        import { Module } from '@nestjs/common';

        import { ProviderFactory } from '../providers/provider.factory';
        import { ChatController } from './chat.controller';
        import { ChatService } from './chat.service';

        @Module({
          controllers: [ChatController],
          providers: [
            ChatService,
            ProviderFactory, // Inyección directa del factory
          ],
        })
        export class ChatModule {}
        """),
    )


def _create_chat_controller_template() -> FileTemplate:
    return FileTemplate(
        "src/agents/chat/chat.controller.ts",
        dedent("""
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
        """),
    )


def _create_chat_service_template() -> FileTemplate:
    return FileTemplate(
        "src/agents/chat/chat.service.ts",
        dedent("""
        import { Injectable, Logger } from '@nestjs/common';
        import { CoreMessage } from 'ai';
        import { Observable, from, map } from 'rxjs';

        import { ProviderFactory } from '../providers/provider.factory';
        import { ChatRequestDto, ChatResponseDto } from './dto/chat-request.dto';

        @Injectable()
        export class ChatService {
          private readonly logger = new Logger(ChatService.name);

          constructor(private readonly providerFactory: ProviderFactory) {}

          /**
           * Procesa un mensaje de chat de forma agnóstica al proveedor.
           * Controller (GRASP): Orquesta la lógica entre el DTO y el Provider.
           */
          async processMessage(dto: ChatRequestDto): Promise<ChatResponseDto> {
            this.logger.log(`Processing message with model: ${dto.model}`);
            
            // 1. Obtener provider y configuración específica del modelo
            const { provider, modelId } = this.providerFactory.create(dto.model);

            // 2. Adaptar mensajes (si fuera necesario, aquí usamos CoreMessage de AI SDK directo)
            const messages: CoreMessage[] = dto.messages.map(m => ({
              role: m.role as 'user' | 'assistant' | 'system',
              content: m.content,
            }));

            // 3. Generar respuesta
            const response = await provider.generateResponse(messages, {
              modelId,
              temperature: dto.temperature,
              maxTokens: dto.maxTokens,
            });

            // 4. Retornar DTO
            return {
              content: response.content,
              role: 'assistant',
              usage: response.usage,
              model: dto.model,
            };
          }

          /**
           * Maneja streaming de respuesta (Server Sent Events).
           */
          streamMessage(dto: ChatRequestDto): Observable<any> {
            return from(this._streamGenerator(dto)).pipe(
              map((chunk) => ({ data: chunk }))
            );
          }

          private async *_streamGenerator(dto: ChatRequestDto) {
            const { provider, modelId } = this.providerFactory.create(dto.model);
            
            const messages: CoreMessage[] = dto.messages.map(m => ({
              role: m.role as 'user' | 'assistant' | 'system',
              content: m.content,
            }));

            const stream = await provider.streamResponse(messages, {
              modelId,
              temperature: dto.temperature,
            });

            // AI SDK stream consumption (simplified example)
            for await (const chunk of stream) {
               yield chunk;
            }
          }
        }
        """),
    )


def _create_chat_dto_template() -> FileTemplate:
    return FileTemplate(
        "src/agents/chat/dto/chat-request.dto.ts",
        dedent("""
        import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
        import { Type } from 'class-transformer';
        import { IsArray, IsEnum, IsNumber, IsOptional, IsString, ValidateNested, Max, Min } from 'class-validator';

        import { ModelName } from '../../common/model-registry';

        export class ChatMessageDto {
          @ApiProperty({ enum: ['user', 'assistant', 'system'] })
          @IsEnum(['user', 'assistant', 'system'])
          role: string;

          @ApiProperty()
          @IsString()
          content: string;
        }

        export class ChatRequestDto {
          @ApiProperty({ enum: ModelName, example: ModelName.GPT_5_1 })
          @IsEnum(ModelName)
          model: ModelName;

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
        """),
    )

