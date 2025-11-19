"""
Templates para archivos de testing.
Incluye fixtures, tests unitarios y de integración.
"""

from generator.templates.base import FileTemplate, dedent


def get_test_templates() -> list[FileTemplate]:
    """
    Factory Method (GoF): Crea conjunto de templates para tests/.
    
    Returns:
        Lista de FileTemplate con archivos de testing.
    """
    return [
        # Root tests/
        FileTemplate("tests/__init__.py", dedent("""
            # Paquete de tests.
        """)),
        
        _create_conftest_template(),
        
        # tests/unit/
        FileTemplate("tests/unit/__init__.py", dedent("""
            # Tests unitarios.
        """)),
        
        _create_unit_test_services_template(),
        _create_unit_test_repositories_template(),
        
        # tests/integration/
        FileTemplate("tests/integration/__init__.py", dedent("""
            # Tests de integración.
        """)),
        
        _create_integration_test_users_endpoint_template(),
    ]


# ==================== conftest.py ====================

def _create_conftest_template() -> FileTemplate:
    """Fixtures compartidos para tests async."""
    return FileTemplate("tests/conftest.py", dedent("""
        import asyncio
        from typing import AsyncGenerator, Generator

        import pytest
        from httpx import AsyncClient, ASGITransport
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

        from app.main import app
        from app.db.base import Base
        from app.db.session import get_db


        # URL de base de datos de test (en memoria o test DB)
        TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


        @pytest.fixture(scope="session")
        def event_loop() -> Generator:
            '''
            Fixture para event loop.
            Necesario para tests async con pytest-asyncio.
            '''
            loop = asyncio.get_event_loop_policy().new_event_loop()
            yield loop
            loop.close()


        @pytest.fixture(scope="function")
        async def engine():
            '''
            Fixture para crear engine de test.
            '''
            engine = create_async_engine(
                TEST_DATABASE_URL,
                echo=False,
                future=True,
            )
            
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            yield engine
            
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            
            await engine.dispose()


        @pytest.fixture(scope="function")
        async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
            '''
            Fixture para crear sesión de DB de test.
            '''
            async_session = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            async with async_session() as session:
                yield session


        @pytest.fixture(scope="function")
        async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
            '''
            Fixture para crear cliente HTTP de test.
            Inyecta DB de test en la app.
            '''
            async def override_get_db():
                yield db_session
            
            app.dependency_overrides[get_db] = override_get_db
            
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as ac:
                yield ac
            
            app.dependency_overrides.clear()
    """))


# ==================== tests/unit/ ====================

