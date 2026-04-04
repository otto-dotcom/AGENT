"""
TRIBE v2 — Brain Encoding Demo
HuggingFace Spaces · ZeroGPU
"""

import os

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
os.environ["PYVISTA_OFF_SCREEN"] = "true"
os.environ["DISPLAY"] = ""
os.environ["VTK_DEFAULT_RENDER_WINDOW_OFFSCREEN"] = "true"

import tempfile
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")

import gradio as gr
import spaces

# ── Constants ──────────────────────────────────────────────────────────────────
CACHE_FOLDER = Path("./cache")
CACHE_FOLDER.mkdir(parents=True, exist_ok=True)

SAMPLE_VIDEO_URL = "https://download.blender.org/durian/trailer/sintel_trailer-480p.mp4"

FIRE_COLORSCALE = [
    [0.00, "rgb(0,0,0)"],
    [0.15, "rgb(30,0,20)"],
    [0.30, "rgb(120,10,5)"],
    [0.50, "rgb(200,50,0)"],
    [0.65, "rgb(240,120,0)"],
    [0.80, "rgb(255,200,20)"],
    [1.00, "rgb(255,255,220)"],
]

# ── HTML blocks ────────────────────────────────────────────────────────────────
HEADER = """
<div id="tribe-header">
  <div class="tribe-wordmark">TRIBE v2</div>
  <p class="tribe-subtitle">
    A Foundation Model of Vision, Audition &amp; Language for In-Silico Neuroscience
  </p>
  <div class="tribe-links">
    <a href="https://huggingface.co/facebook/tribev2" target="_blank">Weights</a>
    <span class="sep">·</span>
    <a href="https://ai.meta.com/research/publications/a-foundation-model-of-vision-audition-and-language-for-in-silico-neuroscience/" target="_blank">Paper</a>
    <span class="sep">·</span>
    <a href="https://github.com/facebookresearch/tribev2" target="_blank">Code</a>
    <span class="sep">·</span>
    <a href="https://aidemos.atmeta.com/tribev2/" target="_blank">Official Demo</a>
  </div>
</div>
"""

NOTICE = """
<div class="tribe-notice">
  <span class="notice-label">Note</span>
  This demo runs on ZeroGPU (shared H200). Processing video and audio inputs
  involves downloading WhisperX on first run and may take 2–4 minutes.
  Subsequent runs within the same session are significantly faster.
</div>
"""

MODEL_INFO = """
<div class="info-grid">
  <div class="info-item">
    <div class="info-key">Architecture</div>
    <div class="info-val">Transformer encoder mapping multimodal features to cortical surface activity</div>
  </div>
  <div class="info-item">
    <div class="info-key">Encoders</div>
    <div class="info-val">V-JEPA2 (video) · Wav2Vec-BERT 2.0 (audio) · LLaMA 3.2-3B (text)</div>
  </div>
  <div class="info-item">
    <div class="info-key">Preprocessing</div>
    <div class="info-val">WhisperX extracts word-level timestamps from audio/video, enabling the text encoder to process speech with precise timing</div>
  </div>
  <div class="info-item">
    <div class="info-key">Output</div>
    <div class="info-val">Predicted fMRI BOLD responses on the fsaverage5 cortical mesh — 20,484 vertices, 1 TR = 1 s</div>
  </div>
  <div class="info-item">
    <div class="info-key">Training data</div>
    <div class="info-val">700+ healthy subjects exposed to images, podcasts, videos, and text (naturalistic paradigm)</div>
  </div>
  <div class="info-item">
    <div class="info-key">License</div>
    <div class="info-val">CC BY-NC 4.0 — research and non-commercial use only</div>
  </div>
</div>
"""

