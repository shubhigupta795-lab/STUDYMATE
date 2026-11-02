import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.llm.output_schema import ResearchExtraction
from app.llm.prompts import EXTRACTION_PROMPT

load_dotenv()


def _client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to .env before uploading a source.")
    return genai.Client(api_key=api_key)


def _model_name() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def _config() -> types.GenerateContentConfig:
    tools = []
    if os.getenv("ENABLE_CURRENT_WEB_RESEARCH", "true").lower() == "true":
        tools.append(types.Tool(google_search=types.GoogleSearch()))

    return types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ResearchExtraction,
        temperature=0.2,
        tools=tools or None,
    )


def extract_from_text(text: str) -> tuple[ResearchExtraction, dict[str, Any]]:
    client = _client()
    prompt = EXTRACTION_PROMPT + "\n\nSOURCE CONTENT:\n" + text
    response = client.models.generate_content(
        model=_model_name(),
        contents=prompt,
        config=_config(),
    )
    parsed = getattr(response, "parsed", None)
    if parsed is None:
        parsed = ResearchExtraction.model_validate_json(response.text)
    elif not isinstance(parsed, ResearchExtraction):
        parsed = ResearchExtraction.model_validate(parsed)

    grounding = _extract_grounding(response)
    return parsed, grounding


def extract_from_pdf(path: Path) -> tuple[ResearchExtraction, dict[str, Any]]:
    client = _client()
    uploaded = client.files.upload(file=str(path))
    contents = [EXTRACTION_PROMPT, uploaded]
    response = client.models.generate_content(
        model=_model_name(),
        contents=contents,
        config=_config(),
    )
    parsed = getattr(response, "parsed", None)
    if parsed is None:
        parsed = ResearchExtraction.model_validate_json(response.text)
    elif not isinstance(parsed, ResearchExtraction):
        parsed = ResearchExtraction.model_validate(parsed)

    grounding = _extract_grounding(response)
    return parsed, grounding


def build_embedding_text(extraction: ResearchExtraction) -> str:
    data = extraction.model_dump()
    # Keep every research category in the embedding input so later retrieval is not
    # driven only by the short summary.
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def create_embedding(text: str) -> list[float]:
    client = _client()
    result = client.models.embed_content(
        model=os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2"),
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768),
    )
    if not result.embeddings:
        raise RuntimeError("Gemini returned no embedding for the extracted knowledge.")
    return list(result.embeddings[0].values)


def _extract_grounding(response: Any) -> dict[str, Any]:
    """Best-effort extraction of current-web grounding metadata."""
    result: dict[str, Any] = {"web_search_queries": [], "web_sources": []}
    try:
        candidate = response.candidates[0]
        metadata = candidate.grounding_metadata
        if not metadata:
            return result

        result["web_search_queries"] = list(metadata.web_search_queries or [])
        for chunk in metadata.grounding_chunks or []:
            web = getattr(chunk, "web", None)
            if web:
                result["web_sources"].append(
                    {
                        "title": getattr(web, "title", None),
                        "uri": getattr(web, "uri", None),
                    }
                )
    except Exception:
        # Grounding metadata is auxiliary; extraction should not fail because the
        # SDK returns a shape we do not recognize.
        pass
    return result
