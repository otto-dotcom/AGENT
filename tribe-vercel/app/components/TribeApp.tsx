'use client';

import { useState, useRef, useCallback } from 'react';

const SPACE_ID = 'Otto808808/tribe-v2';

type Modality = 'Video' | 'Audio' | 'Text';

interface PredictResult {
  brain3d: string;
  timelineUrl: string;
  status: string;
}

// Lazy-load @gradio/client (browser-only)
let _client: Awaited<ReturnType<(typeof import('@gradio/client'))['Client']['connect']>> | null = null;

async function getClient() {
  const { Client } = await import('@gradio/client');
  if (!_client) {
    _client = await Client.connect(SPACE_ID);
  }
  return _client;
}

export default function TribeApp() {
  const [modality, setModality] = useState<Modality>('Text');
  const [text, setText] = useState(
    'A scientist carefully examines colorful brain scans on a large monitor, pointing out areas that light up during speech and movement. Outside the window, the city hums with activity.'
  );
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [nTimesteps, setNTimesteps] = useState(10);
  const [vmin, setVmin] = useState(0.5);

  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState('');
  const [result, setResult] = useState<PredictResult | null>(null);
  const [error, setError] = useState('');

  const blobUrlRef = useRef<string | null>(null);

  const run = useCallback(async () => {
    if (loading) return;
    setLoading(true);
    setError('');
    setResult(null);
    setProgress('Connecting to HuggingFace Space…');

    if (blobUrlRef.current) {
      URL.revokeObjectURL(blobUrlRef.current);
      blobUrlRef.current = null;
    }

    try {
      const client = await getClient();

      // Log available API endpoints for debugging
      try {
        const api = await client.view_api();
        console.log('[TRIBE] Available API endpoints:', JSON.stringify(api, null, 2));
      } catch { /* non-fatal */ }

      setProgress('Queued — processing takes 2–4 min on first run…');

      const videoArg = modality === 'Video' && videoFile ? videoFile : null;
      const audioArg = modality === 'Audio' && audioFile ? audioFile : null;
      const textArg  = modality === 'Text' ? text.trim() : '';

      const args = [modality, videoArg, audioArg, textArg, nTimesteps, vmin, modality === 'Video'];

      // Endpoint is /predict (fn_index 2) — confirmed from API introspection
      const res = await client.predict('/predict', args);

      const data = res.data as [string, unknown, string];
      const brain3dHtml = data[0] as string;
      const timelineRaw = data[1];
      const statusStr   = data[2] as string;

      // gr.Plot returns { url, path, ... } or a plain string
      let timelineUrl = '';
      if (timelineRaw) {
        if (typeof timelineRaw === 'string') {
          timelineUrl = timelineRaw;
        } else if (typeof timelineRaw === 'object' && timelineRaw !== null) {
          const obj = timelineRaw as Record<string, unknown>;
          timelineUrl = (obj.url ?? obj.path ?? '') as string;
          if (timelineUrl && !timelineUrl.startsWith('http')) {
            timelineUrl = `https://otto808808-tribe-v2.hf.space/file=${timelineUrl}`;
          }
        }
      }

      setResult({ brain3d: brain3dHtml, timelineUrl, status: statusStr });
      setProgress('');
    } catch (e: unknown) {
      console.error('[TRIBE] Prediction error:', e);
      let msg: string;
      if (e instanceof Error) {
        // Gradio sometimes embeds a JSON payload in the Error message
        try {
          const parsed = JSON.parse(e.message);
          msg = parsed.title
            ? `${parsed.title}: ${parsed.message}`
            : parsed.message ?? e.message;
        } catch {
          msg = e.message;
        }
      } else if (typeof e === 'object' && e !== null) {
        const obj = e as Record<string, unknown>;
        msg = obj.title
          ? `${obj.title}: ${obj.message}`
          : obj.message
            ? String(obj.message)
            : JSON.stringify(e);
      } else {
        msg = String(e);
      }
      setError(msg);
      setProgress('');
      _client = null;
    } finally {
      setLoading(false);
    }
  }, [loading, modality, text, videoFile, audioFile, nTimesteps, vmin]);

  // Inject the brain HTML (which is already an <iframe srcdoc="..."> string)
  const brainRef = useCallback((node: HTMLDivElement | null) => {
    if (!node || !result?.brain3d) return;
    node.innerHTML = result.brain3d;
    const iframe = node.querySelector('iframe');
    if (iframe) {
      iframe.style.width = '100%';
      iframe.style.height = '520px';
      iframe.style.border = 'none';
    }
  }, [result?.brain3d]);

  const tabClass = (m: Modality) =>
    modality === m ? `tab-btn active-${m.toLowerCase()}` : 'tab-btn';

  return (
    <>
      <header className="header">
        <h1>TRIBE v2</h1>
        <p>A Foundation Model of Vision, Audition &amp; Language for In-Silico Neuroscience</p>
        <div className="header-links">
          <a href="https://huggingface.co/facebook/tribev2" target="_blank" rel="noreferrer">Weights</a>
          <span>·</span>
          <a href="https://ai.meta.com/research/publications/a-foundation-model-of-vision-audition-and-language-for-in-silico-neuroscience/" target="_blank" rel="noreferrer">Paper</a>
          <span>·</span>
          <a href="https://github.com/facebookresearch/tribev2" target="_blank" rel="noreferrer">Code</a>
        </div>
      </header>

      <div className="notice">
        <strong>Note</strong>&nbsp; This app calls the HuggingFace ZeroGPU Space directly from your browser.
        First run may take <strong>2–4 minutes</strong> (downloads WhisperX). Subsequent runs are faster.
        <strong> Text</strong> is the fastest modality to test with.
      </div>

      <div className="main-grid">
        {/* Input panel */}
        <div className="panel">
          <div className="panel-label">Input</div>
          <div className="panel-body">

            <div>
              <div className="field-label">Modality</div>
              <div className="modality-tabs">
                {(['Video', 'Audio', 'Text'] as Modality[]).map(m => (
                  <button key={m} className={tabClass(m)} onClick={() => setModality(m)}>{m}</button>
                ))}
              </div>
            </div>

            {modality === 'Video' && (
              <div>
                <div className="field-label">Video file</div>
                <label className="file-drop">
                  <input type="file" accept="video/*" onChange={e => setVideoFile(e.target.files?.[0] ?? null)} />
                  <div className="file-drop-icon">🎬</div>
                  <div className="file-drop-text">Click or drag a video file</div>
                  <div className="file-drop-hint">mp4 · mkv · avi</div>
                  {videoFile && <div className="file-name">✓ {videoFile.name}</div>}
                </label>
              </div>
            )}

            {modality === 'Audio' && (
              <div>
                <div className="field-label">Audio file</div>
                <label className="file-drop">
                  <input type="file" accept="audio/*" onChange={e => setAudioFile(e.target.files?.[0] ?? null)} />
                  <div className="file-drop-icon">🎵</div>
                  <div className="file-drop-text">Click or drag an audio file</div>
                  <div className="file-drop-hint">wav · mp3 · flac</div>
                  {audioFile && <div className="file-name">✓ {audioFile.name}</div>}
                </label>
              </div>
            )}

            {modality === 'Text' && (
              <div>
                <div className="field-label">Text</div>
                <textarea
                  value={text}
                  onChange={e => setText(e.target.value)}
                  placeholder="Enter text to simulate neural response…"
                  rows={5}
                />
              </div>
            )}

            <div>
              <div className="field-label">Timesteps to visualize &nbsp;(1 TR = 1 s)</div>
              <div className="slider-row">
                <input type="range" min={1} max={30} step={1} value={nTimesteps}
                  onChange={e => setNTimesteps(Number(e.target.value))} />
                <span className="slider-val">{nTimesteps}</span>
              </div>
            </div>

            <div>
              <div className="field-label">Activation threshold (vmin)</div>
              <div className="slider-row">
                <input type="range" min={-0.5} max={1.0} step={0.05} value={vmin}
                  onChange={e => setVmin(Number(e.target.value))} />
                <span className="slider-val">{vmin.toFixed(2)}</span>
              </div>
            </div>

            <button className="run-btn" onClick={run} disabled={loading}>
              {loading ? 'Running…' : 'Run Prediction'}
            </button>

            {loading && <div className="loading-bar" />}
            {progress && <div className="status">{progress}</div>}
            {error && <div className="status error">Error: {error}</div>}
            {result && !loading && <div className="status ok">{result.status}</div>}
          </div>
        </div>

        {/* Results */}
        <div className="right-col">
          <div className="panel">
            <div className="panel-label">
              Cortical surface — predicted BOLD response &nbsp;·&nbsp; drag to rotate &nbsp;·&nbsp; scroll to zoom
            </div>
            <div className="brain-frame-wrap">
              {result?.brain3d ? (
                <div ref={brainRef} style={{ width: '100%', height: 520 }} />
              ) : (
                <div className="brain-placeholder">
                  <svg width="52" height="52" viewBox="0 0 54 54" fill="none">
                    <ellipse cx="19" cy="27" rx="13" ry="17" stroke="#1e3a5a" strokeWidth="1.5"/>
                    <ellipse cx="35" cy="27" rx="13" ry="17" stroke="#1e3a5a" strokeWidth="1.5"/>
                    <path d="M19 10 Q27 6 35 10" stroke="#1e3a5a" strokeWidth="1.5" fill="none"/>
                    <path d="M19 44 Q27 48 35 44" stroke="#1e3a5a" strokeWidth="1.5" fill="none"/>
                    <line x1="27" y1="10" x2="27" y2="44" stroke="#1e3a5a" strokeWidth="1" strokeDasharray="3 3"/>
                    <path d="M12 20 Q9 27 12 34" stroke="#1e3a5a" strokeWidth="1.2" fill="none"/>
                    <path d="M42 20 Q45 27 42 34" stroke="#1e3a5a" strokeWidth="1.2" fill="none"/>
                  </svg>
                  <span>Run prediction to visualize cortical activity</span>
                </div>
              )}
            </div>
          </div>

          {result?.timelineUrl && (
            <div className="panel timeline-wrap">
              <div className="panel-label">Timeline — stimulus + predicted brain response per timestep</div>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={result.timelineUrl} alt="Brain response timeline" />
            </div>
          )}
        </div>
      </div>

      <div style={{ marginTop: 40, fontSize: '0.72rem', color: 'var(--dim)', lineHeight: 1.7, borderTop: '1px solid var(--border)', paddingTop: 16 }}>
        <strong style={{ color: 'var(--border)', textTransform: 'uppercase', letterSpacing: '0.1em', fontSize: '0.62rem' }}>Notes</strong>
        <ul style={{ marginTop: 6, paddingLeft: 16 }}>
          <li>Text input requires the gated <strong style={{color:'var(--dim)'}}>LLaMA 3.2-3B</strong> model on HuggingFace — if text fails, try audio/video.</li>
          <li>The 3D view is interactive: drag to rotate, scroll to zoom, use the time slider to navigate seconds.</li>
          <li>Output is predicted fMRI BOLD on fsaverage5 mesh — 20,484 cortical vertices at 1 s resolution.</li>
          <li>This is an unofficial frontend. Model weights and official demo by Meta FAIR (CC BY-NC 4.0).</li>
        </ul>
      </div>
    </>
  );
}
