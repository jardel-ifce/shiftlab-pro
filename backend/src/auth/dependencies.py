"""
Dependências de autenticação para FastAPI.

Este módulo fornece funções que podem ser usadas como dependências
em endpoints para verificar autenticação e autorização.

Uso:
    @router.get("/protected")
    async def protected_route(
        current_user: User = Depends(get_current_user)
    ):
        return {"message": f"Olá, {current_user.nome}!"}

    @router.get("/admin-only")
    async def admin_route(
        current_user: User = Depends(get_current_admin_user)
    ):
        return {"message": "Você é admin!"}
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User, UserRole
from src.auth.security import decode_token
from src.database import get_db

# =============================================================================
# CONFIGURAÇÃO DO OAUTH2
# =============================================================================

# OAuth2PasswordBearer extrai o token do header Authorization
# tokenUrl é o endpoint de login (para documentação do Swagger)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="JWT",
    description="Token JWT obtido no login"
)


# =============================================================================
# DEPENDÊNCIAS
# =============================================================================

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Obtém o usuário atual a partir do token JWT.

    Esta dependência:
    1. Extrai o token do header Authorization
    2. Decodifica e valida o token
    3. Busca o usuário no banco de dados
    4. Verifica se o usuário está ativo

    Args:
        token: Token JWT extraído do header
        db: Sessão do banco de dados

    Returns:
        User: Usuário autenticado

    Raises:
        HTTPException 401: Se token inválido ou usuário não encontrado
        HTTPException 403: Se usuário desativado

    Example:
        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    """
    # Define exceção padrão para credenciais inválidas
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decodifica o token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # Extrai o email (subject) do token
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    # Busca o usuário no banco
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    # Verifica se está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário desativado"
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Obtém o usuário atual verificando se está ativo.

    Wrapper de get_current_user que garante que o usuário está ativo.
    Útil para endpoints que exigem usuário ativo.

    Args:
        current_user: Usuário obtido do token

    Returns:
        User: Usuário autenticado e ativo

    Raises:
        HTTPException 403: Se usuário não está ativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Obtém o usuário atual verificando se é administrador.

    Use esta dependência em endpoints que só admins podem acessar.

    Args:
        current_user: Usuário obtido do token

    Returns:
        User: Usuário administrador autenticado

    Raises:
        HTTPException 403: Se usuário não é admin

    Example:
        @router.delete("/users/{user_id}")
        async def delete_user(
            user_id: int,
            admin: User = Depends(get_current_admin_user)
        ):
            # Só admins chegam aqui
            ...
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    return current_user


# =============================================================================
# TYPE ALIASES PARA USO NOS ENDPOINTS
# =============================================================================

# Uso: async def endpoint(user: CurrentUser):
CurrentUser = Annotated[User, Depends(get_current_user)]

# Uso: async def endpoint(user: CurrentActiveUser):
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]

# Uso: async def endpoint(admin: CurrentAdminUser):
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]


# =============================================================================
# DEPENDÊNCIAS OPCIONAIS
# =============================================================================

async def get_optional_current_user(
    token: Annotated[str | None, Depends(OAuth2PasswordBearer(
        tokenUrl="/api/v1/auth/login",
        auto_error=False  # Não lança erro se token não presente
    ))],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User | None:
    """
    Obtém o usuário atual se estiver autenticado, ou None.

    Útil para endpoints públicos que têm comportamento diferente
    para usuários autenticados.

    Args:
        token: Token JWT (opcional)
        db: Sessão do banco de dados

    Returns:
        User se autenticado, None caso contrário

    Example:
        @router.get("/items")
        async def list_items(user: User | None = Depends(get_optional_current_user)):
            if user:
                # Retorna items do usuário
                ...
            else:
                # Retorna items públicos
                ...
    """
    if token is None:
        return None

    payload = decode_token(token)
    if payload is None:
        return None

    email = payload.get("sub")
    if email is None:
        return None

    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    return user if user and user.is_active else None
