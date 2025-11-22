"""
Templates para archivos de la aplicación FastAPI.
Contiene 40+ templates con patrones SOLID, GoF y GRASP aplicados.
"""

from generator.templates.base import FileTemplate, dedent


def get_app_templates(project_name: str, hash_algo: str) -> list[FileTemplate]:
    """
    Factory Method (GoF): Crea conjunto de templates para app/.
    Open/Closed (SOLID): Agregar nuevos templates sin modificar esta función.

    Args:
        project_name: Nombre del proyecto.
        hash_algo: Algoritmo de hash ("bcrypt" o "argon2").

    Returns:
        Lista de FileTemplate con todos los archivos de app/.
    """
    return [
        # Root app/
        FileTemplate(
            "app/__init__.py",
            dedent("""
            # Paquete principal de la aplicación FastAPI.
        """),
        ),
        _create_main_template(),
        # app/core/
        FileTemplate(
            "app/core/__init__.py",
            dedent("""
            # Núcleo de la aplicación: configuración, seguridad, eventos, excepciones.
        """),
        ),
        _create_config_template(project_name),
        _create_security_template(hash_algo),
        _create_events_template(),
        _create_exceptions_template(),
        # app/db/
        FileTemplate(
            "app/db/__init__.py",
            dedent("""
            # Capa de acceso a base de datos.
        """),
        ),
        _create_db_session_template(),
        _create_db_base_class_template(),
        _create_db_base_template(),
        # app/models/
        FileTemplate(
            "app/models/__init__.py",
            dedent("""
            # Modelos SQLAlchemy (representan tablas de BD).
        """),
        ),
        _create_user_model_template(),
        _create_product_model_template(),
        _create_order_model_template(),
        # app/schemas/
        FileTemplate(
            "app/schemas/__init__.py",
            dedent("""
            # Schemas Pydantic v2 (validan y serializan datos HTTP).
        """),
        ),
        _create_user_schema_template(),
        _create_product_schema_template(),
        _create_order_schema_template(),
        # app/repositories/
        FileTemplate(
            "app/repositories/__init__.py",
            dedent("""
            # Patrón Repository: abstrae acceso a datos.
            # Solo queries, sin lógica de negocio.
        """),
        ),
        _create_base_repository_template(),
        _create_user_repository_template(),
        _create_product_repository_template(),
        _create_order_repository_template(),
        # app/services/
        FileTemplate(
            "app/services/__init__.py",
            dedent("""
            # Service Layer: lógica de negocio.
            # Valida, coordina repositorios, dispara eventos.
        """),
        ),
        _create_cache_service_template(),
        _create_user_service_template(),
        _create_product_service_template(),
        _create_order_service_template(),
        # app/factories/
        FileTemplate(
            "app/factories/__init__.py",
            dedent("""
            # Factory Pattern: creación de servicios con dependencias.
        """),
        ),
        _create_service_factory_template(),
        # app/utils/
        FileTemplate(
            "app/utils/__init__.py",
            dedent("""
            # Utilidades generales reutilizables.
        """),
        ),
        FileTemplate(
            "app/utils/validators.py",
            dedent("""
            # Validadores de negocio reutilizables.
        """),
        ),
        FileTemplate(
            "app/utils/helpers.py",
            dedent("""
            # Helper functions reutilizables.
        """),
        ),
        # app/api/
        FileTemplate(
            "app/api/__init__.py",
            dedent("""
            # Capa de presentación HTTP (endpoints).
        """),
        ),
        _create_dependencies_template(),
        # app/api/v1/
        FileTemplate(
            "app/api/v1/__init__.py",
            dedent("""
            # API versión 1.
        """),
        ),
        _create_api_router_template(),
        # app/api/v1/endpoints/
        FileTemplate(
            "app/api/v1/endpoints/__init__.py",
            dedent("""
            # Endpoints CRUD agrupados por recurso.
        """),
        ),
        _create_users_endpoint_template(),
        _create_products_endpoint_template(),
        _create_orders_endpoint_template(),
    ]


# ==================== app/main.py ====================


def _create_main_template() -> FileTemplate:
    """FastAPI entry point with lifespan events."""
    return FileTemplate(
        "app/main.py",
        dedent("""
        from contextlib import asynccontextmanager

        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        from app.api.v1.router import api_router
        from app.core.config import settings
        from app.db.session import init_db, close_db


        @asynccontextmanager
        async def lifespan(app: FastAPI):
            '''
            Lifespan events (Startup/Shutdown).
            Observer pattern: Aquí se suscriben listeners de eventos si es necesario.
            '''
            # Startup
            await init_db()
            yield
            # Shutdown
            await close_db()


        def create_app() -> FastAPI:
            '''
            Factory Method (GoF): Crea instancia de FastAPI.
            Single Responsibility (SOLID): Solo configuración de app.
            '''
            app = FastAPI(
                title=settings.PROJECT_NAME,
                version=settings.VERSION,
                lifespan=lifespan,
            )

            # CORS
            app.add_middleware(
                CORSMiddleware,
                allow_origins=settings.CORS_ORIGINS,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            # Routers
            app.include_router(api_router, prefix="/api/v1")

            return app


        app = create_app()
    """),
    )


# ==================== app/core/ ====================