NOTES_HTML = """
<div class="tribe-footer">
  <span class="footer-label">Usage notes</span>
  <ul>
    <li>The 3D brain view is interactive: drag to rotate, scroll to zoom, use the slider to navigate timesteps.</li>
    <li>The text encoder requires access to the gated <strong>LLaMA 3.2-3B</strong> model on Hugging Face. Text input may fail if access is not granted.</li>
    <li>ZeroGPU sessions are ephemeral. If the Space goes idle, the next request re-initialises the model (~30 s).</li>
    <li>This is an unofficial community demo. For the official interactive visualisation, see <a href="https://aidemos.atmeta.com/tribev2/" target="_blank">aidemos.atmeta.com/tribev2</a>.</li>
  </ul>
</div>
"""

# ── Singletons ─────────────────────────────────────────────────────────────────
_model      = None
_plotter    = None
_mesh_cache = None


def _load_model():
    global _model, _plotter
    if _model is None:
        from tribev2.demo_utils import TribeModel
        from tribev2.plotting import PlotBrain

        hf_token = os.environ.get("HF_TOKEN")
        if hf_token:
            from huggingface_hub import login
            login(token=hf_token, add_to_git_credential=False)

        _model   = TribeModel.from_pretrained("facebook/tribev2", cache_folder=CACHE_FOLDER)
        _plotter = PlotBrain(mesh="fsaverage5")
    return _model, _plotter


def _load_mesh():
    global _mesh_cache
    if _mesh_cache is None:
        from nilearn import datasets, surface
        fsaverage = datasets.fetch_surf_fsaverage("fsaverage5")
        coords_L, faces_L = surface.load_surf_mesh(fsaverage.pial_left)
        coords_R, faces_R = surface.load_surf_mesh(fsaverage.pial_right)
        _mesh_cache = (
            np.array(coords_L), np.array(faces_L),
            np.array(coords_R), np.array(faces_R),
        )
    return _mesh_cache


