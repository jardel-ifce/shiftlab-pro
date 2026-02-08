"""
Schemas Pydantic para autenticação.

Define os formatos de dados para entrada e saída da API.
Pydantic valida automaticamente os dados recebidos.

Schemas:
- UserCreate: Dados para criar novo usuário
- UserUpdate: Dados para atualizar usuário
- UserResponse: Dados retornados ao cliente (sem senha!)
- LoginRequest: Dados para fazer login
- TokenResponse: Token JWT retornado após login
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRole(str, Enum):
    """Papéis disponíveis para usuários."""
    ADMIN = "admin"
    FUNCIONARIO = "funcionario"


# =============================================================================
# SCHEMAS DE ENTRADA (REQUEST)
# =============================================================================

class UserCreate(BaseModel):
    """
    Schema para criação de novo usuário.

    Usado em: POST /auth/register

    Validações:
    - email: Formato válido de email
    - password: Mínimo 8 caracteres
    - nome: Mínimo 3 caracteres
    - role: Opcional (padrão: funcionario)
    """

    email: EmailStr = Field(
        ...,
        description="Email válido do usuário",
        examples=["joao@oficina.com"]
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Senha com mínimo 8 caracteres",
        examples=["Senha@123"]
    )

    nome: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nome completo do usuário",
        examples=["João Silva"]
    )

    role: UserRole = Field(
        default=UserRole.FUNCIONARIO,
        description="Papel do usuário no sistema"
    )

    @field_validator("nome")
    @classmethod
    def nome_deve_ter_espacos(cls, v: str) -> str:
        """Remove espaços extras e capitaliza."""
        return " ".join(v.split()).title()

    @field_validator("password")
    @classmethod
    def senha_deve_ser_forte(cls, v: str) -> str:
        """
        Valida força da senha.

        Requisitos:
        - Mínimo 8 caracteres (já validado pelo Field)
        - Pelo menos uma letra maiúscula
        - Pelo menos uma letra minúscula
        - Pelo menos um número
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")
        if not any(c.islower() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Senha deve conter pelo menos um número")
        return v


class UserUpdate(BaseModel):
    """
    Schema para atualização de usuário.

    Usado em: PATCH /users/{id}

    Todos os campos são opcionais - apenas os enviados são atualizados.
    """

    email: EmailStr | None = Field(
        default=None,
        description="Novo email do usuário"
    )

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=100,
        description="Nova senha"
    )

    nome: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
        description="Novo nome"
    )

    role: UserRole | None = Field(
        default=None,
        description="Novo papel"
    )

    is_active: bool | None = Field(
        default=None,
        description="Ativar/desativar usuário"
    )


class LoginRequest(BaseModel):
    """
    Schema para requisição de login.

    Usado em: POST /auth/login
    """

    email: EmailStr = Field(
        ...,
        description="Email cadastrado",
        examples=["joao@oficina.com"]
    )

    password: str = Field(
        ...,
        description="Senha do usuário",
        examples=["Senha@123"]
    )


class PasswordChange(BaseModel):
    """
    Schema para alteração de senha.

    Usado em: POST /auth/change-password
    """

    current_password: str = Field(
        ...,
        description="Senha atual"
    )

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Nova senha"
    )

    @field_validator("new_password")
    @classmethod
    def senha_deve_ser_forte(cls, v: str) -> str:
        """Valida força da nova senha."""
        if not any(c.isupper() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")
        if not any(c.islower() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Senha deve conter pelo menos um número")
        return v


# =============================================================================
# SCHEMAS DE SAÍDA (RESPONSE)
# =============================================================================

class UserResponse(BaseModel):
    """
    Schema para resposta com dados do usuário.

    IMPORTANTE: Nunca inclui a senha!

    Usado em:
    - GET /users/{id}
    - GET /auth/me
    - POST /auth/register (resposta)
    """

    id: int = Field(..., description="ID único do usuário")
    email: str = Field(..., description="Email do usuário")
    nome: str = Field(..., description="Nome completo")
    role: UserRole = Field(..., description="Papel no sistema")
    is_active: bool = Field(..., description="Se está ativo")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    # Permite criar a partir de um model SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """
    Schema para resposta de autenticação com token.

    Usado em: POST /auth/login
    """

    access_token: str = Field(
        ...,
        description="Token JWT para autenticação"
    )

    token_type: str = Field(
        default="bearer",
        description="Tipo do token (sempre 'bearer')"
    )

    expires_in: int = Field(
        ...,
        description="Tempo de expiração em segundos"
    )

    user: UserResponse = Field(
        ...,
        description="Dados do usuário autenticado"
    )


class TokenPayload(BaseModel):
    """
    Schema para o payload do token JWT.

    Usado internamente para decodificar o token.
    """

    sub: str = Field(..., description="Subject (email do usuário)")
    exp: datetime = Field(..., description="Data de expiração")
    iat: datetime = Field(..., description="Data de emissão")
    role: str = Field(..., description="Papel do usuário")


# =============================================================================
# SCHEMAS DE MENSAGEM
# =============================================================================

class MessageResponse(BaseModel):
    """Schema genérico para mensagens de sucesso/erro."""

    message: str = Field(..., description="Mensagem descritiva")
    success: bool = Field(default=True, description="Se a operação foi bem sucedida")