def _create_config_template(project_name: str) -> FileTemplate:
    """Singleton for configuration with pydantic-settings."""
    return FileTemplate(
        "app/core/config.py",
        dedent(f"""
        from functools import lru_cache

        from pydantic_settings import BaseSettings, SettingsConfigDict


        class Settings(BaseSettings):
            '''
            Singleton (GoF): Una sola instancia via lru_cache.
            Single Responsibility (SOLID): Solo maneja configuración.
            Information Expert (GRASP): Conoce toda la configuración de la app.

            Uso:
                from app.core.config import settings
                print(settings.DATABASE_URL)
            '''

            # App
            PROJECT_NAME: str = "{project_name}"
            VERSION: str = "1.0.0"

            # Database
            DATABASE_URL: str
            DB_POOL_SIZE: int = 50
            DB_MAX_OVERFLOW: int = 100

            # Redis
            REDIS_URL: str
            REDIS_ENABLED: bool = True

            # Security
            SECRET_KEY: str
            ALGORITHM: str = "HS256"
            ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

            # CORS
            CORS_ORIGINS: list[str] = ["*"]

            model_config = SettingsConfigDict(
                env_file=".env",
                case_sensitive=True,
                extra="ignore"
            )


        @lru_cache()
        def get_settings() -> Settings:
            '''
            Singleton (GoF): Garantiza una sola instancia.
            Creator (GRASP): Responsable de crear Settings.
            '''
            return Settings()


        # Instancia global
        settings = get_settings()
    """),
    )


def _create_security_template(hash_algo: str) -> FileTemplate:
    """Strategy pattern for password hashing + JWT."""
    default_hasher = "Argon2Hasher" if hash_algo == "argon2" else "BcryptHasher"

    return FileTemplate(
        "app/core/security.py",
        dedent(f"""
        from abc import ABC, abstractmethod
        from datetime import datetime, timedelta, timezone
        from typing import Any

        import jwt
        from passlib.context import CryptContext

        from app.core.config import settings


        class PasswordHasher(ABC):
            '''
            Strategy (GoF): Define familia de algoritmos de hash.
            Open/Closed (SOLID): Agregar nuevas estrategias sin modificar código.

            Permite cambiar entre bcrypt y argon2 fácilmente.
            '''

            @abstractmethod
            def hash(self, password: str) -> str:
                '''Hashea password'''
                pass

            @abstractmethod
            def verify(self, plain_password: str, hashed_password: str) -> bool:
                '''Verifica password'''
                pass


        class BcryptHasher(PasswordHasher):
            '''
            Concrete Strategy: Bcrypt.
            Balance entre seguridad y performance.
            '''

            def __init__(self) -> None:
                self._pwd_context = CryptContext(
                    schemes=["bcrypt"],
                    deprecated="auto"
                )

            def hash(self, password: str) -> str:
                return self._pwd_context.hash(password)

            def verify(self, plain_password: str, hashed_password: str) -> bool:
                return self._pwd_context.verify(plain_password, hashed_password)


        class Argon2Hasher(PasswordHasher):
            '''
            Concrete Strategy: Argon2.
            Más seguro, recomendado para nuevos proyectos.
            '''

            def __init__(self) -> None:
                self._pwd_context = CryptContext(
                    schemes=["argon2"],
                    deprecated="auto"
                )

            def hash(self, password: str) -> str:
                return self._pwd_context.hash(password)

            def verify(self, plain_password: str, hashed_password: str) -> bool:
                return self._pwd_context.verify(plain_password, hashed_password)


        class SecurityService:
            '''
            Dependency Inversion (SOLID): Depende de abstracción (PasswordHasher).
            Information Expert (GRASP): Experto en operaciones de seguridad.
            Single Responsibility (SOLID): Solo maneja hash y JWT.
            '''

            def __init__(self, hasher: PasswordHasher) -> None:
                self._hasher = hasher

            def hash_password(self, password: str) -> str:
                '''Hashea password usando estrategia configurada'''
                return self._hasher.hash(password)

            def verify_password(self, plain_password: str, hashed_password: str) -> bool:
                '''Verifica password usando estrategia configurada'''
                return self._hasher.verify(plain_password, hashed_password)

            def create_access_token(
                self,
                data: dict[str, Any],
                expires_delta: timedelta | None = None
            ) -> str:
                '''
                Create JWT access token.

                Args:
                    data: Token payload (e.g.: {{"sub": "user_id"}})
                    expires_delta: Custom expiration time
                '''
                to_encode = data.copy()

                if expires_delta:
                    expire = datetime.now(timezone.utc) + expires_delta
                else:
                    expire = datetime.now(timezone.utc) + timedelta(
                        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                    )

                to_encode.update({{"exp": expire}})
                encoded_jwt = jwt.encode(
                    to_encode,
                    settings.SECRET_KEY,
                    algorithm=settings.ALGORITHM
                )
                return encoded_jwt

            def decode_token(self, token: str) -> dict[str, Any]:
                '''Decodifica y valida JWT token'''
                return jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM]
                )


        # Singleton: Instancia global con estrategia por defecto
        security = SecurityService({default_hasher}())

        # Para cambiar estrategia:
        # security = SecurityService(BcryptHasher())
    """),
    )