def _create_unit_test_services_template() -> FileTemplate:
    """Tests unitarios para services con mocks."""
    return FileTemplate("tests/unit/test_services.py", dedent("""
        from unittest.mock import AsyncMock, MagicMock

        import pytest

        from app.core.exceptions import DuplicateEmailError, InstanceNotFoundError, ValidationError
        from app.models.user import User
        from app.schemas.user import UserCreate, UserUpdate
        from app.services.user_service import UserService


        @pytest.fixture
        def mock_repository():
            '''Mock de UserRepository'''
            return AsyncMock()


        @pytest.fixture
        def mock_cache():
            '''Mock de CacheService'''
            cache = AsyncMock()
            cache.get.return_value = None  # Default: cache miss
            return cache


        @pytest.fixture
        def user_service(mock_repository, mock_cache):
            '''UserService con dependencias mockeadas'''
            return UserService(mock_repository, mock_cache)


        class TestUserServiceGetAll:
            '''Tests para UserService.get_all()'''
            
            @pytest.mark.asyncio
            async def test_get_all_without_cache(self, user_service, mock_repository, mock_cache):
                '''Test get_all cuando no hay cache'''
                # Arrange
                mock_users = [
                    User(id=1, email="user1@example.com", name="User 1", hashed_password="hash1"),
                    User(id=2, email="user2@example.com", name="User 2", hashed_password="hash2"),
                ]
                mock_repository.get_all.return_value = mock_users
                mock_cache.get.return_value = None
                
                # Act
                result = await user_service.get_all(skip=0, limit=10)
                
                # Assert
                assert len(result) == 2
                assert result[0].id == 1
                assert result[1].id == 2
                mock_repository.get_all.assert_called_once_with(0, 10)
                mock_cache.set.assert_called_once()
            
            @pytest.mark.asyncio
            async def test_get_all_with_cache(self, user_service, mock_repository, mock_cache):
                '''Test get_all cuando hay cache hit'''
                # Arrange
                cached_data = [
                    {{"id": 1, "email": "user1@example.com", "name": "User 1", "is_active": True}},
                ]
                mock_cache.get.return_value = cached_data
                
                # Act
                result = await user_service.get_all()
                
                # Assert
                assert len(result) == 1
                assert result[0].id == 1
                mock_repository.get_all.assert_not_called()  # No debe llamar a DB


        class TestUserServiceGetById:
            '''Tests para UserService.get_by_id()'''
            
            @pytest.mark.asyncio
            async def test_get_by_id_found(self, user_service, mock_repository):
                '''Test get_by_id cuando el usuario existe'''
                # Arrange
                mock_user = User(
                    id=1,
                    email="test@example.com",
                    name="Test User",
                    hashed_password="hash"
                )
                mock_repository.get_by_id.return_value = mock_user
                
                # Act
                result = await user_service.get_by_id(1)
                
                # Assert
                assert result.id == 1
                assert result.email == "test@example.com"
                mock_repository.get_by_id.assert_called_once_with(1)
            
            @pytest.mark.asyncio
            async def test_get_by_id_not_found(self, user_service, mock_repository):
                '''Test get_by_id cuando el usuario no existe'''
                # Arrange
                mock_repository.get_by_id.return_value = None
                
                # Act & Assert
                with pytest.raises(InstanceNotFoundError, match="User with id 999 not found"):
                    await user_service.get_by_id(999)


        class TestUserServiceCreate:
            '''Tests para UserService.create()'''
            
            @pytest.mark.asyncio
            async def test_create_success(self, user_service, mock_repository):
                '''Test create cuando todo es válido'''
                # Arrange
                user_data = UserCreate(
                    email="new@example.com",
                    name="New User",
                    password="securepassword123"
                )
                mock_repository.email_exists.return_value = False
                mock_repository.create.return_value = User(
                    id=1,
                    email=user_data.email,
                    name=user_data.name,
                    hashed_password="hashed"
                )
                
                # Act
                result = await user_service.create(user_data)
                
                # Assert
                assert result.id == 1
                assert result.email == "new@example.com"
                mock_repository.email_exists.assert_called_once_with("new@example.com")
                mock_repository.create.assert_called_once()
            
            @pytest.mark.asyncio
            async def test_create_duplicate_email(self, user_service, mock_repository):
                '''Test create cuando el email ya existe'''
                # Arrange
                user_data = UserCreate(
                    email="existing@example.com",
                    name="User",
                    password="password123"
                )
                mock_repository.email_exists.return_value = True
                
                # Act & Assert
                with pytest.raises(DuplicateEmailError):
                    await user_service.create(user_data)
            
            @pytest.mark.asyncio
            async def test_create_short_password(self, user_service, mock_repository):
                '''Test create cuando el password es muy corto'''
                # Arrange
                user_data = UserCreate(
                    email="test@example.com",
                    name="User",
                    password="short"
                )
                mock_repository.email_exists.return_value = False
                
                # Act & Assert
                with pytest.raises(ValidationError, match="Password must be at least 8 characters"):
                    await user_service.create(user_data)
    """))


def _create_unit_test_repositories_template() -> FileTemplate:
    """Tests unitarios para repositories."""
    return FileTemplate("tests/unit/test_repositories.py", dedent("""
        import pytest

        from app.models.user import User
        from app.repositories.user_repository import UserRepository


        @pytest.mark.asyncio
        async def test_user_repository_create(db_session):
            '''Test crear usuario con repository'''
            # Arrange
            repository = UserRepository(db_session)
            user = User(
                email="test@example.com",
                name="Test User",
                hashed_password="hashedpassword123"
            )
            
            # Act
            created_user = await repository.create(user)
            
            # Assert
            assert created_user.id is not None
            assert created_user.email == "test@example.com"
            assert created_user.name == "Test User"


        @pytest.mark.asyncio
        async def test_user_repository_get_by_id(db_session):
            '''Test obtener usuario por ID'''
            # Arrange
            repository = UserRepository(db_session)
            user = User(
                email="test@example.com",
                name="Test User",
                hashed_password="hashedpassword123"
            )
            created_user = await repository.create(user)
            
            # Act
            found_user = await repository.get_by_id(created_user.id)
            
            # Assert
            assert found_user is not None
            assert found_user.id == created_user.id
            assert found_user.email == created_user.email


        @pytest.mark.asyncio
        async def test_user_repository_get_by_email(db_session):
            '''Test obtener usuario por email'''
            # Arrange
            repository = UserRepository(db_session)
            user = User(
                email="unique@example.com",
                name="Test User",
                hashed_password="hashedpassword123"
            )
            await repository.create(user)
            
            # Act
            found_user = await repository.get_by_email("unique@example.com")
            
            # Assert
            assert found_user is not None
            assert found_user.email == "unique@example.com"


        @pytest.mark.asyncio
        async def test_user_repository_email_exists(db_session):
            '''Test verificar si email existe'''
            # Arrange
            repository = UserRepository(db_session)
            user = User(
                email="exists@example.com",
                name="Test User",
                hashed_password="hashedpassword123"
            )
            await repository.create(user)
            
            # Act & Assert
            assert await repository.email_exists("exists@example.com") is True
            assert await repository.email_exists("notexists@example.com") is False


        @pytest.mark.asyncio
        async def test_user_repository_get_all(db_session):
            '''Test obtener todos los usuarios con paginación'''
            # Arrange
            repository = UserRepository(db_session)
            for i in range(5):
                user = User(
                    email=f"user{{i}}@example.com",
                    name=f"User {{i}}",
                    hashed_password="hashedpassword123"
                )
                await repository.create(user)
            
            # Act
            users = await repository.get_all(skip=0, limit=3)
            
            # Assert
            assert len(users) == 3
    """))


