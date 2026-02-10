"""
ShiftLab Pro - Entry Point da Aplicação.

Este é o ponto de entrada principal da API FastAPI.
Configura a aplicação, middlewares, rotas e eventos de ciclo de vida.

Para executar:
    uvicorn src.main:app --reload

Para acessar a documentação:
    http://localhost:8000/docs     (Swagger UI)
    http://localhost:8000/redoc    (ReDoc)
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.v1.catalogo import router as catalogo_router
from src.api.v1.clientes import router as clientes_router
from src.api.v1.oleos import router as oleos_router
from src.api.v1.pecas import router as pecas_router
from src.api.v1.servicos import router as servicos_router
from src.api.v1.trocas import router as trocas_router
from src.api.v1.veiculos import router as veiculos_router
from src.auth.router import router as auth_router
from src.auth.service import AuthService
from src.config import settings
from src.database import async_session_maker, create_all_tables, engine

# =============================================================================
# LIFECYCLE EVENTS
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.

    Startup (antes de receber requests):
    - Verifica conexão com o banco
    - Cria primeiro admin se não existir

    Shutdown (ao encerrar):
    - Fecha conexões com o banco
    """
    # === STARTUP ===
    print("=" * 60)
    print(f"🚀 Iniciando {settings.APP_NAME}...")
    print(f"📍 Ambiente: {settings.ENVIRONMENT}")
    print(f"🔗 Banco: {settings.DATABASE_URL[:50]}...")
    print("=" * 60)

    # Cria diretório de uploads se não existir
    uploads_dir = Path(settings.UPLOAD_DIR) / "oleos"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Uploads: {uploads_dir.resolve()}")

    # Cria tabelas novas (dev only — em produção usar Alembic)
    await create_all_tables()

    # Cria primeiro admin se não existir
    async with async_session_maker() as session:
        try:
            service = AuthService(session)
            admin = await service.create_first_admin()
            if admin:
                print(f"✅ Admin criado: {admin.email}")
            else:
                print("ℹ️  Admin já existe")
            await session.commit()
        except Exception as e:
            print(f"⚠️  Erro ao criar admin: {e}")
            await session.rollback()

    print("✅ Aplicação pronta para receber requests!")
    print(f"📚 Documentação: http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 60)

    yield  # Aplicação rodando

    # === SHUTDOWN ===
    print("=" * 60)
    print("🛑 Encerrando aplicação...")
    await engine.dispose()
    print("✅ Conexões fechadas. Até logo!")
    print("=" * 60)


# =============================================================================
# CRIAÇÃO DA APLICAÇÃO
# =============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    description="""
## ShiftLab Pro - Sistema de Gerenciamento de Troca de Óleo

Sistema completo para oficinas mecânicas gerenciarem:

* **Clientes** - Cadastro e histórico de clientes
* **Veículos** - Registro de veículos por cliente
* **Trocas de Óleo** - Histórico completo de manutenções
* **Alertas** - Notificações de próximas trocas
* **Relatórios** - Faturamento e estatísticas

### Autenticação

A API usa autenticação via **JWT (JSON Web Token)**.

1. Faça login em `/api/v1/auth/login` para obter o token
2. Use o token no header: `Authorization: Bearer <token>`
3. O token expira em 30 minutos

### Contato

* **Email**: contato@shiftlab.com.br
* **GitHub**: https://github.com/shiftlab/shiftlab-pro
    """,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# =============================================================================
# MIDDLEWARES
# =============================================================================

# CORS - Cross-Origin Resource Sharing
# Permite que o frontend (React) acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Authorization, Content-Type, etc.
)


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handler para erros de validação do Pydantic.

    Retorna mensagens de erro mais amigáveis.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "campo": field,
            "mensagem": error["msg"],
            "tipo": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Erro de validação nos dados enviados",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handler genérico para exceções não tratadas.

    Em produção, não expõe detalhes do erro.
    """
    if settings.DEBUG:
        detail = str(exc)
    else:
        detail = "Erro interno do servidor"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail}
    )


# =============================================================================
# ROTAS
# =============================================================================

# Rota de health check (verificar se API está online)
@app.get(
    "/health",
    tags=["Health"],
    summary="Verificar status da API",
    response_model=dict
)
async def health_check() -> dict:
    """
    Endpoint de health check.

    Retorna o status da API e informações básicas.
    Útil para monitoramento e load balancers.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Rota raiz
@app.get(
    "/",
    tags=["Root"],
    summary="Informações da API",
    response_model=dict
)
async def root() -> dict:
    """
    Rota raiz da API.

    Retorna informações básicas e links úteis.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


# =============================================================================
# INCLUIR ROUTERS
# =============================================================================

# Auth Router - /api/v1/auth/*
app.include_router(
    auth_router,
    prefix=settings.API_PREFIX,
)

# Clientes Router - /api/v1/clientes/*
app.include_router(
    clientes_router,
    prefix=settings.API_PREFIX,
)

# Veículos Router - /api/v1/veiculos/*
app.include_router(
    veiculos_router,
    prefix=settings.API_PREFIX,
)

# Óleos Router - /api/v1/oleos/*
app.include_router(
    oleos_router,
    prefix=settings.API_PREFIX,
)

# Peças Router - /api/v1/pecas/*
app.include_router(
    pecas_router,
    prefix=settings.API_PREFIX,
)

# Serviços Router - /api/v1/servicos/*
app.include_router(
    servicos_router,
    prefix=settings.API_PREFIX,
)

# Trocas Router - /api/v1/trocas/*
app.include_router(
    trocas_router,
    prefix=settings.API_PREFIX,
)

# Catálogo Router - /api/v1/catalogo/*
app.include_router(
    catalogo_router,
    prefix=settings.API_PREFIX,
)

# =============================================================================
# ARQUIVOS ESTÁTICOS (uploads)
# =============================================================================

app.mount(
    "/uploads",
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="uploads",
)


# =============================================================================
# EXECUÇÃO DIRETA
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )
