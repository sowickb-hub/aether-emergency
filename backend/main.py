"""
Aether Emergency — FastAPI Backend
Bridge between React frontend and Gemini 2.0 Flash.
GEMINI_API_KEY is loaded exclusively from the environment; never exposed to the browser.
"""

from __future__ import annotations

import json
import os
import base64
from dotenv import load_dotenv

# Always load from the .env next to this file, regardless of CWD
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
loaded = load_dotenv(_env_path)
print(f"[startup] .env loaded from: {_env_path} → {loaded}")
print(f"[startup] GEMINI_API_KEY set: {'YES' if os.getenv('GEMINI_API_KEY') else 'NO'}")
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ── App ------------------------------------------------------------------
app = FastAPI(title="Aether Emergency API", version="1.0.0")

# ── CORS (allow Vite dev server + same-origin in production) -------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",  # vite preview
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Gemini client (lazy, validated once on first request) ----------------
_gemini_client: genai.Client | None = None

def get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=503,
                detail="GEMINI_API_KEY environment variable is not set on the server.",
            )
        _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


# ── Request / Response models -------------------------------------------
class ImagePayload(BaseModel):
    mime_type: str
    data: str  # base64-encoded


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Crisis report text")
    images: list[ImagePayload] = Field(default_factory=list)


# ── System prompt --------------------------------------------------------
SYSTEM_PROMPT = """\
You are Aether Emergency, an elite Emergency Dispatch AI. Analyze the crisis data and return a structured assessment.

CRITICAL: Respond ONLY with valid JSON matching this exact schema (no markdown fences, no extra text):

{
  "hazard_level": "RED" | "ORANGE" | "YELLOW",
  "hazard_justification": "<1-2 sentence explanation>",
  "primary_need": "MEDICAL" | "FIRE" | "RESCUE" | "HAZMAT" | "EVACUATION",
  "secondary_needs": ["<need1>", "<need2>"],
  "location_details": "<extracted location or 'UNSPECIFIED'>",
  "casualties_reported": "<number/description or 'UNKNOWN'>",
  "imminent_threats": ["<threat1>", "<threat2>"],
  "recommended_units": ["<unit1>", "<unit2>"],
  "first_aid_protocols": ["<step1>", "<step2>", "<step3>"],
  "ems_priority_code": "P1" | "P2" | "P3",
  "estimated_response_time_min": <integer>,
  "narrative_summary": "<3-5 sentence human-readable dispatch briefing>",
  "confidence_score": <float 0.0-1.0>,
  "image_observations": "<brief description of evidence photos or 'NO IMAGES PROVIDED'>"
}

Hazard levels:
- RED: Immediate life threat, active fire/violence, critical injuries
- ORANGE: Serious injuries, contained fire, significant property risk
- YELLOW: Minor injuries, precautionary response, no immediate life threat
"""


# ── Streaming analysis endpoint -----------------------------------------
async def _stream_analysis(request: AnalyzeRequest) -> AsyncGenerator[str, None]:
    client = get_gemini_client()

    # Build content parts
    parts: list[types.Part] = [
        types.Part.from_text(
            text=f"{SYSTEM_PROMPT}\n\n=== CRISIS REPORT ===\n{request.text}\n=== END REPORT ==="
        )
    ]

    for img in request.images:
        try:
            raw_bytes = base64.b64decode(img.data)
            parts.append(
                types.Part.from_bytes(data=raw_bytes, mime_type=img.mime_type)
            )
        except Exception:
            pass  # skip malformed images

    try:
        response_stream = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=parts,
        )
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as exc:
        error_payload = json.dumps({"error": str(exc)})
        yield error_payload


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """Stream Gemini analysis back to the frontend as plain text chunks."""
    if not request.text.strip():
        raise HTTPException(status_code=422, detail="Crisis text cannot be empty.")
    return StreamingResponse(
        _stream_analysis(request),
        media_type="text/plain; charset=utf-8",
        headers={"X-Accel-Buffering": "no"},
    )


# ── Key test endpoint (debug) -------------------------------------------
@app.get("/test-key")
async def test_key():
    """Quick check: is the API key loaded and accepted by Google?"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "error", "detail": "GEMINI_API_KEY not set in environment"}
    try:
        from google import genai as _g
        c = _g.Client(api_key=api_key)
        # List models as a lightweight ping
        models = [m.name for m in c.models.list()]
        return {"status": "ok", "key_prefix": api_key[:8] + "...", "models_available": models[:5]}
    except Exception as exc:
        return {"status": "error", "key_prefix": api_key[:8] + "...", "detail": str(exc)}


# ── Health check ---------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "aether-emergency-api"}


# ── Serve React static build (production) --------------------------------
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(STATIC_DIR):
    from fastapi.responses import FileResponse

    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
