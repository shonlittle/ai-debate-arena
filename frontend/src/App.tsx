import { FormEvent, useMemo, useRef, useState } from 'react';
import type { DebateRequest, DebateResponse, DebateTurn } from './types';

const PERSONAS = ['Scientist', 'Philosopher', 'Economist', 'Historian', 'Optimist'];

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function toDataUrl(turn: DebateTurn): string {
  return `data:${turn.audio_mime_type};base64,${turn.audio_base64}`;
}

export default function App() {
  const [topic, setTopic] = useState('Will AI improve education outcomes in the next decade?');
  const [personaA, setPersonaA] = useState(PERSONAS[0]);
  const [personaB, setPersonaB] = useState(PERSONAS[2]);
  const [turnCount, setTurnCount] = useState(6);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debate, setDebate] = useState<DebateResponse | null>(null);

  const [currentTurn, setCurrentTurn] = useState<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const canGenerate = topic.trim().length > 2 && personaA !== personaB;

  const currentSubtitle = useMemo(() => {
    if (!debate || currentTurn === null) {
      return 'Press Play to start debate narration.';
    }
    return debate.turns[currentTurn]?.text ?? '';
  }, [debate, currentTurn]);

  async function generateDebate(event: FormEvent) {
    event.preventDefault();
    if (!canGenerate) {
      setError('Enter a valid topic and choose two different personas.');
      return;
    }

    setLoading(true);
    setError(null);
    setDebate(null);
    setCurrentTurn(null);
    stopPlayback();

    const payload: DebateRequest = {
      topic: topic.trim(),
      persona_a: personaA,
      persona_b: personaB,
      turns: turnCount,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/debate/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Request failed with ${response.status}`);
      }

      const data = (await response.json()) as DebateResponse;
      setDebate(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(`Unable to generate debate: ${message}`);
    } finally {
      setLoading(false);
    }
  }

  function stopPlayback() {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.src = '';
    }
  }

  function playFrom(index: number) {
    if (!debate || index >= debate.turns.length) {
      setCurrentTurn(null);
      stopPlayback();
      return;
    }

    const turn = debate.turns[index];
    if (!audioRef.current) {
      audioRef.current = new Audio();
    }

    audioRef.current.src = toDataUrl(turn);
    audioRef.current.onended = () => {
      playFrom(index + 1);
    };

    setCurrentTurn(index);
    void audioRef.current.play();
  }

  return (
    <main className="app-shell">
      <section className="panel">
        <h1>AI Debate Arena</h1>
        <p className="muted">Generate a scripted audio debate between two personas.</p>

        <form onSubmit={generateDebate} className="controls">
          <label>
            Topic
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter debate topic"
            />
          </label>

          <label>
            Persona A
            <select value={personaA} onChange={(e) => setPersonaA(e.target.value)}>
              {PERSONAS.map((persona) => (
                <option key={`a-${persona}`} value={persona}>
                  {persona}
                </option>
              ))}
            </select>
          </label>

          <label>
            Persona B
            <select value={personaB} onChange={(e) => setPersonaB(e.target.value)}>
              {PERSONAS.map((persona) => (
                <option key={`b-${persona}`} value={persona}>
                  {persona}
                </option>
              ))}
            </select>
          </label>

          <label>
            Debate Length (turns)
            <input
              type="number"
              min={2}
              max={20}
              step={1}
              value={turnCount}
              onChange={(e) => setTurnCount(Number(e.target.value))}
            />
          </label>

          <button type="submit" disabled={loading || !canGenerate}>
            {loading ? 'Generating...' : 'Generate Debate'}
          </button>
        </form>

        {error ? <p className="error">{error}</p> : null}
      </section>

      <section className="panel">
        <h2>Playback</h2>

        <div className="actions">
          <button onClick={() => playFrom(0)} disabled={!debate || loading}>
            Play
          </button>
          <button
            onClick={() => {
              setCurrentTurn(null);
              stopPlayback();
            }}
            disabled={!debate}
          >
            Stop
          </button>
        </div>

        <div className="subtitle-box">
          <h3>Subtitle</h3>
          <p>{currentSubtitle}</p>
        </div>

        <div>
          <h3>Turns</h3>
          <ol className="turns">
            {(debate?.turns ?? []).map((turn, idx) => (
              <li key={`${turn.turn_index}-${turn.persona}`} className={idx === currentTurn ? 'active' : ''}>
                <strong>{turn.persona}</strong>: {turn.text}
              </li>
            ))}
          </ol>
        </div>
      </section>
    </main>
  );
}
