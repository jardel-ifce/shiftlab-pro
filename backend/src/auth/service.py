"""
Serviço de autenticação.

Este módulo contém a lógica de negócio para:
- Registro de novos usuários
- Autenticação (login)
- Gerenciamento de usuários

O serviço é a camada entre os endpoints (router) e o banco de dados.
Toda a lógica de negócio deve ficar aqui, não nos endpoints.
"""

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User, UserRole
from src.auth.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from src.auth.security import (
    create_access_token,
    get_token_expiration_seconds,
    hash_password,
    verify_password,
)
from src.config import settings


class AuthService:
    """
    Serviço de autenticação e gerenciamento de usuários.

    Responsabilidades:
    - Criar novos usuários com validação de email único
    - Autenticar usuários (verificar credenciais)
    - Gerar tokens JWT
    - Buscar e atualizar usuários

    Example:
        service = AuthService(db_session)
        user = await service.create_user(user_data)
        token = await service.authenticate(login_data)
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa o serviço com uma sessão do banco.

        Args:
            db: Sessão assíncrona do SQLAlchemy
        """
        self.db = db

    # =========================================================================
    # MÉTODOS DE BUSCA
    # =========================================================================

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Busca um usuário pelo email.

        Args:
            email: Email do usuário

        Returns:
            User se encontrado, None caso contrário
        """
        query = select(User).where(User.email == email.lower())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Busca um usuário pelo ID.

        Args:
            user_id: ID do usuário

        Returns:
            User se encontrado, None caso contrário
        """
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = True
    ) -> list[User]:
        """
        Lista todos os usuários com paginação.

        Args:
            skip: Quantos registros pular (offset)
            limit: Máximo de registros a retornar
            only_active: Se True, retorna apenas usuários ativos

        Returns:
            Lista de usuários
        """
        query = select(User)

        if only_active:
            query = query.where(User.is_active == True)  # noqa: E712

        query = query.offset(skip).limit(limit).order_by(User.nome)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # =========================================================================
    # MÉTODOS DE CRIAÇÃO
    # =========================================================================

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Cria um novo usuário no sistema.

        Validações:
        - Email deve ser único
        - Senha é automaticamente hasheada

        Args:
            user_data: Dados do usuário (schema UserCreate)

        Returns:
            User: Usuário criado

        Raises:
            ValueError: Se email já estiver cadastrado
        """
        # Verifica se email já existe
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email já cadastrado no sistema")

        # Cria o usuário com senha hasheada
        user = User(
            email=user_data.email.lower(),
            hashed_password=hash_password(user_data.password),
            nome=user_data.nome,
            role=user_data.role,
            is_active=True,
        )

        self.db.add(user)
        await self.db.flush()  # Gera o ID sem commitar
        await self.db.refresh(user)  # Carrega campos gerados (created_at)

        return user

    async def create_first_admin(self) -> User | None:
        """
        Cria o primeiro usuário administrador se não existir nenhum.

        Usado na inicialização do sistema para garantir que
        sempre exista pelo menos um admin.

        Returns:
            User: Admin criado, ou None se já existir
        """
        # Verifica se já existe algum admin
        query = select(User).where(User.role == UserRole.ADMIN)
        result = await self.db.execute(query)
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            return None

        # Cria o admin usando dados do .env
        admin = User(
            email=settings.FIRST_ADMIN_EMAIL.lower(),
            hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
            nome=settings.FIRST_ADMIN_NAME,
            role=UserRole.ADMIN,
            is_active=True,
        )

        self.db.add(admin)
        await self.db.flush()
        await self.db.refresh(admin)

        return admin

    # =========================================================================
    # MÉTODOS DE AUTENTICAÇÃO
    # =========================================================================

    async def authenticate(self, login_data: LoginRequest) -> TokenResponse:
        """
        Autentica um usuário e retorna o token JWT.

        Validações:
        - Email deve existir no sistema
        - Senha deve estar correta
        - Usuário deve estar ativo

        Args:
            login_data: Email e senha para login

        Returns:
            TokenResponse: Token JWT e dados do usuário

        Raises:
            ValueError: Se credenciais inválidas ou usuário inativo
        """
        # Busca o usuário
        user = await self.get_user_by_email(login_data.email)

        # Verifica se existe e se a senha está correta
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise ValueError("Email ou senha incorretos")

        # Verifica se está ativo
        if not user.is_active:
            raise ValueError("Usuário desativado. Entre em contato com o administrador.")

        # Gera o token
        role_value = user.role.value if hasattr(user.role, 'value') else user.role
        access_token = create_access_token(
            data={
                "sub": user.email,
                "role": role_value,
                "user_id": user.id,
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=get_token_expiration_seconds(),
            user=UserResponse.model_validate(user)
        )

    # =========================================================================
    # MÉTODOS DE ATUALIZAÇÃO
    # =========================================================================

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdate,
        current_user: User
    ) -> User:
        """
        Atualiza dados de um usuário.

        Regras:
        - Usuário comum só pode atualizar a si mesmo
        - Admin pode atualizar qualquer usuário
        - Não pode alterar role para admin (apenas admin pode)

        Args:
            user_id: ID do usuário a atualizar
            user_data: Dados a atualizar
            current_user: Usuário que está fazendo a requisição

        Returns:
            User: Usuário atualizado

        Raises:
            ValueError: Se não encontrado ou sem permissão
        """
        # Busca o usuário
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")

        # Verifica permissão
        if not current_user.is_admin and current_user.id != user_id:
            raise ValueError("Sem permissão para atualizar este usuário")

        # Atualiza campos enviados
        update_data = user_data.model_dump(exclude_unset=True)

        # Se está tentando mudar role para admin, precisa ser admin
        if "role" in update_data and update_data["role"] == UserRole.ADMIN:
            if not current_user.is_admin:
                raise ValueError("Apenas administradores podem promover a admin")

        # Se está atualizando senha, faz hash
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        # Se está atualizando email, normaliza e verifica duplicidade
        if "email" in update_data:
            new_email = update_data["email"].lower()
            existing = await self.get_user_by_email(new_email)
            if existing and existing.id != user_id:
                raise ValueError("Este email já está em uso")
            update_data["email"] = new_email

        # Aplica atualizações
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Altera a senha de um usuário.

        Args:
            user: Usuário que está alterando a senha
            current_password: Senha atual
            new_password: Nova senha

        Returns:
            bool: True se alterado com sucesso

        Raises:
            ValueError: Se senha atual incorreta
        """
        # Verifica senha atual
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Senha atual incorreta")

        # Atualiza para nova senha
        user.hashed_password = hash_password(new_password)
        await self.db.flush()

        return True

    async def deactivate_user(self, user_id: int, current_user: User) -> User:
        """
        Desativa um usuário (soft delete).

        Args:
            user_id: ID do usuário a desativar
            current_user: Usuário que está fazendo a requisição

        Returns:
            User: Usuário desativado

        Raises:
            ValueError: Se não encontrado ou sem permissão
        """
        if not current_user.is_admin:
            raise ValueError("Apenas administradores podem desativar usuários")

        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")

        if user.id == current_user.id:
            raise ValueError("Você não pode desativar a si mesmo")

        user.is_active = False
        await self.db.flush()
        await self.db.refresh(user)

        return user
