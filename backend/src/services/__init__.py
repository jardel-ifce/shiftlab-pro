"""
Módulo Services - Lógica de Negócio do ShiftLab Pro.

Contém a lógica de negócio para:
- ClienteService: Gerenciamento de clientes
- VeiculoService: Gerenciamento de veículos
- OleoService: Gerenciamento de óleos/produtos
- TrocaOleoService: Registro de trocas de óleo

Uso:
    from src.services import ClienteService, VeiculoService

    service = ClienteService(db_session)
    cliente = await service.create(data)
"""

from src.services.cliente_service import ClienteService
from src.services.oleo_service import OleoService
from src.services.servico_service import ServicoService
from src.services.troca_service import TrocaOleoService
from src.services.veiculo_service import VeiculoService

__all__ = [
    "ClienteService",
    "VeiculoService",
    "OleoService",
    "ServicoService",
    "TrocaOleoService",
]
