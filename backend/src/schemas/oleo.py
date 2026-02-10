"""
Schemas Pydantic para Óleo (Produto).

Define validação de entrada e formato de saída da API.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OleoBase(BaseModel):
    """Campos comuns para Óleo."""
    nome: str = Field(..., min_length=2, max_length=100, description="Nome do produto")
    marca: str = Field(..., min_length=2, max_length=50, description="Fabricante")
    modelo: str | None = Field(None, max_length=100, description="Linha/modelo do produto")
    tipo_veiculo: str | None = Field(None, max_length=50, description="Ex: Carro, Caminhonete")
    viscosidade: str | None = Field(None, max_length=20, description="Grau de viscosidade")
    volume_unidade: str | None = Field(None, max_length=20, description="Ex: 1 L")
    volume_liquido: str | None = Field(None, max_length=20, description="Ex: 1 L")
    formato_venda: str | None = Field(None, max_length=30, description="Ex: Unidade, Caixa")
    tipo_recipiente: str | None = Field(None, max_length=50, description="Ex: Garrafa plástica")
    tipo_oleo_transmissao: str | None = Field(None, max_length=100, description="Ex: ATF Dexron VI")
    desempenho: str | None = Field(None, max_length=100, description="Ex: Full Synthetic")
    codigo_oem: str | None = Field(None, max_length=100, description="Ex: GM General Motors")
    custo_litro: Decimal = Field(Decimal("0"), ge=0, description="Custo de aquisição por litro")
    preco_litro: Decimal = Field(Decimal("0"), ge=0, description="Preço de venda por litro")
    estoque_litros: Decimal = Field(Decimal("0"), ge=0, description="Estoque atual")
    estoque_minimo: Decimal = Field(Decimal("5"), ge=0, description="Estoque mínimo")
    observacoes: str | None = Field(None, description="Observações")


class OleoCreate(OleoBase):
    """Schema para criar óleo."""
    pass


class OleoUpdate(BaseModel):
    """Schema para atualizar óleo (todos opcionais)."""
    nome: str | None = Field(None, min_length=2, max_length=100)
    marca: str | None = Field(None, min_length=2, max_length=50)
    modelo: str | None = Field(None, max_length=100)
    tipo_veiculo: str | None = Field(None, max_length=50)
    viscosidade: str | None = Field(None, max_length=20)
    volume_unidade: str | None = Field(None, max_length=20)
    volume_liquido: str | None = Field(None, max_length=20)
    formato_venda: str | None = Field(None, max_length=30)
    tipo_recipiente: str | None = Field(None, max_length=50)
    tipo_oleo_transmissao: str | None = Field(None, max_length=100)
    desempenho: str | None = Field(None, max_length=100)
    codigo_oem: str | None = Field(None, max_length=100)
    custo_litro: Decimal | None = Field(None, ge=0)
    preco_litro: Decimal | None = Field(None, ge=0)
    estoque_litros: Decimal | None = Field(None, ge=0)
    estoque_minimo: Decimal | None = Field(None, ge=0)
    ativo: bool | None = Field(None)
    observacoes: str | None = Field(None)
    foto_url: str | None = Field(None, description="Caminho da foto do produto")


class OleoResponse(OleoBase):
    """Schema de resposta com dados do banco."""
    id: int
    ativo: bool
    foto_url: str | None = Field(None, description="Caminho da foto do produto")
    created_at: datetime
    updated_at: datetime
    estoque_baixo: bool = Field(description="Se estoque está abaixo do mínimo")
    margem_lucro: Decimal = Field(description="Margem de lucro em %")
    lucro_por_litro: Decimal = Field(description="Lucro bruto por litro")

    model_config = ConfigDict(from_attributes=True)


class OleoListResponse(BaseModel):
    """Resposta paginada de óleos."""
    items: list[OleoResponse]
    total: int
    page: int
    pages: int


class OleoEstoqueUpdate(BaseModel):
    """Schema para atualizar estoque."""
    quantidade: Decimal = Field(..., description="Quantidade a adicionar/remover")
    operacao: str = Field("adicionar", description="'adicionar' ou 'remover'")

    @field_validator("operacao")
    @classmethod
    def validar_operacao(cls, v: str) -> str:
        if v.lower() not in ["adicionar", "remover"]:
            raise ValueError("Operação deve ser 'adicionar' ou 'remover'")
        return v.lower()
