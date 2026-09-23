"""Enriquecimiento opcional via LLM en la nube (Google Gemini, capa gratuita).
Apagado por defecto (LLM_ENABLED=false): en ese caso nunca se llama a esta
funcion, cero llamadas de red. Si esta habilitado y Gemini no responde o
GEMINI_API_KEY no esta configurado, se degrada silenciosamente devolviendo
None; el llamador conserva siempre el texto del motor de reglas como fuente
principal."""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = (
    "Reescribe esta recomendacion de ciberseguridad en un parrafo breve y "
    "profesional para un directivo municipal, sin agregar hechos nuevos: "
    "{rule_text}. Contexto: {context}."
)


async def enrich(rule_text: str, context: dict) -> str | None:
    if not settings.llm_enabled or not settings.gemini_api_key:
        return None

    prompt = _PROMPT_TEMPLATE.format(rule_text=rule_text, context=context)
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )
    try:
        async with httpx.AsyncClient(timeout=12.0) as http_client:
            response = await http_client.post(
                url,
                params={"key": settings.gemini_api_key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    # Skip Gemini's "thinking" mode: this is a short paraphrase task,
                    # not reasoning, and thinking tokens burn free-tier quota for nothing.
                    "generationConfig": {"thinkingConfig": {"thinkingBudget": 0}},
                },
            )
            response.raise_for_status()
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return text or None
    except (httpx.HTTPError, ValueError, KeyError, IndexError) as exc:
        logger.warning("Gemini enrichment failed, falling back to rule text: %r", exc)
        return None
