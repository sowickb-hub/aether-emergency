import streamlit as st
import json
import base64
import os
from PIL import Image
import io
import google.generativeai as genai

# ─────────────────────────────────────────────
#  Page Config  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LifePulse — Emergency Dispatch AI",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  Cyberpunk Dark Theme CSS
# ─────────────────────────────────────────────
CYBERPUNK_CSS = """
<style>
/* === Google Font === */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600&display=swap');

/* === Root Variables === */
:root {
    --neon-crimson:   #ff003c;
    --neon-orange:    #ff6a00;
    --neon-yellow:    #ffe600;
    --neon-cyan:      #00f5ff;
    --neon-purple:    #bc00ff;
    --bg-void:        #040408;
    --bg-panel:       rgba(12, 12, 22, 0.85);
    --bg-glass:       rgba(255, 0, 60, 0.05);
    --border-glow:    rgba(255, 0, 60, 0.4);
    --text-primary:   #f0f0f0;
    --text-muted:     #888aaa;
    --text-data:      #00f5ff;
}

/* === Global Reset === */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-void);
    color: var(--text-primary);
}

/* === Animated Grid Background === */
.stApp {
    background-color: var(--bg-void);
    background-image:
        linear-gradient(rgba(255,0,60,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,0,60,0.04) 1px, transparent 1px);
    background-size: 50px 50px;
    min-height: 100vh;
}

/* === Scanline overlay === */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 0, 0, 0.15) 2px,
        rgba(0, 0, 0, 0.15) 4px
    );
    pointer-events: none;
    z-index: 9999;
    animation: scanlines 8s linear infinite;
}

@keyframes scanlines {
    0%   { background-position: 0 0; }
    100% { background-position: 0 100px; }
}

/* === Header === */
.lifepulse-header {
    text-align: center;
    padding: 2rem 1rem 1rem;
    position: relative;
}

.lifepulse-title {
    font-family: 'Orbitron', monospace;
    font-size: 3.8rem;
    font-weight: 900;
    letter-spacing: 0.2em;
    color: var(--text-primary);
    text-shadow:
        0 0 10px var(--neon-crimson),
        0 0 30px var(--neon-crimson),
        0 0 60px rgba(255,0,60,0.5);
    margin: 0;
    animation: pulse-glow 2.5s ease-in-out infinite alternate;
}

@keyframes pulse-glow {
    from { text-shadow: 0 0 10px var(--neon-crimson), 0 0 30px var(--neon-crimson), 0 0 60px rgba(255,0,60,0.4); }
    to   { text-shadow: 0 0 20px var(--neon-crimson), 0 0 50px var(--neon-crimson), 0 0 90px rgba(255,0,60,0.7), 0 0 120px rgba(255,0,60,0.3); }
}

.lifepulse-subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.95rem;
    color: var(--text-muted);
    letter-spacing: 0.35em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}

.lifepulse-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--neon-crimson), var(--neon-orange), transparent);
    margin: 1.5rem auto;
    max-width: 600px;
    border: none;
    box-shadow: 0 0 12px var(--neon-crimson);
}

/* === Glass Panel === */
.glass-panel {
    background: var(--bg-panel);
    border: 1px solid var(--border-glow);
    border-radius: 12px;
    padding: 1.5rem;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow:
        0 0 20px rgba(255,0,60,0.15),
        inset 0 1px 0 rgba(255,255,255,0.05);
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}

.glass-panel::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--neon-crimson), transparent);
}

.panel-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: var(--neon-crimson);
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.panel-label::before {
    content: "//";
    color: var(--text-muted);
}

/* === Streamlit widget overrides === */
.stTextArea textarea {
    background: rgba(4,4,8,0.9) !important;
    border: 1px solid var(--border-glow) !important;
    border-radius: 8px !important;
    color: var(--text-data) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.88rem !important;
    caret-color: var(--neon-crimson) !important;
    transition: border-color 0.3s, box-shadow 0.3s;
}

.stTextArea textarea:focus {
    border-color: var(--neon-crimson) !important;
    box-shadow: 0 0 16px rgba(255,0,60,0.35) !important;
    outline: none !important;
}

.stFileUploader {
    background: rgba(4,4,8,0.9) !important;
    border: 1px dashed var(--border-glow) !important;
    border-radius: 8px !important;
    transition: border-color 0.3s, box-shadow 0.3s;
}

.stFileUploader:hover {
    border-color: var(--neon-crimson) !important;
    box-shadow: 0 0 16px rgba(255,0,60,0.3) !important;
}

/* === Button === */
.stButton > button {
    display: block;
    width: 100%;
    background: linear-gradient(135deg, #ff003c 0%, #cc0030 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.15em !important;
    padding: 0.9rem 2rem !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 20px rgba(255,0,60,0.5), 0 4px 15px rgba(0,0,0,0.5) !important;
    text-transform: uppercase !important;
    position: relative;
    overflow: hidden;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 35px rgba(255,0,60,0.75), 0 8px 25px rgba(0,0,0,0.6) !important;
    background: linear-gradient(135deg, #ff1a50 0%, #e0003a 100%) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* === Spinner/Status === */
.stSpinner > div {
    border-top-color: var(--neon-crimson) !important;
}

/* === Hazard Badge === */
.hazard-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.6rem 1.4rem;
    border-radius: 50px;
    font-family: 'Orbitron', monospace;
    font-size: 1.2rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin: 0.5rem 0;
}

.hazard-RED {
    background: rgba(255,0,60,0.15);
    border: 2px solid #ff003c;
    color: #ff003c;
    box-shadow: 0 0 25px rgba(255,0,60,0.5), inset 0 0 20px rgba(255,0,60,0.08);
    animation: danger-pulse 1.2s ease-in-out infinite alternate;
}

.hazard-ORANGE {
    background: rgba(255,106,0,0.12);
    border: 2px solid #ff6a00;
    color: #ff6a00;
    box-shadow: 0 0 25px rgba(255,106,0,0.45);
}

.hazard-YELLOW {
    background: rgba(255,230,0,0.1);
    border: 2px solid #ffe600;
    color: #ffe600;
    box-shadow: 0 0 25px rgba(255,230,0,0.4);
}

@keyframes danger-pulse {
    from { box-shadow: 0 0 20px rgba(255,0,60,0.5), inset 0 0 20px rgba(255,0,60,0.08); }
    to   { box-shadow: 0 0 40px rgba(255,0,60,0.85), inset 0 0 30px rgba(255,0,60,0.15); border-color: #ff4466; }
}

/* === Metric Tile === */
.metric-tile {
    background: rgba(12,12,22,0.9);
    border: 1px solid var(--border-glow);
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}

.metric-tile:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 25px rgba(255,0,60,0.35);
}

.metric-tile-icon {
    font-size: 2rem;
    margin-bottom: 0.3rem;
}

.metric-tile-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

.metric-tile-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--neon-crimson);
    margin-top: 0.2rem;
    text-shadow: 0 0 10px rgba(255,0,60,0.6);
}

/* === JSON Block === */
.json-block {
    background: rgba(0,0,0,0.8);
    border: 1px solid rgba(0,245,255,0.25);
    border-radius: 8px;
    padding: 1.2rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.82rem;
    color: var(--neon-cyan);
    overflow-x: auto;
    line-height: 1.6;
    box-shadow: inset 0 0 20px rgba(0,245,255,0.05);
}

/* === Status Bar === */
.status-bar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-muted);
    padding: 0.5rem 0;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--neon-crimson);
    box-shadow: 0 0 6px var(--neon-crimson);
    animation: blink 1.5s step-end infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0; }
}

/* === Summary Box === */
.summary-box {
    background: rgba(0,0,0,0.6);
    border-left: 3px solid var(--neon-crimson);
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    font-size: 0.92rem;
    line-height: 1.7;
    color: var(--text-primary);
}

/* === Section Title === */
.section-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--neon-crimson);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin: 1rem 0 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.section-title::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border-glow), transparent);
}

/* === Sidebar === */
section[data-testid="stSidebar"] {
    background: rgba(4,4,8,0.98) !important;
    border-right: 1px solid var(--border-glow) !important;
}

/* === Streamlit label text === */
label, .stLabel {
    color: var(--text-muted) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.1em !important;
}

/* === Scroll bar === */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-void); }
::-webkit-scrollbar-thumb { background: var(--border-glow); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--neon-crimson); }

/* === Alert / Info boxes === */
.stAlert {
    background: rgba(255,0,60,0.08) !important;
    border: 1px solid var(--border-glow) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}

/* === Image display === */
.uploaded-image {
    border: 1px solid var(--border-glow);
    border-radius: 8px;
    box-shadow: 0 0 15px rgba(255,0,60,0.2);
    width: 100%;
}

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
</style>
"""

