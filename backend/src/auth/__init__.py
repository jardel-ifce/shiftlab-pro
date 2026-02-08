"""
Módulo de Autenticação - ShiftLab Pro.

Este módulo fornece toda a infraestrutura de autenticação e autorização:
- Modelo de usuário (User)
- Autenticação via JWT
- Controle de acesso baseado em papéis (RBAC)

Componentes principais:
- models: Entidade User para o banco de dados
- schemas: Validação de entrada/saída (Pydantic)
- security: Hash de senhas e tokens JWT
- service: Lógica de negócio de autenticação
- dependencies: Proteção de rotas (get_current_user)
- router: Endpoints da API

Uso básico:
    # No main.py
    from src.auth.router import router as auth_router
    app.include_router(auth_router, prefix="/api/v1")

    # Em outros routers (proteger endpoint)
    from src.auth.dependencies import CurrentUser

    @router.get("/protected")
    async def protected(user: CurrentUser):
        return {"user": user.nome}
"""

from src.auth.dependencies import (
    CurrentActiveUser,
    CurrentAdminUser,
    CurrentUser,
    get_current_admin_user,
    get_current_user,
)
from src.auth.models import User, UserRole
from src.auth.router import router
from src.auth.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from src.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from src.auth.service import AuthService

__all__ = [
    # Models
    "User",
    "UserRole",
    # Schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "LoginRequest",
    "TokenResponse",
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    # Service
    "AuthService",
    # Dependencies
    "get_current_user",
    "get_current_admin_user",
    "CurrentUser",
    "CurrentActiveUser",
    "CurrentAdminUser",
    # Router
    "router",
]
