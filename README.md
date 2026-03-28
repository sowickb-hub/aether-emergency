# 🚨 LifePulse — Emergency Dispatch Intelligence System

<div align="center">

```
██╗     ██╗███████╗███████╗██████╗ ██╗   ██╗██╗     ███████╗███████╗
██║     ██║██╔════╝██╔════╝██╔══██╗██║   ██║██║     ██╔════╝██╔════╝
██║     ██║█████╗  █████╗  ██████╔╝██║   ██║██║     ███████╗█████╗  
██║     ██║██╔══╝  ██╔══╝  ██╔═══╝ ██║   ██║██║     ╚════██║██╔══╝  
███████╗██║██║     ███████╗██║     ╚██████╔╝███████╗███████║███████╗
╚══════╝╚═╝╚═╝     ╚══════╝╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝
```

**A Universal Bridge for Societal Benefit**  
*AI-Powered Emergency Dispatch — Built for Google Gemini*

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?style=flat-square&logo=streamlit)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google_Gemini-2.0_Flash-4285F4?style=flat-square&logo=google)](https://ai.google.dev)
[![Cloud Run](https://img.shields.io/badge/Cloud_Run-Ready-brightgreen?style=flat-square&logo=google-cloud)](https://cloud.google.com/run)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

## 🎯 What LifePulse Does

**LifePulse** transforms chaotic, unstructured crisis communications into structured, actionable **Emergency Dispatch Intelligence** — in real time. Emergency operators paste raw incident reports; LifePulse uses Google Gemini's multimodal AI to instantly parse them into color-coded hazard assessments, unit recommendations, and machine-readable dispatch packets.

> **"Every second matters. LifePulse makes every second count."**

---

## ⭐ Technical Merit

### 1. Multimodal AI at the Core
LifePulse harnesses **Google Gemini 2.0 Flash**'s multimodal capabilities to simultaneously reason over:
- **Unstructured text** — raw crisis reports from callers, field units, or public feeds
- **Visual evidence** — uploaded scene photographs analyzed for hazard indicators

Both modalities are packaged into a single API call using the `google-generativeai` SDK's `inline_data` pattern, enabling real-time cross-modal inference with sub-3-second response times.

### 2. Zero-Schema Extraction via Prompt Engineering
Instead of relying on NER pipelines, regex rules, or fine-tuned models, LifePulse uses a single **constrained JSON prompt** to extract a rich 13-field structured schema from arbitrary natural language. The schema covers:
- Hazard classification (RED / ORANGE / YELLOW)
- Primary & secondary emergency service needs
- Location extraction, casualty estimation
- EMS Priority Codes (P1/P2/P3)
- Recommended response unit types
- AI confidence scoring

This approach is model-agnostic, zero-shot, and immediately updatable without retraining.

### 3. Cloud-Native Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      Google Cloud Run                        │
│  ┌──────────────────┐    ┌────────────────────────────────┐ │
│  │ Streamlit Frontend│───▶│ Gemini 2.0 Flash API          │ │
│  │ (Port 8080)       │    │  - Text understanding         │ │
│  │                   │◀───│  - Image analysis             │ │
│  │ Cyberpunk Dark UI │    │  - JSON schema compliance     │ │
│  └──────────────────┘    └────────────────────────────────┘ │
│                                                              │
│  Multi-stage Docker build │ Non-root user │ Health probes   │
└─────────────────────────────────────────────────────────────┘
```

The Dockerfile uses a **multi-stage build** to minimize the final image size (~180MB), a dedicated non-root system user for security compliance, and an integrated `HEALTHCHECK` endpoint compatible with Cloud Run's readiness probing.

### 4. Cyberpunk Dark UI System
The frontend is built with a custom CSS design system featuring:
- **Glassmorphism panels** with `backdrop-filter: blur(16px)`  
- **Animated neon glow** effects on hazard badges (with pulse animation for RED-level incidents)
- **CSS scanline overlay** for cyberpunk authenticity
- **Animated grid background** using pure CSS gradients
- **`Orbitron` + `Share Tech Mono`** Google Fonts for typeface hierarchy
- **Dynamic color theming** driven by hazard level classification

---

## 🌍 Alignment with Cause

### The Problem: The Communication Gap in Crisis Response
Every year, thousands of emergency calls are lost in translation. Dispatchers receive fragmented, panic-driven descriptions; critical details get missed; wrong units are sent. In mass-casualty events, this bottleneck costs lives.

### LifePulse as a Societal Bridge
LifePulse directly addresses the **Universal Bridge** challenge by:

| Challenge | LifePulse Solution |
|-----------|-------------------|
| Unstructured crisis data | Gemini parses any natural language format |
| Multi-modal incidents | Vision + text processed in one request |
| Integration barriers | Exportable machine-readable JSON for CAD systems |
| Dispatcher cognitive load | Color-coded, prioritized output cuts decision time |
| Accessibility | Web-based, no specialized hardware required |

### Real-World Impact Vectors
- **🏥 Emergency Medical Services** — Faster triage classification and ambulance routing
- **🔥 Fire Departments** — Instant hazard identification and resource pre-staging  
- **⛑️ Search & Rescue** — Multi-agency coordination via shared JSON dispatch packets
- **🌐 Disaster Response NGOs** — Process field reports from non-English crisis zones (Gemini's multilingual capability)
- **📡 911 Call Centers** — Augment dispatcher judgment with AI-validated severity scores

### Ethical Safeguards
- **AI as assistant, not replacement** — LifePulse surfaces AI confidence scores, ensuring dispatchers maintain decision authority
- **No PII storage** — All processing is ephemeral; no data is persisted beyond the session
- **Fail-safe design** — Errors surface clearly; the system never silently degrades

---

## 🚀 Quick Start

### Local Development

```bash
# 1. Clone and enter project
git clone <repo-url>
cd lifepulse

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
$env:GOOGLE_API_KEY = "your-api-key-here"   # Windows PowerShell
# export GOOGLE_API_KEY="your-api-key-here"  # Linux/macOS

# 5. Run LifePulse
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

> 💡 Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## 🐳 Deploy to Google Cloud Run

### Prerequisites
```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Step 1 — Build & Push Image
```bash
# Enable required services
gcloud services enable run.googleapis.com containerregistry.googleapis.com

# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/lifepulse .
```

### Step 2 — Deploy to Cloud Run
```bash
gcloud run deploy lifepulse \
  --image gcr.io/YOUR_PROJECT_ID/lifepulse \
  --platform managed \
  --region us-central1 \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars GOOGLE_API_KEY=your-api-key \
  --allow-unauthenticated
```

### Step 3 — Secure the API Key (Production)
For production deployments, store the API key in **Google Secret Manager**:
```bash
# Create secret
echo -n "your-api-key" | gcloud secrets create GOOGLE_API_KEY --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
  --member="serviceAccount:YOUR_SA@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secret reference
gcloud run deploy lifepulse \
  --set-secrets GOOGLE_API_KEY=GOOGLE_API_KEY:latest \
  ...
```

---

## 📊 Dispatch Output Schema

```jsonc
{
  "hazard_level": "RED",                          // 🔴 RED | 🟠 ORANGE | 🟡 YELLOW
  "hazard_justification": "Active fire with...",  // AI reasoning
  "primary_need": "FIRE",                         // MEDICAL | FIRE | RESCUE | HAZMAT | EVACUATION
  "secondary_needs": ["MEDICAL", "EVACUATION"],
  "location_details": "Pine Ave Building 7, 3F",
  "casualties_reported": "2 trapped, 1 unconscious",
  "imminent_threats": ["Electrical sparks", "Structural collapse risk"],
  "recommended_units": ["Engine Company", "Ladder Company", "ALS Unit"],
  "ems_priority_code": "P1",                      // P1=Critical | P2=Urgent | P3=Non-urgent
  "estimated_response_time_min": 4,
  "narrative_summary": "Active fire on third floor...",
  "confidence_score": 0.94,                       // 0.0 - 1.0
  "image_observations": "Dense smoke visible..."
}
```

---

## 🗂️ Project Structure

```
lifepulse/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── Dockerfile              # Cloud Run-optimised multi-stage image
├── streamlit_config.toml   # Streamlit theme configuration
└── README.md               # This document
```

---

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google AI Studio API key | Yes |
| `PORT` | Server port (Cloud Run auto-injects) | No (default: 8080) |

---

## 📜 License

MIT License — free to use, modify, and deploy.

---

<div align="center">

Built with ❤️ for the **Universal Bridge for Societal Benefit** challenge  
Powered by **Google Gemini 2.0 Flash** · Deployed on **Google Cloud Run**

</div>