# ── 3-D brain builder ──────────────────────────────────────────────────────────
def build_3d_figure(preds: np.ndarray, vmin_val: float = 0.5) -> str:
    """Return an HTML iframe with interactive 3-D brain — white base,
    fire activation overlay, centered slider."""
    import plotly.graph_objects as go
    import json
    import html as _html

    coords_L, faces_L, coords_R, faces_R = _load_mesh()
    n_verts_L = coords_L.shape[0]
    n_t       = preds.shape[0]

    # Normalization: same threshold as the timeline slider
    vmax = np.percentile(preds, 99)
    vmin = vmin_val

    BG   = "#1a1a2e"
    MONO = "ui-monospace, 'Cascadia Code', 'Source Code Pro', monospace"

    # White base colorscale: 0→white, fire only above threshold
    WHITE_FIRE = [
        [0.00, "rgb(245,245,245)"],
        [0.25, "rgb(220,180,160)"],
        [0.45, "rgb(200,60,10)"],
        [0.65, "rgb(240,120,0)"],
        [0.80, "rgb(255,200,20)"],
        [1.00, "rgb(255,255,220)"],
    ]

    mesh_kw = dict(
        colorscale=WHITE_FIRE, cmin=0, cmax=1, showscale=False,
        flatshading=False, hoverinfo="skip",
        lighting=dict(ambient=0.60, diffuse=0.85, specular=0.25, roughness=0.45),
        lightposition=dict(x=80, y=180, z=200),
    )

    def _vals(t):
        v = preds[t]
        return np.clip((v - vmin) / max(vmax - vmin, 1e-8), 0, 1)

    def _traces(t):
        vn = _vals(t)
        offset = 8.0
        tL = go.Mesh3d(
            x=coords_L[:, 0] - offset, y=coords_L[:, 1], z=coords_L[:, 2],
            i=faces_L[:, 0], j=faces_L[:, 1], k=faces_L[:, 2],
            intensity=vn[:n_verts_L], name="Left", **mesh_kw)
        tR = go.Mesh3d(
            x=coords_R[:, 0] + offset, y=coords_R[:, 1], z=coords_R[:, 2],
            i=faces_R[:, 0], j=faces_R[:, 1], k=faces_R[:, 2],
            intensity=vn[n_verts_L:], name="Right", **mesh_kw)
        return tL, tR

    def _intensity_only(t):
        vn = _vals(t)
        return [go.Mesh3d(intensity=vn[:n_verts_L]),
                go.Mesh3d(intensity=vn[n_verts_L:])]

    tL0, tR0 = _traces(0)
    frames = [
        go.Frame(data=_intensity_only(t), name=str(t),
                 layout=go.Layout(title_text=f"t = {t} s"))
        for t in range(n_t)
    ]

    slider_steps = [
        dict(args=[[str(t)], dict(frame=dict(duration=0, redraw=True),
                                  mode="immediate", transition=dict(duration=0))],
             label=str(t), method="animate")
        for t in range(n_t)
    ]

    fig = go.Figure(
        data=[tL0, tR0],
        frames=frames,
        layout=go.Layout(
            height=500,
            paper_bgcolor=BG,
            plot_bgcolor=BG,
            scene=dict(
                bgcolor=BG,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                camera=dict(
                    eye=dict(x=0, y=-1.9, z=0.4),
                    up=dict(x=0, y=0, z=1),
                ),
                aspectmode="data",
            ),
            margin=dict(l=0, r=0, t=8, b=70),
            title=dict(
                text="t = 0 s  —  drag to rotate  ·  scroll to zoom",
                font=dict(color="#9ca3af", family=MONO, size=11),
                x=0.5,
            ),
            updatemenus=[],
            sliders=[dict(
                active=0, steps=slider_steps,
                currentvalue=dict(
                    prefix="t = ", suffix=" s",
                    font=dict(color="#9ca3af", family=MONO, size=11),
                    visible=True, xanchor="center",
                ),
                pad=dict(b=8, t=8),
                len=0.85, x=0.5, xanchor="center", y=0,
                bgcolor="#111827", bordercolor="#1f2937",
                tickcolor="#374151",
                font=dict(color="#6b7280", family=MONO, size=10),
            )],
        ),
    )

    inner_html = fig.to_html(
        include_plotlyjs=True,
        full_html=True,
        config={"responsive": True, "displayModeBar": False},
    )
    srcdoc = _html.escape(inner_html, quote=True)
    return (
        f'<iframe srcdoc="{srcdoc}" '
        f'style="width:100%;height:520px;border:none;background:{BG};" '
        f'scrolling="no"></iframe>'
    )


# ── Core inference ─────────────────────────────────────────────────────────────
@spaces.GPU(duration=120)
def run_prediction(input_type, video_file, audio_file, text_input, n_timesteps, vmin_val, show_stimuli):
    model, plotter = _load_model()

    if input_type == "Video" and video_file is not None:
        df      = model.get_events_dataframe(video_path=video_file)
        stimuli = show_stimuli
    elif input_type == "Audio" and audio_file is not None:
        df      = model.get_events_dataframe(audio_path=audio_file)
        stimuli = False
    elif input_type == "Text" and text_input.strip():
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
            tmp.write(text_input.strip())
            fpath = tmp.name
        try:
            df = model.get_events_dataframe(text_path=fpath)
        finally:
            os.unlink(fpath)
        stimuli = False
    else:
        raise gr.Error("Please provide an input for the selected modality.")

    # ZeroGPU runs in a daemon process — DataLoader cannot spawn children.
    import torch.utils.data
    _orig = torch.utils.data.DataLoader.__init__
    def _patched(self, *a, **kw):
        kw["num_workers"] = 0
        _orig(self, *a, **kw)
    torch.utils.data.DataLoader.__init__ = _patched
    try:
        preds, segments = model.predict(events=df)
    finally:
        torch.utils.data.DataLoader.__init__ = _orig

    n = min(int(n_timesteps), len(preds))
    if n == 0:
        raise gr.Error("Model returned no predictions for this input.")

    preds_n = preds[:n]

    timeline_fig = plotter.plot_timesteps(
        preds_n, segments=segments[:n],
        cmap="fire", norm_percentile=99, vmin=vmin_val,
        alpha_cmap=(0.0, 0.2), show_stimuli=stimuli,
    )
    timeline_fig.set_dpi(180)
    brain_3d_html = build_3d_figure(preds_n, vmin_val=vmin_val)

    status = (
        f"{preds.shape[0]} timesteps  ×  {preds.shape[1]:,} vertices  "
        f"(fsaverage5)  —  showing first {n}"
    )
    return brain_3d_html, timeline_fig, status