def _create_events_template() -> FileTemplate:
    """Observer pattern for async event system."""
    return FileTemplate(
        "app/core/events.py",
        dedent("""
        from enum import Enum
        from typing import Callable


        class EventType(str, Enum):
            '''
            Tipos de eventos del sistema.
            '''
            USER_CREATED = "user.created"
            USER_UPDATED = "user.updated"
            USER_DELETED = "user.deleted"

            ORDER_CREATED = "order.created"
            ORDER_COMPLETED = "order.completed"
            ORDER_CANCELLED = "order.cancelled"

            PRODUCT_OUT_OF_STOCK = "product.out_of_stock"
            PRODUCT_LOW_STOCK = "product.low_stock"


        class Event:
            '''
            Representa un evento del sistema.
            '''

            def __init__(self, event_type: EventType, data: dict) -> None:
                self.type = event_type
                self.data = data


        class EventDispatcher:
            '''
            Observer (GoF): Subject que notifica a observers.
            Single Responsibility (SOLID): Solo maneja eventos.
            Controller (GRASP): Coordina flujo de eventos.

            Uso:
                from app.core.events import event_dispatcher, EventType, Event

                async def handle_user_created(event: Event):
                    print(f"Usuario creado: {event.data}")

                event_dispatcher.subscribe(EventType.USER_CREATED, handle_user_created)
                await event_dispatcher.dispatch(Event(EventType.USER_CREATED, {{"id": 1}}))
            '''

            def __init__(self) -> None:
                self._listeners: dict[EventType, list[Callable]] = {}

            def subscribe(self, event_type: EventType, listener: Callable) -> None:
                '''
                Suscribe un listener a un tipo de evento.
                '''
                if event_type not in self._listeners:
                    self._listeners[event_type] = []

                self._listeners[event_type].append(listener)

            def unsubscribe(self, event_type: EventType, listener: Callable) -> None:
                '''
                Desuscribe un listener.
                '''
                if event_type in self._listeners:
                    try:
                        self._listeners[event_type].remove(listener)
                    except ValueError:
                        pass

            async def dispatch(self, event: Event) -> None:
                '''
                Dispara un evento a todos los listeners suscritos.
                '''
                if event.type not in self._listeners:
                    return

                for listener in self._listeners[event.type]:
                    try:
                        if callable(listener):
                            result = listener(event)
                            # Si es async, await
                            if hasattr(result, '__await__'):
                                await result
                    except Exception as exc:
                        # Log error pero no detiene otros listeners
                        print(f"Error in event listener: {exc}")


        # Singleton: Instancia global
        event_dispatcher = EventDispatcher()


        # Ejemplo de listeners
        async def send_welcome_email(event: Event) -> None:
            '''
            Listener: Envía email de bienvenida cuando se crea usuario.
            '''
            user_data = event.data
            print(f"📧 Sending welcome email to {user_data.get('email')}")
            # Aquí iría la lógica real de envío


        async def log_user_creation(event: Event) -> None:
            '''
            Listener: Registra creación de usuario en logs.
            '''
            user_data = event.data
            print(f"📝 User created: {user_data.get('id')} - {user_data.get('email')}")


        async def notify_low_stock(event: Event) -> None:
            '''
            Listener: Notifica cuando un producto tiene stock bajo.
            '''
            product_data = event.data
            print(f"⚠️ Low stock alert: {product_data.get('name')} - Stock: {product_data.get('stock')}")


        # Registrar listeners por defecto
        event_dispatcher.subscribe(EventType.USER_CREATED, send_welcome_email)
        event_dispatcher.subscribe(EventType.USER_CREATED, log_user_creation)
        event_dispatcher.subscribe(EventType.PRODUCT_LOW_STOCK, notify_low_stock)
    """),
    )


def _create_exceptions_template() -> FileTemplate:
    """Custom domain exceptions."""
    return FileTemplate(
        "app/core/exceptions.py",
        dedent("""
        class AppException(Exception):
            '''
            Excepción base de la aplicación.
            Todas las excepciones custom heredan de esta.
            '''
            pass


        class InstanceNotFoundError(AppException):
            '''
            Entidad no encontrada en la base de datos.
            '''
            pass


        class DuplicateEmailError(AppException):
            '''
            Email duplicado (violación de unicidad).
            '''
            pass


        class ValidationError(AppException):
            '''
            Error de validación de reglas de negocio.
            '''
            pass


        class DatabaseError(AppException):
            '''
            Error de base de datos.
            '''
            pass


        class CacheError(AppException):
            '''
            Error de cache (Redis).
            '''
            pass


        class AuthenticationError(AppException):
            '''
            Error de autenticación (credenciales inválidas).
            '''
            pass


        class AuthorizationError(AppException):
            '''
            Error de autorización (permisos insuficientes).
            '''
            pass
    """),
    )


# ==================== app/db/ ====================


def _create_db_session_template() -> FileTemplate:
    """AsyncSession factory for SQLAlchemy 2.0."""
    return FileTemplate(
        "app/db/session.py",
        dedent("""
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

        from app.core.config import settings


        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            echo=False,
            future=True,
        )

        # Create session factory
        SessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )


        async def get_db() -> AsyncSession:
            '''
            Dependency para obtener sesión de DB.
            Creator (GRASP): Responsable de crear sesiones.

            Uso en endpoints:
                async def endpoint(db: AsyncSession = Depends(get_db)):
                    ...
            '''
            async with SessionLocal() as session:
                yield session


        async def init_db() -> None:
            '''
            Inicializa conexión a DB (llamado en startup).
            '''
            pass


        async def close_db() -> None:
            '''
            Cierra conexión a DB (llamado en shutdown).
            '''
            await engine.dispose()
    """),
    )


def _create_db_base_class_template() -> FileTemplate:
    """SQLAlchemy declarative base (pure base class)."""
    return FileTemplate(
        "app/db/base_class.py",
        dedent("""
        from sqlalchemy.orm import declarative_base

        # Base declarativa para todos los modelos
        # Este archivo contiene solo la definición de Base para evitar importaciones circulares
        Base = declarative_base()
    """),
    )


