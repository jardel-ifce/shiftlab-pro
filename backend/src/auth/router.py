"""
Rotas de autenticação da API.

Endpoints:
- POST /auth/login: Autenticar usuário e obter token
- POST /auth/register: Registrar novo usuário (apenas admin)
- GET /auth/me: Obter dados do usuário atual
- POST /auth/change-password: Alterar senha
- GET /auth/users: Listar usuários (apenas admin)
- PATCH /auth/users/{id}: Atualizar usuário
- DELETE /auth/users/{id}: Desativar usuário (apenas admin)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import (
    CurrentActiveUser,
    CurrentAdminUser,
    CurrentUser,
)
from src.auth.schemas import (
    LoginRequest,
    MessageResponse,
    PasswordChange,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from src.auth.service import AuthService
from src.database import get_db

# =============================================================================
# CONFIGURAÇÃO DO ROUTER
# =============================================================================

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
    responses={
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão"},
    }
)


# =============================================================================
# ENDPOINTS PÚBLICOS
# =============================================================================

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Fazer login",
    description="Autentica o usuário e retorna um token JWT."
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> TokenResponse:
    """
    Autentica um usuário com email e senha.

    - **username**: Email do usuário (campo padrão OAuth2)
    - **password**: Senha do usuário

    Retorna um token JWT que deve ser usado no header:
    `Authorization: Bearer <token>`
    """
    service = AuthService(db)

    try:
        # OAuth2PasswordRequestForm usa 'username', mas nosso sistema usa email
        login_data = LoginRequest(email=form_data.username, password=form_data.password)
        return await service.authenticate(login_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/login/json",
    response_model=TokenResponse,
    summary="Fazer login (JSON)",
    description="Versão alternativa do login que aceita JSON no corpo."
)
async def login_json(
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> TokenResponse:
    """
    Autentica um usuário com email e senha via JSON.

    Alternativa ao endpoint OAuth2 para clientes que preferem JSON.
    """
    service = AuthService(db)

    try:
        return await service.authenticate(login_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# =============================================================================
# ENDPOINTS AUTENTICADOS
# =============================================================================

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obter usuário atual",
    description="Retorna os dados do usuário autenticado."
)
async def get_current_user_info(
    current_user: CurrentUser
) -> UserResponse:
    """
    Retorna os dados do usuário que está autenticado.

    Útil para obter informações do perfil e verificar a sessão.
    """
    return UserResponse.model_validate(current_user)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Alterar senha",
    description="Altera a senha do usuário atual."
)
async def change_password(
    password_data: PasswordChange,
    current_user: CurrentActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> MessageResponse:
    """
    Altera a senha do usuário autenticado.

    - **current_password**: Senha atual (para confirmação)
    - **new_password**: Nova senha (mínimo 8 caracteres)
    """
    service = AuthService(db)

    try:
        await service.change_password(
            user=current_user,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        return MessageResponse(message="Senha alterada com sucesso")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# ENDPOINTS DE ADMIN
# =============================================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria um novo usuário no sistema. Apenas administradores."
)
async def register_user(
    user_data: UserCreate,
    current_user: CurrentAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserResponse:
    """
    Registra um novo usuário no sistema.

    Apenas administradores podem criar novos usuários.

    - **email**: Email único do usuário
    - **password**: Senha (mínimo 8 caracteres, 1 maiúscula, 1 minúscula, 1 número)
    - **nome**: Nome completo
    - **role**: Papel no sistema (admin ou funcionario)
    """
    service = AuthService(db)

    try:
        user = await service.create_user(user_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="Listar usuários",
    description="Lista todos os usuários do sistema. Apenas administradores."
)
async def list_users(
    current_user: CurrentAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False
) -> list[UserResponse]:
    """
    Lista todos os usuários do sistema.

    - **skip**: Quantos registros pular (para paginação)
    - **limit**: Máximo de registros a retornar
    - **include_inactive**: Se True, inclui usuários desativados
    """
    service = AuthService(db)
    users = await service.get_all_users(
        skip=skip,
        limit=limit,
        only_active=not include_inactive
    )
    return [UserResponse.model_validate(user) for user in users]


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Obter usuário por ID",
    description="Retorna os dados de um usuário específico."
)
async def get_user(
    user_id: int,
    current_user: CurrentActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserResponse:
    """
    Retorna os dados de um usuário específico.

    Usuários comuns só podem ver seus próprios dados.
    Administradores podem ver qualquer usuário.
    """
    # Verifica permissão
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para ver este usuário"
        )

    service = AuthService(db)
    user = await service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return UserResponse.model_validate(user)


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Atualizar usuário",
    description="Atualiza os dados de um usuário."
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: CurrentActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserResponse:
    """
    Atualiza os dados de um usuário.

    - Usuários comuns só podem atualizar a si mesmos
    - Apenas admins podem alterar o role para admin
    """
    service = AuthService(db)

    try:
        user = await service.update_user(
            user_id=user_id,
            user_data=user_data,
            current_user=current_user
        )
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/users/{user_id}",
    response_model=MessageResponse,
    summary="Desativar usuário",
    description="Desativa um usuário do sistema. Apenas administradores."
)
async def deactivate_user(
    user_id: int,
    current_user: CurrentAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> MessageResponse:
    """
    Desativa um usuário do sistema.

    O usuário não é excluído, apenas marcado como inativo.
    Isso impede que ele faça login, mas mantém o histórico.
    """
    service = AuthService(db)

    try:
        user = await service.deactivate_user(
            user_id=user_id,
            current_user=current_user
        )
        return MessageResponse(
            message=f"Usuário {user.nome} desativado com sucesso"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
