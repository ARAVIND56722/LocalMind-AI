from fastapi import APIRouter
from app.schemas.schemas import ModelListResponse, ModelInfo
from app.services.providers.gateway import provider_gateway
from app.core.config import settings

router = APIRouter(tags=["Models & Providers"])

@router.get("/models", response_model=ModelListResponse)
async def list_models():
    # Evaluate actual reachability of each provider
    ollama_ok = await provider_gateway.providers["ollama"].is_available()
    anthropic_ok = await provider_gateway.providers["anthropic"].is_available()
    openai_ok = await provider_gateway.providers["openai"].is_available()
    mock_ok = True

    models = [
        ModelInfo(
            id="llama3.2",
            name="Llama 3.2 (Local Ollama)",
            provider="ollama",
            available=ollama_ok,
            is_default=(settings.DEFAULT_PROVIDER == "ollama"),
            details=f"Ollama server at {settings.OLLAMA_BASE_URL} ({'ONLINE' if ollama_ok else 'OFFLINE - run ollama serve'})"
        ),
        ModelInfo(
            id="claude-3-5-sonnet-20241022",
            name="Claude 3.5 Sonnet",
            provider="anthropic",
            available=anthropic_ok,
            is_default=(settings.DEFAULT_PROVIDER == "anthropic"),
            details="Anthropic Cloud API" if anthropic_ok else "Missing or unconfigured ANTHROPIC_API_KEY"
        ),
        ModelInfo(
            id="gpt-4o",
            name="GPT-4o",
            provider="openai",
            available=openai_ok,
            is_default=(settings.DEFAULT_PROVIDER == "openai"),
            details="OpenAI Cloud API" if openai_ok else "Missing or unconfigured OPENAI_API_KEY"
        ),
        ModelInfo(
            id="evaluation-mock",
            name="High-Fidelity Evaluation Engine",
            provider="mock",
            available=mock_ok,
            is_default=(settings.DEFAULT_PROVIDER == "mock"),
            details="Deterministic local practitioner synthesis model (always ready)"
        ),
    ]

    active_provider, _ = await provider_gateway.get_provider()
    active_model = settings.DEFAULT_MODEL if active_provider != "mock" else "evaluation-mock"

    return ModelListResponse(
        active_provider=active_provider,
        active_model=active_model,
        models=models
    )