def _create_db_base_template() -> FileTemplate:
    """Import Base and register models for Alembic."""
    return FileTemplate(
        "app/db/base.py",
        dedent("""
        # Importar Base desde base_class para evitar importaciones circulares
        from app.db.base_class import Base  # noqa: F401

        # Importar todos los modelos aquí para que Alembic los detecte
        # Los modelos importan Base desde base_class, no desde aquí
        from app.models.user import User  # noqa: F401
        from app.models.product import Product  # noqa: F401
        from app.models.order import Order  # noqa: F401
    """),
    )


# ==================== app/models/ ====================


def _create_user_model_template() -> FileTemplate:
    """SQLAlchemy model for User."""
    return FileTemplate(
        "app/models/user.py",
        dedent("""
        from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

        from app.db.base_class import Base


        class User(Base):
            '''
            Modelo de usuario.
            Information Expert (GRASP): Conoce estructura de datos de usuario.
            '''
            __tablename__ = "users"

            id = Column(Integer, primary_key=True, index=True)
            email = Column(String(255), unique=True, index=True, nullable=False)
            name = Column(String(255), nullable=False)
            hashed_password = Column(String(255), nullable=False)
            is_active = Column(Boolean, default=True, nullable=False)
            created_at = Column(
                DateTime(timezone=True),
                server_default=func.now(),
                nullable=False,
            )
            updated_at = Column(
                DateTime(timezone=True),
                server_default=func.now(),
                onupdate=func.now(),
                nullable=False,
            )
    """),
    )


def _create_product_model_template() -> FileTemplate:
    """SQLAlchemy model for Product."""
    return FileTemplate(
        "app/models/product.py",
        dedent("""
        from sqlalchemy import Column, DateTime, Integer, Numeric, String, func

        from app.db.base_class import Base


        class Product(Base):
            '''
            Modelo de producto.
            Information Expert (GRASP): Conoce estructura de datos de producto.
            '''
            __tablename__ = "products"

            id = Column(Integer, primary_key=True, index=True)
            name = Column(String(255), unique=True, index=True, nullable=False)
            description = Column(String(1024), nullable=True)
            price = Column(Numeric(10, 2), nullable=False)
            stock = Column(Integer, nullable=False, default=0)
            created_at = Column(
                DateTime(timezone=True),
                server_default=func.now(),
                nullable=False,
            )
            updated_at = Column(
                DateTime(timezone=True),
                server_default=func.now(),
                onupdate=func.now(),
                nullable=False,
            )
    """),
    )


def _create_order_model_template() -> FileTemplate:
    """SQLAlchemy model for Order."""
    return FileTemplate(
        "app/models/order.py",
        dedent("""
        from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func
        from sqlalchemy.orm import relationship

        from app.db.base_class import Base


        class Order(Base):
            '''
            Modelo de orden.
            Information Expert (GRASP): Conoce estructura de datos de orden.
            '''
            __tablename__ = "orders"

            id = Column(Integer, primary_key=True, index=True)
            user_id = Column(
                Integer,
                ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            )
            status = Column(String(50), nullable=False, default="pending")
            total_amount = Column(Numeric(10, 2), nullable=False, default=0)
            created_at = Column(
                DateTime(timezone=True),
                server_default=func.now(),
                nullable=False,
            )
            updated_at = Column(
                DateTime(timezone=True),
                server_default=func.now(),
                onupdate=func.now(),
                nullable=False,
            )

            # Relationships
            user = relationship("User", backref="orders")
    """),
    )


# ==================== app/schemas/ ====================


def _create_user_schema_template() -> FileTemplate:
    """Pydantic v2 schemas for User."""
    return FileTemplate(
        "app/schemas/user.py",
        dedent("""
        from pydantic import BaseModel, EmailStr, ConfigDict


        class UserBase(BaseModel):
            '''Schema base de usuario.'''
            email: EmailStr
            name: str


        class UserCreate(UserBase):
            '''Schema para crear usuario.'''
            password: str


        class UserUpdate(BaseModel):
            '''Schema para actualizar usuario (campos opcionales).'''
            email: EmailStr | None = None
            name: str | None = None
            password: str | None = None


        class UserResponse(UserBase):
            '''Schema de respuesta de usuario.'''
            id: int
            is_active: bool = True

            model_config = ConfigDict(from_attributes=True)
    """),
    )


def _create_product_schema_template() -> FileTemplate:
    """Pydantic v2 schemas for Product."""
    return FileTemplate(
        "app/schemas/product.py",
        dedent("""
        from decimal import Decimal

        from pydantic import BaseModel, ConfigDict


        class ProductBase(BaseModel):
            '''Schema base de producto.'''
            name: str
            description: str | None = None
            price: Decimal
            stock: int


        class ProductCreate(ProductBase):
            '''Schema para crear producto.'''
            pass


        class ProductUpdate(BaseModel):
            '''Schema para actualizar producto (campos opcionales).'''
            name: str | None = None
            description: str | None = None
            price: Decimal | None = None
            stock: int | None = None


        class ProductResponse(ProductBase):
            '''Schema de respuesta de producto.'''
            id: int

            model_config = ConfigDict(from_attributes=True)
    """),
    )