def download_sample_video():
    from tribev2.demo_utils import download_file
    dest = CACHE_FOLDER / "sintel_trailer.mp4"
    download_file(SAMPLE_VIDEO_URL, dest)
    return str(dest)


# ── CSS ────────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

body, .gradio-container {
    background: #0b0e17 !important;
    color: #c9d4e8 !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}
.gradio-container {
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 28px 56px !important;
}

/* ── Header ── */
#tribe-header {
    padding: 36px 0 22px;
    text-align: center;
    border-bottom: 1px solid #1a2235;
}
.tribe-wordmark {
    font-size: 2.4rem;
    font-weight: 600;
    letter-spacing: -0.03em;
    color: #edf2ff;
    line-height: 1;
    margin-bottom: 10px;
}
.tribe-subtitle {
    font-size: 0.87rem;
    color: #5a6a88;
    margin: 0 0 12px;
    line-height: 1.6;
}
.tribe-links { font-size: 0.76rem; }
.tribe-links a { color: #5a7aaa; text-decoration: none; transition: color 0.15s; }
.tribe-links a:hover { color: #a0b8d8; }
.tribe-links .sep { margin: 0 8px; color: #1e2a3a; }

/* ── Notice ── */
.tribe-notice {
    background: #0d1120;
    border: 1px solid #1a2235;
    border-left: 3px solid #1b4f8a;
    border-radius: 4px;
    padding: 11px 16px;
    font-size: 0.79rem;
    color: #5a7aaa;
    line-height: 1.6;
    margin: 16px 0 0;
}
.notice-label {
    font-weight: 600;
    color: #4a9fd4;
    margin-right: 8px;
    text-transform: uppercase;
    font-size: 0.66rem;
    letter-spacing: 0.1em;
}

/* ── Panel box — applied via elem_classes ── */
.tribe-box {
    background: #0d1120 !important;
    border: 1px solid #1a2235 !important;
    border-radius: 6px !important;
    overflow: hidden !important;
    padding: 0 !important;
}

/* ── Section label ── */
.sec-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 11px 16px;
    border-bottom: 1px solid #1a2235;
    margin: 0;
}
.sec-label-input    { color: #4a9fd4; }
.sec-label-brain    { color: #4a9fd4; }
.sec-label-timeline { color: #4a9fd4; }

/* ── Inner padding for input col ── */
.input-col-inner { padding: 14px 16px 14px; }
.input-col-inner > .gr-group,
.input-col-inner > div { margin-bottom: 10px; }

/* ── Modality buttons ── */
.modality-selector { width: 100% !important; }
.modality-selector > .wrap {
    display: grid !important;
    grid-template-columns: 1fr 1fr 1fr !important;
    gap: 5px !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    width: 100% !important;
}
.modality-selector label {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 9px 4px !important;
    border-radius: 4px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.18s !important;
    user-select: none !important;
    text-align: center !important;
    border: 1px solid transparent !important;
}
/* Force white text on ALL spans inside modality labels */
.modality-selector label span,
.modality-selector label > span,
.modality-selector span { 
    color: #ffffff !important; 
    display: inline !important;
}
/* Video — blue */
.modality-selector label:nth-child(1) {
    background: #1a4a7a !important;
    border-color: #2478bb !important;
}
.modality-selector label:nth-child(1):has(input:checked) {
    background: #2478bb !important;
    border-color: #4a9fd4 !important;
    box-shadow: 0 0 10px rgba(36,120,187,0.5) !important;
}
/* Audio — teal */
.modality-selector label:nth-child(2) {
    background: #0d4a3a !important;
    border-color: #0f9e80 !important;
}
.modality-selector label:nth-child(2):has(input:checked) {
    background: #0f9e80 !important;
    border-color: #2dbba3 !important;
    box-shadow: 0 0 10px rgba(15,158,128,0.5) !important;
}
/* Text — indigo */
.modality-selector label:nth-child(3) {
    background: #2a2060 !important;
    border-color: #4a5eab !important;
}
.modality-selector label:nth-child(3):has(input:checked) {
    background: #4a5eab !important;
    border-color: #7080d0 !important;
    box-shadow: 0 0 10px rgba(74,94,171,0.5) !important;
}
.modality-selector input[type=radio] { display: none !important; }

/* ── Gradio component labels ── */
label > span {
    font-size: 0.69rem !important;
    color: #3a4f6a !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
}

/* ── Upload / video / audio ── */
.gr-video, .gr-audio,
[data-testid="video"], [data-testid="audio"] {
    background: #080c18 !important;
    border: 1px solid #1a2235 !important;
    border-radius: 4px !important;
    width: 100% !important;
    color: #c9d4e8 !important;
}

/* Wrapper group: no border, no padding, invisible groups leave zero trace */
.upload-slot-wrap {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* The actual component (Video/Audio) — fixed height */
.upload-slot {
    height: 220px !important;
    min-height: 220px !important;
    max-height: 220px !important;
    overflow: hidden !important;
    position: relative !important;
}
.upload-slot > * { max-height: 220px !important; overflow: hidden !important; }
.upload-slot video {
    width: 100% !important;
    height: 170px !important;
    max-height: 170px !important;
    object-fit: contain !important;
    display: block !important;
    background: #080c18 !important;
}

/* Modality label — add breathing room below the "Modality" title */
.modality-selector > .wrap { margin-top: 6px !important; }

/* ── Main row: panels align to top, NOT stretched to equal height ── */
#main-row {
    align-items: flex-start !important;
}
/* panel-brain shrinks to fit its content (the plot), no empty space */
.panel-brain {
    align-self: flex-start !important;
}

/* ── Textarea ── */
textarea {
    background: #080c18 !important;
    border: 1px solid #1a2235 !important;
    border-radius: 4px !important;
    color: #c9d4e8 !important;
    font-size: 0.86rem !important;
    line-height: 1.6 !important;
    resize: vertical !important;
    width: 100% !important;
}
textarea::placeholder { color: #3a4f6a !important; }
textarea:focus { border-color: #1b4f8a !important; outline: none !important; }

/* ── Slider & checkbox ── */
input[type=range]    { accent-color: #2478bb !important; }
input[type=checkbox] { accent-color: #2478bb !important; }

/* ── Run button ── */
.btn-run button {
    background: #edf2ff !important;
    color: #0b0e17 !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    letter-spacing: 0.03em !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 11px 0 !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: background 0.15s !important;
    margin-top: 8px !important;
}
.btn-run button:hover { background: #c0cfe8 !important; }

/* ── Sample button ── */
.btn-sample button {
    background: transparent !important;
    color: #3a4f6a !important;
    border: 1px solid #1a2235 !important;
    border-radius: 4px !important;
    font-size: 0.74rem !important;
    padding: 5px 12px !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    width: 100% !important;
    margin-top: 6px !important;
}
.btn-sample button:hover { color: #7a9abf !important; border-color: #1b4f8a !important; }

/* ── Status ── */
.status-line p {
    font-size: 0.72rem !important;
    color: #3a4f6a !important;
    margin: 8px 0 0 !important;
    font-variant-numeric: tabular-nums !important;
    font-family: ui-monospace, monospace !important;
}

/* ── Plot containers ── */
.plot-3d {
    width: 100% !important;
    min-height: 500px !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
    display: block !important;
}
.plot-3d > div { width: 100% !important; }
.plot-timeline {
    background: #07090f !important;
    width: 100% !important;
    min-height: 340px !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
}
.plot-timeline .label-wrap { display: none !important; }
.plot-timeline .wrap { padding: 0 !important; margin: 0 !important; }
.panel-brain .wrap,
.panel-brain > * { gap: 0 !important; padding-top: 0 !important; margin-top: 0 !important; }

/* ── Accordion ── */
.gr-accordion > .label-wrap {
    background: transparent !important;
    border: none !important;
    border-top: 1px solid #1a2235 !important;
    padding: 9px 0 !important;
    font-size: 0.74rem !important;
    color: #3a4f6a !important;
}
.gr-accordion > .label-wrap:hover { color: #5a7aaa !important; }

/* ── Model info ── */
.info-grid { display: flex; flex-direction: column; }
.info-item {
    display: flex; gap: 20px; padding: 9px 0;
    border-bottom: 1px solid #0e1220;
    font-size: 0.79rem; line-height: 1.55;
}
.info-item:last-child { border-bottom: none; }
.info-key {
    min-width: 120px; color: #3a4f6a; font-weight: 500;
    flex-shrink: 0; font-size: 0.71rem;
    text-transform: uppercase; letter-spacing: 0.07em; padding-top: 2px;
}
.info-val { color: #5a7aaa; }

/* ── Footer ── */
.tribe-footer {
    margin-top: 24px; padding-top: 16px;
    border-top: 1px solid #1a2235;
    font-size: 0.74rem; color: #3a4f6a; line-height: 1.7;
}
.footer-label {
    display: block; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.09em; font-size: 0.63rem; color: #1e2a3a; margin-bottom: 8px;
}
.tribe-footer ul { margin: 0; padding-left: 16px; }
.tribe-footer li { margin-bottom: 4px; }
.tribe-footer a { color: #3a4f6a; text-decoration: none; }
.tribe-footer a:hover { color: #5a7aaa; }
.tribe-footer strong { color: #4a6080; font-weight: 500; }
"""

# ── Brain placeholder ─────────────────────────────────────────────────────────
BRAIN_PLACEHOLDER = """
<div style="
  width:100%; height:500px;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  color:#1e2a3a; font-family:ui-monospace,'Cascadia Code','Source Code Pro',monospace;
  font-size:0.78rem; letter-spacing:0.06em; gap:14px;
  background:#0d1120;
">
  <svg width="54" height="54" viewBox="0 0 54 54" fill="none" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="19" cy="27" rx="13" ry="17" stroke="#1e3a5a" stroke-width="1.5"/>
    <ellipse cx="35" cy="27" rx="13" ry="17" stroke="#1e3a5a" stroke-width="1.5"/>
    <path d="M19 10 Q27 6 35 10" stroke="#1e3a5a" stroke-width="1.5" fill="none"/>
    <path d="M19 44 Q27 48 35 44" stroke="#1e3a5a" stroke-width="1.5" fill="none"/>
    <line x1="27" y1="10" x2="27" y2="44" stroke="#1e3a5a" stroke-width="1" stroke-dasharray="3 3"/>
    <path d="M12 20 Q9 27 12 34" stroke="#1e3a5a" stroke-width="1.2" fill="none"/>
    <path d="M42 20 Q45 27 42 34" stroke="#1e3a5a" stroke-width="1.2" fill="none"/>
  </svg>
  <span style="color:#1e3a5a; text-transform:uppercase; letter-spacing:0.12em;">
    Run prediction to visualize cortical activity
  </span>
</div>
"""

# ── UI ─────────────────────────────────────────────────────────────────────────
with gr.Blocks() as demo:

    gr.HTML(HEADER)
    gr.HTML(NOTICE)

    with gr.Accordion("About the model", open=False):
        gr.HTML(MODEL_INFO)

    with gr.Row(elem_id="main-row"):

        # ── Col left: Input ──
        with gr.Column(scale=1, elem_classes=["tribe-box", "panel-input"]):
            gr.HTML('<div class="sec-label sec-label-input">Input</div>')
            with gr.Column(elem_classes=["input-col-inner"]):

                input_type = gr.Radio(
                    choices=["Video", "Audio", "Text"],
                    value="Video",
                    label="Modality",
                    elem_classes=["modality-selector"],
                )

                with gr.Group(visible=True, elem_classes=["upload-slot-wrap"]) as video_group:
                    video_file = gr.Video(label="Video file — mp4, mkv, avi", elem_classes=["upload-slot"])

                sample_btn = gr.Button(
                    "Load sample  (Sintel trailer)",
                    elem_classes=["btn-sample"],
                    visible=True,
                )

                with gr.Group(visible=False, elem_classes=["upload-slot-wrap"]) as audio_group:
                    audio_file = gr.Audio(
                        label="Audio file — wav, mp3, flac",
                        type="filepath",
                        elem_classes=["upload-slot"],
                    )

                with gr.Group(visible=False) as text_group:
                    text_input = gr.Textbox(
                        label="Text",
                        placeholder="Enter text. Converted to speech internally.",
                        lines=4, max_lines=8,
                    )

                with gr.Accordion("Settings", open=True):
                    n_timesteps = gr.Slider(
                        minimum=1, maximum=30, value=10, step=1,
                        label="Timesteps to visualize  (1 TR = 1 s)",
                    )
                    vmin_slider = gr.Slider(
                        minimum=-0.5, maximum=1.0, value=0.5, step=0.05,
                        label="Activation threshold (vmin)  —  lower = more brain covered",
                    )
                    show_stimuli = gr.Checkbox(
                        value=True,
                        label="Overlay stimulus frames (video only)",
                    )

                run_btn   = gr.Button("Run prediction", elem_classes=["btn-run"])
                status_md = gr.Markdown(value="", elem_classes=["status-line"])

        # ── Col right: 3D Brain ──
        with gr.Column(scale=2, elem_classes=["tribe-box", "panel-brain"]):
            gr.HTML('<div class="sec-label sec-label-brain">Cortical surface &mdash; predicted BOLD response &nbsp;&middot;&nbsp; drag to rotate &nbsp;&middot;&nbsp; scroll to zoom</div>')
            brain_3d = gr.HTML(value=BRAIN_PLACEHOLDER, elem_classes=["plot-3d"])

    with gr.Row():
        with gr.Column(elem_classes=["tribe-box"]):
            gr.HTML('<div class="sec-label sec-label-timeline">Timeline &mdash; stimulus and predicted brain response per timestep</div>')
            timeline_plot = gr.Plot(elem_classes=["plot-timeline"])

    gr.HTML(NOTES_HTML)

    # ── Callbacks ──
    def toggle_inputs(choice):
        return (
            gr.update(visible=choice == "Video"),
            gr.update(visible=choice == "Audio"),
            gr.update(visible=choice == "Text"),
            gr.update(visible=choice == "Video"),
        )

    input_type.change(
        fn=toggle_inputs, inputs=[input_type],
        outputs=[video_group, audio_group, text_group, sample_btn],
    )
    sample_btn.click(fn=download_sample_video, inputs=[], outputs=[video_file])
    run_btn.click(
        fn=run_prediction,
        inputs=[input_type, video_file, audio_file, text_input, n_timesteps, vmin_slider, show_stimuli],
        outputs=[brain_3d, timeline_plot, status_md],
        show_progress="full",
    )

demo.launch(
    ssr_mode=False,
    css=CSS,
    theme=gr.themes.Base(
        primary_hue=gr.themes.colors.slate,
        neutral_hue=gr.themes.colors.slate,
        font=gr.themes.GoogleFont("Inter"),
    ),
)