st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Gemini Client
# ─────────────────────────────────────────────
def get_gemini_client():
    api_key = os.environ.get("GOOGLE_API_KEY") or st.session_state.get("api_key")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-3-flash-preview")

# ─────────────────────────────────────────────
#  Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="lifepulse-header">
    <p class="lifepulse-title">🚨 LIFEPULSE</p>
    <p class="lifepulse-subtitle">Emergency Dispatch Intelligence System // v2.0.6</p>
    <hr class="lifepulse-divider">
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Status Bar
# ─────────────────────────────────────────────
st.markdown("""
<div class="status-bar">
    <span class="status-dot"></span>
    <span>SYSTEM ONLINE</span>
    &nbsp;|&nbsp;
    <span>AI ENGINE: GEMINI-3-FLASH</span>
    &nbsp;|&nbsp;
    <span>DISPATCH PROTOCOL: ACTIVE</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  API Key (sidebar)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 API Configuration")
    api_key_input = st.text_input(
        "Google AI API Key",
        type="password",
        placeholder="AIza...",
        value=st.session_state.get("api_key", ""),
        help="Get your API key from https://aistudio.google.com"
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input
        st.success("✅ API key configured")

    st.markdown("---")
    st.markdown("### ℹ️ About LifePulse")
    st.markdown("""
    **LifePulse** is an AI-powered emergency dispatch bridge that converts unstructured crisis reports into actionable, structured intelligence.

    - 🔴 **Red** — Critical / Life-threatening
    - 🟠 **Orange** — Serious / Urgent
    - 🟡 **Yellow** — Moderate / Precautionary
    """)

# ─────────────────────────────────────────────
#  Main Layout  (2 columns)
# ─────────────────────────────────────────────
col_input, col_output = st.columns([1, 1.15], gap="large")

# ══════════════════════════════════════════════
#  LEFT COLUMN — Input Panel
# ══════════════════════════════════════════════
with col_input:
    st.markdown('<div class="panel-label">Crisis Data Input</div>', unsafe_allow_html=True)


    crisis_text = st.text_area(
        "Unstructured Crisis Data",
        placeholder=(
            "Paste raw crisis report here...\n\n"
            "Example: 'There's smoke and fire coming from the 3rd floor of Pine Ave building 7. "
            "Two people are trapped, one appears unconscious. Electrical sparks visible near the stairwell. "
            "Caller is panicking, says the alarm is sounding. Crowd gathering outside.'"
        ),
        height=220,
        label_visibility="visible",
    )

    st.markdown('<div class="section-title">Evidence Media</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Evidence Photos",
        type=["jpg", "jpeg", "png", "webp", "gif"],
        accept_multiple_files=True,
        help="Upload up to 5 evidence photos from the scene",
        label_visibility="visible",
    )

    if uploaded_files:
        img_cols = st.columns(min(len(uploaded_files), 3))
        for i, f in enumerate(uploaded_files[:3]):
            with img_cols[i]:
                st.image(f, caption=f.name, use_column_width=True)
        if len(uploaded_files) > 3:
            st.caption(f"+ {len(uploaded_files)-3} more file(s) attached")

    # Dispatch button
    dispatch_btn = st.button("⚡ ANALYZE & DISPATCH", use_container_width=True)

# ══════════════════════════════════════════════
#  Gemini Analysis Function
# ══════════════════════════════════════════════
SYSTEM_PROMPT = """
You are LifePulse, an elite Emergency Dispatch AI. Analyze the crisis data provided and return a structured assessment.

IMPORTANT: Respond ONLY with valid JSON in the exact schema below (no markdown, no extra text):

{
  "hazard_level": "RED" | "ORANGE" | "YELLOW",
  "hazard_justification": "<1-2 sentence explanation>",
  "primary_need": "MEDICAL" | "FIRE" | "RESCUE" | "HAZMAT" | "EVACUATION",
  "secondary_needs": ["<need1>", "<need2>"],
  "location_details": "<extracted location if present, else 'UNSPECIFIED'>",
  "casualties_reported": "<number or description, else 'UNKNOWN'>",
  "imminent_threats": ["<threat1>", "<threat2>"],
  "recommended_units": ["<unit1>", "<unit2>"],
  "ems_priority_code": "<P1|P2|P3>",
  "estimated_response_time_min": <integer>,
  "narrative_summary": "<3-5 sentence human-readable dispatch briefing>",
  "confidence_score": <float 0.0-1.0>,
  "image_observations": "<brief description of what's visible in evidence photos, or 'NO IMAGES PROVIDED'>"
}

Be precise. Hazard levels:
- RED: Immediate life threat, active fire/violence, critical injuries
- ORANGE: Serious injuries, contained fire, significant property risk
- YELLOW: Minor injuries, precautionary response, no immediate life threat
"""

def analyze_crisis(text: str, images: list) -> dict | None:
    model = get_gemini_client()
    if model is None:
        st.error("🔑 Please set your Google AI API key in the sidebar.")
        return None

    parts = [SYSTEM_PROMPT, f"\n\n=== CRISIS REPORT ===\n{text}\n\n=== END REPORT ==="]

    for img_file in images:
        try:
            img_bytes = img_file.read()
            img_part = {
                "inline_data": {
                    "mime_type": img_file.type,
                    "data": base64.b64encode(img_bytes).decode("utf-8"),
                }
            }
            parts.append(img_part)
        except Exception:
            pass

    try:
        response = model.generate_content(parts)
        raw = response.text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:])
        if raw.endswith("```"):
            raw = "\n".join(raw.split("\n")[:-1])
        return json.loads(raw)
    except json.JSONDecodeError as e:
        st.error(f"JSON parse error: {e}\n\nRaw response:\n{response.text[:500]}")
        return None
    except Exception as e:
        st.error(f"Gemini API error: {e}")
        return None

# ══════════════════════════════════════════════
#  RIGHT COLUMN — Output / Dispatch Panel
# ══════════════════════════════════════════════
with col_output:
    st.markdown('<div class="panel-label">Emergency Dispatch Intelligence</div>', unsafe_allow_html=True)

    if dispatch_btn:
        if not crisis_text.strip():
            st.warning("⚠️ Please enter crisis data before analyzing.")
        else:
            with st.spinner("🔄 ANALYZING CRISIS DATA — AI ENGINE PROCESSING..."):
                result = analyze_crisis(crisis_text, uploaded_files or [])
                if result:
                    st.session_state["dispatch_result"] = result

    if "dispatch_result" not in st.session_state:
        # Empty state
        st.markdown("""
        <div class="glass-panel" style="min-height:540px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:1rem;">
            <div style="font-size:4rem; filter: drop-shadow(0 0 20px rgba(255,0,60,0.5));">📡</div>
            <div style="font-family:'Orbitron',monospace; font-size:1rem; color:rgba(255,0,60,0.7); letter-spacing:0.2em; text-align:center;">
                AWAITING CRISIS DATA
            </div>
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.78rem; color:#555; text-align:center; max-width:280px; line-height:1.8;">
                Enter unstructured crisis data on the left panel and click ANALYZE &amp; DISPATCH to generate an emergency response assessment.
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        result = st.session_state["dispatch_result"]

        # ── Hazard Level Badge
        level = result.get("hazard_level", "YELLOW")
        hazard_icon = {"RED": "🔴", "ORANGE": "🟠", "YELLOW": "🟡"}.get(level, "⚪")

        st.markdown(f"""
        <div class="glass-panel">
            <div class="panel-label">Hazard Assessment</div>
            <div style="display:flex; align-items:center; gap:1rem; flex-wrap:wrap;">
                <div class="hazard-badge hazard-{level}">
                    {hazard_icon} {level}
                </div>
                <div style="font-family:'Share Tech Mono',monospace; font-size:0.82rem; color:#aaa; max-width:340px;">
                    {result.get('hazard_justification', '')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Metrics Row
        m1, m2, m3 = st.columns(3)
        need_icon = {"MEDICAL":"🏥","FIRE":"🔥","RESCUE":"⛑️","HAZMAT":"☣️","EVACUATION":"🚨"}.get(result.get("primary_need",""), "🆘")
        ems_colors = {"P1":"#ff003c","P2":"#ff6a00","P3":"#ffe600"}
        ems_code = result.get("ems_priority_code","P1")

        with m1:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-tile-icon">{need_icon}</div>
                <div class="metric-tile-label">Primary Need</div>
                <div class="metric-tile-value">{result.get('primary_need','—')}</div>
            </div>""", unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-tile-icon">🆘</div>
                <div class="metric-tile-label">EMS Priority</div>
                <div class="metric-tile-value" style="color:{ems_colors.get(ems_code,'#ff003c')}">{ems_code}</div>
            </div>""", unsafe_allow_html=True)

        with m3:
            confidence = result.get("confidence_score", 0)
            conf_pct = f"{confidence*100:.0f}%"
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-tile-icon">🎯</div>
                <div class="metric-tile-label">AI Confidence</div>
                <div class="metric-tile-value">{conf_pct}</div>
            </div>""", unsafe_allow_html=True)

        # ── Details
        st.markdown("""
        <div class="glass-panel">
            <div class="panel-label">Dispatch Briefing</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""<div class="summary-box">{result.get('narrative_summary','No summary available.')}</div>""",
                    unsafe_allow_html=True)

        d1, d2 = st.columns(2)
        with d1:
            st.markdown('<div class="section-title">🚑 Recommended Units</div>', unsafe_allow_html=True)
            units = result.get("recommended_units", [])
            for u in units:
                st.markdown(f"- `{u}`")

            st.markdown('<div class="section-title">⚠️ Imminent Threats</div>', unsafe_allow_html=True)
            threats = result.get("imminent_threats", [])
            for t in threats:
                st.markdown(f"- {t}")

        with d2:
            st.markdown('<div class="section-title">📍 Location</div>', unsafe_allow_html=True)
            st.markdown(f"**{result.get('location_details','Unspecified')}**")

            st.markdown('<div class="section-title">🩸 Casualties</div>', unsafe_allow_html=True)
            st.markdown(f"{result.get('casualties_reported','Unknown')}")

            st.markdown('<div class="section-title">⏱ Est. Response Time</div>', unsafe_allow_html=True)
            st.markdown(f"**{result.get('estimated_response_time_min','—')} minutes**")

        if result.get("secondary_needs"):
            st.markdown('<div class="section-title">🔗 Secondary Needs</div>', unsafe_allow_html=True)
            st.markdown(" · ".join([f"`{n}`" for n in result["secondary_needs"]]))

        if result.get("image_observations") and result["image_observations"] != "NO IMAGES PROVIDED":
            st.markdown('<div class="section-title">📸 Image Analysis</div>', unsafe_allow_html=True)
            st.markdown(result["image_observations"])

        st.markdown('</div>', unsafe_allow_html=True)

        # ── JSON Block
        with st.expander("📦 System Integration JSON", expanded=False):
            cleaned = {k: v for k, v in result.items()}
            json_str = json.dumps(cleaned, indent=2)
            st.markdown(f'<div class="json-block"><pre>{json_str}</pre></div>', unsafe_allow_html=True)
            st.download_button(
                "⬇️ Download JSON",
                data=json_str,
                file_name="lifepulse_dispatch.json",
                mime="application/json",
                use_container_width=True,
            )