def _create_order_schema_template() -> FileTemplate:
    """Pydantic v2 schemas for Order."""
    return FileTemplate(
        "app/schemas/order.py",
        dedent("""
        from decimal import Decimal

        from pydantic import BaseModel, ConfigDict


        class OrderBase(BaseModel):
            '''Schema base de orden.'''
            user_id: int
            status: str = "pending"
            total_amount: Decimal


        class OrderCreate(OrderBase):
            '''Schema para crear orden.'''
            pass


        class OrderUpdate(BaseModel):
            '''Schema para actualizar orden (campos opcionales).'''
            status: str | None = None
            total_amount: Decimal | None = None


        class OrderResponse(OrderBase):
            '''Schema de respuesta de orden.'''
            id: int

            model_config = ConfigDict(from_attributes=True)
    """),
    )


# ==================== app/repositories/ ====================


def _create_base_repository_template() -> FileTemplate:
    """Generic async repository pattern."""
    return FileTemplate(
        "app/repositories/base.py",
        dedent("""
        from typing import Generic, TypeVar, Type

        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession

        from app.core.exceptions import DatabaseError
        from app.db.base_class import Base


        ModelType = TypeVar("ModelType", bound=Base)


        class BaseRepository(Generic[ModelType]):
            '''
            Repository Pattern (GoF): Abstrae acceso a datos.
            Pure Fabrication (GRASP): No es del dominio, es infraestructura.
            Single Responsibility (SOLID): Solo queries.
            Open/Closed (SOLID): Extendible por herencia.
            Protected Variations (GRASP): Protege servicios de cambios en ORM.

            Beneficios:
            - Cambiar ORM no afecta servicios
            - Fácil mockear en tests
            - Reutilizar queries comunes
            '''

            def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
                self._model = model
                self._db = db

            async def get_by_id(self, id: int) -> ModelType | None:
                '''Obtiene entidad por ID'''
                try:
                    result = await self._db.execute(
                        select(self._model).where(self._model.id == id)
                    )
                    return result.scalar_one_or_none()
                except Exception as exc:
                    raise DatabaseError(f"Error fetching {self._model.__name__}: {exc}")

            async def get_all(
                self,
                skip: int = 0,
                limit: int = 100
            ) -> list[ModelType]:
                '''Obtiene todas las entidades con paginación'''
                try:
                    result = await self._db.execute(
                        select(self._model).offset(skip).limit(limit)
                    )
                    return list(result.scalars().all())
                except Exception as exc:
                    raise DatabaseError(f"Error fetching {self._model.__name__} list: {exc}")

            async def create(self, entity: ModelType) -> ModelType:
                '''Crea nueva entidad'''
                try:
                    self._db.add(entity)
                    await self._db.commit()
                    await self._db.refresh(entity)
                    return entity
                except Exception as exc:
                    await self._db.rollback()
                    raise DatabaseError(f"Error creating {self._model.__name__}: {exc}")

            async def update(self, entity: ModelType) -> ModelType:
                '''Actualiza entidad existente'''
                try:
                    await self._db.commit()
                    await self._db.refresh(entity)
                    return entity
                except Exception as exc:
                    await self._db.rollback()
                    raise DatabaseError(f"Error updating {self._model.__name__}: {exc}")

            async def delete(self, entity: ModelType) -> None:
                '''Elimina entidad'''
                try:
                    self._db.delete(entity)
                    await self._db.commit()
                except Exception as exc:
                    await self._db.rollback()
                    raise DatabaseError(f"Error deleting {self._model.__name__}: {exc}")

            async def exists(self, id: int) -> bool:
                '''Verifica si existe entidad'''
                result = await self._db.execute(
                    select(self._model.id).where(self._model.id == id)
                )
                return result.scalar_one_or_none() is not None
    """),
    )


def _create_user_repository_template() -> FileTemplate:
    """Concrete repository for User."""
    return FileTemplate(
        "app/repositories/user_repository.py",
        dedent("""
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession

        from app.models.user import User
        from app.repositories.base import BaseRepository


        class UserRepository(BaseRepository[User]):
            '''
            Open/Closed (SOLID): Extiende BaseRepository.
            Information Expert (GRASP): Experto en persistencia de usuarios.

            Agrega queries específicos de User.
            '''

            def __init__(self, db: AsyncSession) -> None:
                super().__init__(User, db)

            async def get_by_email(self, email: str) -> User | None:
                '''Query específico: buscar por email'''
                result = await self._db.execute(
                    select(User).where(User.email == email)
                )
                return result.scalar_one_or_none()

            async def email_exists(self, email: str) -> bool:
                '''Verifica si email ya existe'''
                result = await self._db.execute(
                    select(User.id).where(User.email == email)
                )
                return result.scalar_one_or_none() is not None
    """),
    )


def _create_product_repository_template() -> FileTemplate:
    """Concrete repository for Product."""
    return FileTemplate(
        "app/repositories/product_repository.py",
        dedent("""
        from sqlalchemy.ext.asyncio import AsyncSession

        from app.models.product import Product
        from app.repositories.base import BaseRepository


        class ProductRepository(BaseRepository[Product]):
            '''
            Repository para productos.
            '''

            def __init__(self, db: AsyncSession) -> None:
                super().__init__(Product, db)
    """),
    )


def _create_order_repository_template() -> FileTemplate:
    """Concrete repository for Order."""
    return FileTemplate(
        "app/repositories/order_repository.py",
        dedent("""
        from sqlalchemy.ext.asyncio import AsyncSession

        from app.models.order import Order
        from app.repositories.base import BaseRepository


        class OrderRepository(BaseRepository[Order]):
            '''
            Repository para órdenes.
            '''

            def __init__(self, db: AsyncSession) -> None:
                super().__init__(Order, db)
    """),
    )


