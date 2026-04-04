'use client';

import { useState, useRef, useCallback } from 'react';

const SPACE_URL = 'https://beta3-tribe-v2-neural-activity-predictor.hf.space';
// run_prediction is fn_index 2 (0=toggle_inputs, 1=download_sample, 2=run_prediction)
const FN_INDEX = 2;

type Modality = 'Video' | 'Audio' | 'Text';

interface PredictResult {
  brain3d: string;
  timelineUrl: string;
  status: string;
}

// ── Raw Gradio queue API (bypasses @gradio/client schema validation) ───────────
function randomHash(len = 10) {
  return Math.random().toString(36).slice(2, 2 + len);
}

async function gradioPredict(
  args: unknown[],
  onStatus: (msg: string) => void,
): Promise<unknown[]> {
  const sessionHash = randomHash();

  // 1. Join the queue
  const joinRes = await fetch(`${SPACE_URL}/queue/join`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      data: args,
      fn_index: FN_INDEX,
      session_hash: sessionHash,
      event_data: null,
      trigger_id: null,
    }),
  });
  if (!joinRes.ok) {
    const text = await joinRes.text();
    throw new Error(`Queue join failed (${joinRes.status}): ${text}`);
  }

  // 2. Stream SSE events from /queue/data
  return new Promise((resolve, reject) => {
    const url = `${SPACE_URL}/queue/data?session_hash=${sessionHash}`;
    const src = new EventSource(url);

    const timeout = setTimeout(() => {
      src.close();
      reject(new Error('Timed out waiting for result (10 min)'));
    }, 10 * 60 * 1000);

    src.onmessage = (ev) => {
      let msg: Record<string, unknown>;
      try { msg = JSON.parse(ev.data); } catch { return; }

      const stage = msg.msg as string;
      console.log('[TRIBE] queue event:', stage, msg);

      if (stage === 'estimation') {
        const rank = msg.rank as number ?? '?';
        onStatus(`Queued (position ${rank})… first run may take 2–4 min`);
      } else if (stage === 'process_starts') {
        onStatus('Processing on GPU…');
      } else if (stage === 'process_generating') {
        onStatus('Generating output…');
      } else if (stage === 'process_completed') {
        clearTimeout(timeout);
        src.close();
        const out = msg.output as { data?: unknown[]; error?: string };
        if (msg.success && out?.data) {
          resolve(out.data);
        } else {
          reject(new Error(out?.error ?? JSON.stringify(msg)));
        }
      } else if (stage === 'error') {
        clearTimeout(timeout);
        src.close();
        const title = msg.title as string ?? 'Error';
        const message = msg.message as string ?? JSON.stringify(msg);
        reject(new Error(`${title}: ${message}`));
      }
    };

    src.onerror = () => {
      clearTimeout(timeout);
      src.close();
      reject(new Error('SSE connection dropped'));
    };
  });
}

// ── Component ─────────────────────────────────────────────────────────────────
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
      const textArg = modality === 'Text' ? text.trim() : '';
      // File args: for video/audio we pass null for now (text is primary)
      const args = [modality, null, null, textArg, nTimesteps, vmin, false];

      const data = await gradioPredict(args, setProgress) as [string, unknown, string];

      const brain3dHtml = data[0] as string;
      const timelineRaw = data[1];
      const statusStr   = data[2] as string;

      let timelineUrl = '';
      if (timelineRaw) {
        if (typeof timelineRaw === 'string') {
          timelineUrl = timelineRaw;
        } else if (typeof timelineRaw === 'object' && timelineRaw !== null) {
          const obj = timelineRaw as Record<string, unknown>;
          timelineUrl = (obj.url ?? obj.path ?? '') as string;
          if (timelineUrl && !timelineUrl.startsWith('http')) {
            timelineUrl = `${SPACE_URL}/file=${timelineUrl}`;
          }
        }
      }

      setResult({ brain3d: brain3dHtml, timelineUrl, status: statusStr });
      setProgress('');
    } catch (e: unknown) {
      console.error('[TRIBE]', e);
      setError(e instanceof Error ? e.message : JSON.stringify(e));
      setProgress('');
    } finally {
      setLoading(false);
    }
  }, [loading, modality, text, nTimesteps, vmin]);

  // Inject the brain HTML string (already an <iframe srcdoc="..."> element)
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
        <strong>Note</strong>&nbsp; Calls the HuggingFace ZeroGPU Space directly.
        First run takes <strong>2–4 minutes</strong> (model + WhisperX download).
        Text is the fastest modality.
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
                <div style={{fontSize:'0.72rem',color:'var(--dim)',marginTop:6}}>
                  Video upload coming soon — use Text or Audio for now.
                </div>
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
                <div style={{fontSize:'0.72rem',color:'var(--dim)',marginTop:6}}>
                  Audio upload coming soon — use Text for now.
                </div>
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
          <li>Text input requires the gated <strong style={{color:'var(--dim)'}}>LLaMA 3.2-3B</strong> model — if text fails, the Space may need a HF_TOKEN env var set.</li>
          <li>The 3D view is interactive: drag to rotate, scroll to zoom, use the time slider to navigate seconds.</li>
          <li>Output is predicted fMRI BOLD on fsaverage5 mesh — 20,484 cortical vertices at 1 s resolution.</li>
          <li>This is an unofficial frontend. Model weights and official demo by Meta FAIR (CC BY-NC 4.0).</li>
        </ul>
      </div>
    </>
  );
}