# ==================== tests/integration/ ====================

def _create_integration_test_users_endpoint_template() -> FileTemplate:
    """Tests E2E para endpoints de users."""
    return FileTemplate("tests/integration/test_users_endpoint.py", dedent("""
        import pytest
        from httpx import AsyncClient


        @pytest.mark.asyncio
        async def test_create_user(client: AsyncClient):
            '''Test E2E: Crear usuario'''
            # Arrange
            user_data = {{
                "email": "newuser@example.com",
                "name": "New User",
                "password": "securepassword123"
            }}
            
            # Act
            response = await client.post("/api/v1/users/", json=user_data)
            
            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == "newuser@example.com"
            assert data["name"] == "New User"
            assert "id" in data
            assert "password" not in data  # No debe retornar password


        @pytest.mark.asyncio
        async def test_get_users(client: AsyncClient):
            '''Test E2E: Obtener lista de usuarios'''
            # Arrange - Crear algunos usuarios primero
            for i in range(3):
                await client.post("/api/v1/users/", json={{
                    "email": f"user{{i}}@example.com",
                    "name": f"User {{i}}",
                    "password": "password123"
                }})
            
            # Act
            response = await client.get("/api/v1/users/")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data) >= 3


        @pytest.mark.asyncio
        async def test_get_user_by_id(client: AsyncClient):
            '''Test E2E: Obtener usuario por ID'''
            # Arrange - Crear usuario
            create_response = await client.post("/api/v1/users/", json={{
                "email": "getuser@example.com",
                "name": "Get User",
                "password": "password123"
            }})
            user_id = create_response.json()["id"]
            
            # Act
            response = await client.get(f"/api/v1/users/{{user_id}}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == user_id
            assert data["email"] == "getuser@example.com"


        @pytest.mark.asyncio
        async def test_get_user_not_found(client: AsyncClient):
            '''Test E2E: Obtener usuario inexistente'''
            # Act
            response = await client.get("/api/v1/users/99999")
            
            # Assert
            assert response.status_code == 404


        @pytest.mark.asyncio
        async def test_update_user(client: AsyncClient):
            '''Test E2E: Actualizar usuario'''
            # Arrange - Crear usuario
            create_response = await client.post("/api/v1/users/", json={{
                "email": "updateuser@example.com",
                "name": "Update User",
                "password": "password123"
            }})
            user_id = create_response.json()["id"]
            
            # Act
            update_data = {{"name": "Updated Name"}}
            response = await client.put(f"/api/v1/users/{{user_id}}", json=update_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Name"
            assert data["email"] == "updateuser@example.com"  # Email no cambió


        @pytest.mark.asyncio
        async def test_delete_user(client: AsyncClient):
            '''Test E2E: Eliminar usuario'''
            # Arrange - Crear usuario
            create_response = await client.post("/api/v1/users/", json={{
                "email": "deleteuser@example.com",
                "name": "Delete User",
                "password": "password123"
            }})
            user_id = create_response.json()["id"]
            
            # Act
            response = await client.delete(f"/api/v1/users/{{user_id}}")
            
            # Assert
            assert response.status_code == 204
            
            # Verificar que ya no existe
            get_response = await client.get(f"/api/v1/users/{{user_id}}")
            assert get_response.status_code == 404


        @pytest.mark.asyncio
        async def test_create_user_duplicate_email(client: AsyncClient):
            '''Test E2E: Crear usuario con email duplicado'''
            # Arrange - Crear usuario
            user_data = {{
                "email": "duplicate@example.com",
                "name": "User",
                "password": "password123"
            }}
            await client.post("/api/v1/users/", json=user_data)
            
            # Act - Intentar crear otro con mismo email
            response = await client.post("/api/v1/users/", json=user_data)
            
            # Assert
            assert response.status_code == 400
            assert "already exists" in response.json()["detail"]


        @pytest.mark.asyncio
        async def test_create_user_short_password(client: AsyncClient):
            '''Test E2E: Crear usuario con password muy corto'''
            # Arrange
            user_data = {{
                "email": "test@example.com",
                "name": "Test User",
                "password": "short"
            }}
            
            # Act
            response = await client.post("/api/v1/users/", json=user_data)
            
            # Assert
            assert response.status_code == 400
            assert "at least 8 characters" in response.json()["detail"]
    """))