# ==================== app/services/ ====================


def _create_cache_service_template() -> FileTemplate:
    """Singleton for async Redis."""
    return FileTemplate(
        "app/services/cache_service.py",
        dedent("""
        import json
        from functools import lru_cache
        from typing import Any

        from redis.asyncio import Redis

        from app.core.config import settings


        class CacheService:
            '''
            Singleton (GoF): Una sola instancia via lru_cache.
            Single Responsibility (SOLID): Solo maneja cache.
            '''

            def __init__(self) -> None:
                if not settings.REDIS_ENABLED:
                    self._client = None
                    return

                self._client = Redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )

            async def get(self, key: str) -> Any | None:
                '''Obtiene valor del cache'''
                if not self._client:
                    return None

                try:
                    value = await self._client.get(key)
                    return json.loads(value) if value else None
                except Exception:
                    return None

            async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
                '''Guarda valor en cache'''
                if not self._client:
                    return False

                try:
                    serialized = json.dumps(value)
                    await self._client.setex(key, ttl, serialized)
                    return True
                except Exception:
                    return False

            async def delete(self, pattern: str) -> int:
                '''Elimina keys que coincidan con el patrón'''
                if not self._client:
                    return 0

                try:
                    keys = await self._client.keys(pattern)
                    if keys:
                        return await self._client.delete(*keys)
                    return 0
                except Exception:
                    return 0

            async def close(self) -> None:
                '''Cierra conexión'''
                if self._client:
                    await self._client.close()


        @lru_cache()
        def get_cache_service() -> CacheService:
            '''
            Singleton (GoF): Garantiza una sola instancia.
            Creator (GRASP): Responsable de crear CacheService.
            '''
            return CacheService()


        # Instancia global
        cache = get_cache_service()
    """),
    )


def _create_user_service_template() -> FileTemplate:
    """Service layer for User with business logic."""
    return FileTemplate(
        "app/services/user_service.py",
        dedent("""
        from app.core.events import Event, EventType, event_dispatcher
        from app.core.exceptions import (
            DuplicateEmailError,
            InstanceNotFoundError,
            ValidationError,
        )
        from app.core.security import security
        from app.models.user import User
        from app.repositories.user_repository import UserRepository
        from app.schemas.user import UserCreate, UserResponse, UserUpdate
        from app.services.cache_service import CacheService


        class UserService:
            '''
            Service Layer: Lógica de negocio de usuarios.

            SOLID:
                - Single Responsibility: Lógica de negocio de usuarios
                - Dependency Inversion: Depende de abstracciones (Repository, Cache)
            GRASP:
                - Controller: Coordina operaciones de usuario
                - Information Expert: Conoce reglas de negocio de usuarios
                - Low Coupling: Usa repositorio, no accede directamente a DB
            '''

            def __init__(
                self,
                repository: UserRepository,
                cache: CacheService
            ) -> None:
                self._repository = repository
                self._cache = cache

            async def get_all(
                self,
                skip: int = 0,
                limit: int = 100
            ) -> list[UserResponse]:
                '''Obtiene todos los usuarios (con cache)'''
                cache_key = f"users:list:{skip}:{limit}"
                cached = await self._cache.get(cache_key)

                if cached:
                    return [UserResponse(**user) for user in cached]

                users = await self._repository.get_all(skip, limit)

                users_dict = [
                    UserResponse.model_validate(u).model_dump()
                    for u in users
                ]
                await self._cache.set(cache_key, users_dict, ttl=300)

                return [UserResponse.model_validate(u) for u in users]

            async def get_by_id(self, user_id: int) -> UserResponse:
                '''Obtiene usuario por ID (con cache)'''
                cache_key = f"users:id:{user_id}"
                cached = await self._cache.get(cache_key)

                if cached:
                    return UserResponse(**cached)

                user = await self._repository.get_by_id(user_id)
                if not user:
                    raise InstanceNotFoundError(f"User with id {user_id} not found")

                user_dict = UserResponse.model_validate(user).model_dump()
                await self._cache.set(cache_key, user_dict, ttl=300)

                return UserResponse.model_validate(user)

            async def create(self, user_data: UserCreate) -> UserResponse:
                '''
                Crea nuevo usuario.
                Valida: email único, password seguro.
                Dispara: evento USER_CREATED.
                '''
                # Validación de negocio
                if await self._repository.email_exists(user_data.email):
                    raise DuplicateEmailError(
                        f"Email {user_data.email} already exists"
                    )

                if len(user_data.password) < 8:
                    raise ValidationError("Password must be at least 8 characters")

                # Hash password
                hashed_password = security.hash_password(user_data.password)

                # Crear entidad
                user = User(
                    email=user_data.email,
                    name=user_data.name,
                    hashed_password=hashed_password
                )

                # Persistir
                created_user = await self._repository.create(user)

                # Invalidar cache
                await self._cache.delete("users:list:*")

                # Disparar evento
                await event_dispatcher.dispatch(Event(
                    EventType.USER_CREATED,
                    data={
                        "id": created_user.id,
                        "email": created_user.email,
                        "name": created_user.name
                    }
                ))

                return UserResponse.model_validate(created_user)

            async def update(
                self,
                user_id: int,
                user_data: UserUpdate
            ) -> UserResponse:
                '''Actualiza usuario existente'''
                user = await self._repository.get_by_id(user_id)
                if not user:
                    raise InstanceNotFoundError(f"User with id {user_id} not found")

                # Validar email único si se cambia
                if user_data.email and user_data.email != user.email:
                    if await self._repository.email_exists(user_data.email):
                        raise DuplicateEmailError(
                            f"Email {user_data.email} already exists"
                        )

                # Actualizar campos
                update_data = user_data.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    if field == "password" and value is not None:
                        setattr(
                            user,
                            "hashed_password",
                            security.hash_password(value)
                        )
                    elif field != "password":
                        setattr(user, field, value)

                # Persistir
                updated_user = await self._repository.update(user)

                # Invalidar cache
                await self._cache.delete(f"users:id:{user_id}")
                await self._cache.delete("users:list:*")

                return UserResponse.model_validate(updated_user)

            async def delete(self, user_id: int) -> None:
                '''Elimina usuario'''
                user = await self._repository.get_by_id(user_id)
                if not user:
                    raise InstanceNotFoundError(f"User with id {user_id} not found")

                await self._repository.delete(user)

                # Invalidar cache
                await self._cache.delete(f"users:id:{user_id}")
                await self._cache.delete("users:list:*")
    """),
    )


