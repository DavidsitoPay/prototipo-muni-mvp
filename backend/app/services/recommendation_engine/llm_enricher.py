"""Enriquecimiento opcional via LLM local (Ollama). Apagado por defecto
(LLM_ENABLED=false): en ese caso nunca se llama a esta funcion, cero
llamadas de red. Si esta habilitado y Ollama no responde, se degrada
silenciosamente devolviendo None; el llamador conserva siempre el texto
del motor de reglas como fuente principal."""

import httpx

from app.config import settings

_PROMPT_TEMPLATE = (
    "Reescribe esta recomendacion de ciberseguridad en un parrafo breve y "
    "profesional para un directivo municipal, sin agregar hechos nuevos: "
    "{rule_text}. Contexto: {context}."
)


async def enrich(rule_text: str, context: dict) -> str | None:
    if not settings.llm_enabled:
        return None

    prompt = _PROMPT_TEMPLATE.format(rule_text=rule_text, context=context)
    try:
        async with httpx.AsyncClient(timeout=5.0) as http_client:
            response = await http_client.post(
                f"{settings.ollama_host}/api/generate",
                json={"model": "llama3.2", "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("response", "").strip()
            return text or None
    except (httpx.HTTPError, ValueError):
        return None
