"""
Módulo Schemas - Validação Pydantic do ShiftLab Pro.

Contém todos os schemas de validação para a API:
- ClienteCreate, ClienteResponse, etc.
- VeiculoCreate, VeiculoResponse, etc.
- OleoCreate, OleoResponse, etc.
- TrocaOleoCreate, TrocaOleoResponse, etc.

Uso:
    from src.schemas import ClienteCreate, ClienteResponse
"""

from src.schemas.cliente import (
    ClienteCreate,
    ClienteListResponse,
    ClienteResponse,
    ClienteUpdate,
)
from src.schemas.oleo import (
    OleoCreate,
    OleoEstoqueUpdate,
    OleoListResponse,
    OleoResponse,
    OleoUpdate,
)
from src.schemas.servico import (
    ServicoCreate,
    ServicoListResponse,
    ServicoResponse,
    ServicoUpdate,
)
from src.schemas.troca_oleo import (
    ProximasTrocasResponse,
    TrocaOleoCreate,
    TrocaOleoDetailResponse,
    TrocaOleoListResponse,
    TrocaOleoResponse,
    TrocaOleoUpdate,
)
from src.schemas.veiculo import (
    VeiculoComClienteResponse,
    VeiculoCreate,
    VeiculoListResponse,
    VeiculoResponse,
    VeiculoUpdate,
)

__all__ = [
    # Cliente
    "ClienteCreate",
    "ClienteUpdate",
    "ClienteResponse",
    "ClienteListResponse",
    # Veículo
    "VeiculoCreate",
    "VeiculoUpdate",
    "VeiculoResponse",
    "VeiculoComClienteResponse",
    "VeiculoListResponse",
    # Óleo
    "OleoCreate",
    "OleoUpdate",
    "OleoResponse",
    "OleoListResponse",
    "OleoEstoqueUpdate",
    # Serviço
    "ServicoCreate",
    "ServicoUpdate",
    "ServicoResponse",
    "ServicoListResponse",
    # Troca de Óleo
    "TrocaOleoCreate",
    "TrocaOleoUpdate",
    "TrocaOleoResponse",
    "TrocaOleoDetailResponse",
    "TrocaOleoListResponse",
    "ProximasTrocasResponse",
]