def _create_product_service_template() -> FileTemplate:
    """Service layer for Product."""
    return FileTemplate(
        "app/services/product_service.py",
        dedent("""
        from app.repositories.product_repository import ProductRepository
        from app.schemas.product import ProductResponse
        from app.services.cache_service import CacheService


        class ProductService:
            '''
            Service Layer: Lógica de negocio de productos.
            '''

            def __init__(
                self,
                repository: ProductRepository,
                cache: CacheService
            ) -> None:
                self._repository = repository
                self._cache = cache

            async def get_all(
                self,
                skip: int = 0,
                limit: int = 100
            ) -> list[ProductResponse]:
                '''Obtiene todos los productos'''
                products = await self._repository.get_all(skip=skip, limit=limit)
                return [ProductResponse.model_validate(p) for p in products]
    """),
    )


def _create_order_service_template() -> FileTemplate:
    """Service layer for Order."""
    return FileTemplate(
        "app/services/order_service.py",
        dedent("""
        from app.repositories.order_repository import OrderRepository
        from app.repositories.product_repository import ProductRepository
        from app.repositories.user_repository import UserRepository
        from app.schemas.order import OrderResponse
        from app.services.cache_service import CacheService


        class OrderService:
            '''
            Service Layer: Lógica de negocio de órdenes.
            Ejemplo de servicio que coordina múltiples repositorios.
            '''

            def __init__(
                self,
                repository: OrderRepository,
                product_repository: ProductRepository,
                user_repository: UserRepository,
                cache: CacheService
            ) -> None:
                self._repository = repository
                self._product_repository = product_repository
                self._user_repository = user_repository
                self._cache = cache

            async def get_all(
                self,
                skip: int = 0,
                limit: int = 100
            ) -> list[OrderResponse]:
                '''Obtiene todas las órdenes'''
                orders = await self._repository.get_all(skip=skip, limit=limit)
                return [OrderResponse.model_validate(o) for o in orders]
    """),
    )


# ==================== app/factories/ ====================


def _create_service_factory_template() -> FileTemplate:
    """Factory for service creation with dependencies."""
    return FileTemplate(
        "app/factories/service_factory.py",
        dedent("""
        from sqlalchemy.ext.asyncio import AsyncSession

        from app.repositories.order_repository import OrderRepository
        from app.repositories.product_repository import ProductRepository
        from app.repositories.user_repository import UserRepository
        from app.services.cache_service import cache
        from app.services.order_service import OrderService
        from app.services.product_service import ProductService
        from app.services.user_service import UserService


        class ServiceFactory:
            '''
            Factory (GoF): Centraliza creación de servicios.
            Creator (GRASP): Responsable de crear servicios con dependencias.
            Single Responsibility (SOLID): Solo crea servicios.

            Beneficios:
            - Oculta complejidad de construcción
            - Centraliza inyección de dependencias
            - Facilita testing (mockear factory)
            '''

            @staticmethod
            def create_user_service(db: AsyncSession) -> UserService:
                '''Crea UserService con todas sus dependencias'''
                repository = UserRepository(db)
                return UserService(repository, cache)

            @staticmethod
            def create_product_service(db: AsyncSession) -> ProductService:
                '''Crea ProductService con todas sus dependencias'''
                repository = ProductRepository(db)
                return ProductService(repository, cache)

            @staticmethod
            def create_order_service(db: AsyncSession) -> OrderService:
                '''
                Crea OrderService con todas sus dependencias.
                Ejemplo de servicio que necesita múltiples repositorios.
                '''
                order_repo = OrderRepository(db)
                product_repo = ProductRepository(db)
                user_repo = UserRepository(db)

                return OrderService(
                    repository=order_repo,
                    product_repository=product_repo,
                    user_repository=user_repo,
                    cache=cache
                )
    """),
    )


# ==================== app/api/ ====================


