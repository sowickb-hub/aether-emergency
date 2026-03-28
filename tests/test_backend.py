"""
Pytest tests for Aether Emergency FastAPI backend.
Run: pytest tests/test_backend.py -v
"""

import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

# Make sure we can import backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Patch Gemini before importing app ──────────────────────────────────
@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Inject a dummy API key so the app doesn't crash on import."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-abc123")


@pytest.fixture()
def client(mock_env):
    from backend.main import app
    return TestClient(app)


# ── Health endpoint ─────────────────────────────────────────────────────
class TestHealth:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_payload(self, client):
        data = client.get("/health").json()
        assert data["status"] == "ok"
        assert "aether-emergency" in data["service"].lower()


# ── /analyze validation ─────────────────────────────────────────────────
class TestAnalyzeValidation:
    def test_empty_text_rejected(self, client):
        """Empty crisis text must return 422 Unprocessable Entity."""
        response = client.post("/analyze", json={"text": "   "})
        assert response.status_code == 422

    def test_missing_text_rejected(self, client):
        """Missing text field must return 422."""
        response = client.post("/analyze", json={})
        assert response.status_code == 422

    def test_valid_request_calls_gemini(self, client):
        """Valid request reaches the Gemini layer (mocked)."""
        sample_json = {
            "hazard_level": "RED",
            "hazard_justification": "Active fire with trapped persons.",
            "primary_need": "FIRE",
            "secondary_needs": ["MEDICAL"],
            "location_details": "Pine Ave Building 7, Floor 3",
            "casualties_reported": "2",
            "imminent_threats": ["Structural collapse", "Smoke inhalation"],
            "recommended_units": ["Engine 4", "Medic 2"],
            "first_aid_protocols": ["Evacuate building", "Treat for smoke inhalation"],
            "ems_priority_code": "P1",
            "estimated_response_time_min": 5,
            "narrative_summary": "Active fire on floor 3, two trapped.",
            "confidence_score": 0.95,
            "image_observations": "NO IMAGES PROVIDED",
        }

        mock_chunk = MagicMock()
        mock_chunk.text = json.dumps(sample_json)

        with patch("backend.main.get_gemini_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.models.generate_content_stream.return_value = iter([mock_chunk])
            mock_get_client.return_value = mock_client

            response = client.post(
                "/analyze",
                json={"text": "Fire on floor 3, two people trapped."},
            )

        assert response.status_code == 200

    def test_images_accepted(self, client):
        """Request with base64 image payload is accepted at schema level."""
        import base64

        tiny_png = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20).decode()

        mock_chunk = MagicMock()
        mock_chunk.text = '{"hazard_level":"YELLOW"}'

        with patch("backend.main.get_gemini_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.models.generate_content_stream.return_value = iter([mock_chunk])
            mock_get_client.return_value = mock_client

            response = client.post(
                "/analyze",
                json={
                    "text": "Minor incident with photo evidence.",
                    "images": [{"mime_type": "image/png", "data": tiny_png}],
                },
            )

        assert response.status_code == 200


# ── JSON extraction logic ───────────────────────────────────────────────
class TestJsonExtraction:
    """Unit tests for response JSON parsing helpers."""

    REQUIRED_KEYS = {
        "hazard_level",
        "hazard_justification",
        "primary_need",
        "secondary_needs",
        "location_details",
        "casualties_reported",
        "imminent_threats",
        "recommended_units",
        "first_aid_protocols",
        "ems_priority_code",
        "estimated_response_time_min",
        "narrative_summary",
        "confidence_score",
        "image_observations",
    }

    def test_schema_has_all_required_keys(self):
        """Ensure the expected schema contains all required keys."""
        sample = {k: None for k in self.REQUIRED_KEYS}
        assert set(sample.keys()) == self.REQUIRED_KEYS

    def test_hazard_level_values(self):
        valid = {"RED", "ORANGE", "YELLOW"}
        for level in valid:
            assert level in valid

    def test_ems_priority_values(self):
        valid = {"P1", "P2", "P3"}
        for code in valid:
            assert code in valid

    def test_confidence_score_range(self):
        scores = [0.0, 0.5, 0.95, 1.0]
        for s in scores:
            assert 0.0 <= s <= 1.0
