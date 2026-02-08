"""
Módulo Domain - Entidades do ShiftLab Pro.

Contém todos os modelos SQLAlchemy do sistema:
- Cliente: Clientes da oficina
- Veiculo: Veículos cadastrados
- Oleo: Tipos de óleo disponíveis
- TrocaOleo: Histórico de trocas

Uso:
    from src.domain import Cliente, Veiculo, Oleo, TrocaOleo
"""

from src.domain.base import BaseModel
from src.domain.cliente import Cliente
from src.domain.item_troca import ItemTroca
from src.domain.oleo import Oleo, TipoOleo
from src.domain.peca import Peca
from src.domain.servico import Servico
from src.domain.troca_oleo import TrocaOleo
from src.domain.veiculo import TipoCambio, Veiculo

__all__ = [
    "BaseModel",
    "Cliente",
    "Veiculo",
    "TipoCambio",
    "Oleo",
    "TipoOleo",
    "Peca",
    "Servico",
    "ItemTroca",
    "TrocaOleo",
]