def _create_dependencies_template() -> FileTemplate:
    """Dependency Injection for FastAPI."""
    return FileTemplate(
        "app/api/dependencies.py",
        dedent("""
        from typing import Annotated

        from fastapi import Depends
        from sqlalchemy.ext.asyncio import AsyncSession

        from app.db.session import get_db
        from app.factories.service_factory import ServiceFactory
        from app.services.order_service import OrderService
        from app.services.product_service import ProductService
        from app.services.user_service import UserService


        def get_user_service(
            db: Annotated[AsyncSession, Depends(get_db)]
        ) -> UserService:
            '''
            Inyecta UserService usando Factory.
            Facade (GoF): Simplifica acceso a factory.
            Low Coupling (GRASP): Endpoints no conocen cómo crear servicios.
            '''
            return ServiceFactory.create_user_service(db)


        def get_product_service(
            db: Annotated[AsyncSession, Depends(get_db)]
        ) -> ProductService:
            '''Inyecta ProductService usando Factory'''
            return ServiceFactory.create_product_service(db)


        def get_order_service(
            db: Annotated[AsyncSession, Depends(get_db)]
        ) -> OrderService:
            '''Inyecta OrderService usando Factory'''
            return ServiceFactory.create_order_service(db)
    """),
    )


def _create_api_router_template() -> FileTemplate:
    """Main router that aggregates all endpoints."""
    return FileTemplate(
        "app/api/v1/router.py",
        dedent("""
        from fastapi import APIRouter

        from app.api.v1.endpoints import users, products, orders


        api_router = APIRouter()

        # Incluir routers de cada recurso
        api_router.include_router(
            users.router,
            prefix="/users",
            tags=["users"],
        )

        api_router.include_router(
            products.router,
            prefix="/products",
            tags=["products"],
        )

        api_router.include_router(
            orders.router,
            prefix="/orders",
            tags=["orders"],
        )
    """),
    )


# ==================== app/api/v1/endpoints/ ====================


def _create_users_endpoint_template() -> FileTemplate:
    """CRUD endpoints for users."""
    return FileTemplate(
        "app/api/v1/endpoints/users.py",
        dedent("""
        from typing import Annotated

        from fastapi import APIRouter, Depends, HTTPException, status

        from app.api.dependencies import get_user_service
        from app.core.exceptions import (
            DuplicateEmailError,
            InstanceNotFoundError,
            ValidationError,
        )
        from app.schemas.user import UserCreate, UserResponse, UserUpdate
        from app.services.user_service import UserService


        router = APIRouter()


        @router.get("/", response_model=list[UserResponse])
        async def get_users(
            skip: int = 0,
            limit: int = 100,
            service: Annotated[UserService, Depends(get_user_service)] = None,
        ):
            '''
            Controller (GRASP): Solo maneja HTTP.
            Single Responsibility (SOLID): Solo endpoints.

            Obtiene lista de usuarios con paginación.
            '''
            return await service.get_all(skip, limit)


        @router.get("/{user_id}", response_model=UserResponse)
        async def get_user(
            user_id: int,
            service: Annotated[UserService, Depends(get_user_service)] = None,
        ):
            '''Obtiene usuario por ID'''
            try:
                return await service.get_by_id(user_id)
            except InstanceNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc))


        @router.post(
            "/",
            response_model=UserResponse,
            status_code=status.HTTP_201_CREATED,
        )
        async def create_user(
            user: UserCreate,
            service: Annotated[UserService, Depends(get_user_service)] = None,
        ):
            '''Crea nuevo usuario'''
            try:
                return await service.create(user)
            except DuplicateEmailError as exc:
                raise HTTPException(status_code=400, detail=str(exc))
            except ValidationError as exc:
                raise HTTPException(status_code=400, detail=str(exc))


        @router.put("/{user_id}", response_model=UserResponse)
        async def update_user(
            user_id: int,
            user: UserUpdate,
            service: Annotated[UserService, Depends(get_user_service)] = None,
        ):
            '''Actualiza usuario'''
            try:
                return await service.update(user_id, user)
            except InstanceNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc))
            except DuplicateEmailError as exc:
                raise HTTPException(status_code=400, detail=str(exc))


        @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_user(
            user_id: int,
            service: Annotated[UserService, Depends(get_user_service)] = None,
        ):
            '''Elimina usuario'''
            try:
                await service.delete(user_id)
            except InstanceNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc))
    """),
    )


def _create_products_endpoint_template() -> FileTemplate:
    """CRUD endpoints for products."""
    return FileTemplate(
        "app/api/v1/endpoints/products.py",
        dedent("""
        from typing import Annotated

        from fastapi import APIRouter, Depends

        from app.api.dependencies import get_product_service
        from app.schemas.product import ProductResponse
        from app.services.product_service import ProductService


        router = APIRouter()


        @router.get("/", response_model=list[ProductResponse])
        async def list_products(
            skip: int = 0,
            limit: int = 100,
            service: Annotated[ProductService, Depends(get_product_service)] = None,
        ):
            '''
            Endpoint de ejemplo para productos.
            Implementa CRUD completo según necesidad.
            '''
            return await service.get_all(skip=skip, limit=limit)
    """),
    )


def _create_orders_endpoint_template() -> FileTemplate:
    """CRUD endpoints for orders."""
    return FileTemplate(
        "app/api/v1/endpoints/orders.py",
        dedent("""
        from typing import Annotated

        from fastapi import APIRouter, Depends

        from app.api.dependencies import get_order_service
        from app.schemas.order import OrderResponse
        from app.services.order_service import OrderService


        router = APIRouter()


        @router.get("/", response_model=list[OrderResponse])
        async def list_orders(
            skip: int = 0,
            limit: int = 100,
            service: Annotated[OrderService, Depends(get_order_service)] = None,
        ):
            '''
            Endpoint de ejemplo para órdenes.
            Implementa CRUD completo según necesidad.
            '''
            return await service.get_all(skip=skip, limit=limit)
    """),
    )
