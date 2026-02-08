"""
Funções de segurança para autenticação.

Este módulo contém:
- Hash de senhas com SHA-256 + salt
- Criação e validação de tokens JWT
- Funções auxiliares de criptografia

IMPORTANTE: Nunca armazene senhas em texto plano!
Sempre use hash_password() antes de salvar no banco.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from src.config import settings


# =============================================================================
# FUNÇÕES DE HASH DE SENHA (SHA-256 + Salt)
# =============================================================================

def hash_password(password: str) -> str:
    """
    Gera hash de uma senha usando SHA-256 com salt.

    Formato do hash: salt$hash
    - salt: 16 bytes aleatórios (hex)
    - hash: SHA-256 da senha + salt

    Args:
        password: Senha em texto plano

    Returns:
        str: Hash da senha no formato "salt$hash"
    """
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    password_hash = hash_obj.hexdigest()
    return f"{salt}${password_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha corresponde ao hash armazenado.

    Args:
        plain_password: Senha em texto plano (digitada pelo usuário)
        hashed_password: Hash armazenado no banco de dados

    Returns:
        bool: True se a senha está correta, False caso contrário
    """
    try:
        salt, stored_hash = hashed_password.split("$")
        hash_obj = hashlib.sha256((plain_password + salt).encode())
        return hash_obj.hexdigest() == stored_hash
    except ValueError:
        return False


# =============================================================================
# FUNÇÕES DE TOKEN JWT
# =============================================================================

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
) -> str:
    """
    Cria um token JWT de acesso.

    O token contém:
    - sub: Subject (identificador do usuário, geralmente email)
    - exp: Data de expiração
    - iat: Data de emissão
    - Dados adicionais passados em 'data'

    Args:
        data: Dicionário com dados a incluir no token
        expires_delta: Tempo de expiração (opcional)

    Returns:
        str: Token JWT codificado

    Example:
        token = create_access_token(
            data={"sub": user.email, "role": user.role},
            expires_delta=timedelta(minutes=30)
        )
    """
    to_encode = data.copy()

    # Define tempo de expiração
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Adiciona claims padrão
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })

    # Codifica o token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Cria um token JWT de refresh (longa duração).

    O refresh token é usado para obter novos access tokens
    sem precisar fazer login novamente.

    Args:
        data: Dicionário com dados a incluir no token

    Returns:
        str: Token JWT de refresh

    Example:
        refresh_token = create_refresh_token({"sub": user.email})
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",  # Marca como refresh token
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> dict | None:
    """
    Decodifica e valida um token JWT.

    Verifica:
    - Assinatura do token (usando SECRET_KEY)
    - Data de expiração

    Args:
        token: Token JWT a ser decodificado

    Returns:
        dict: Payload do token se válido
        None: Se o token for inválido ou expirado

    Example:
        payload = decode_token(token)
        if payload:
            user_email = payload.get("sub")
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> dict | None:
    """
    Alias para decode_token para maior clareza.

    Args:
        token: Token JWT a ser verificado

    Returns:
        dict: Payload se válido, None caso contrário
    """
    return decode_token(token)


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_token_expiration_seconds() -> int:
    """
    Retorna o tempo de expiração do access token em segundos.

    Útil para retornar na resposta de login.

    Returns:
        int: Segundos até expiração
    """
    return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
