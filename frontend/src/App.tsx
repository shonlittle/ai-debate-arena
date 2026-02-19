import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import type { DebateRequest, DebateResponse, DebateTurn, Voice, VoicesResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function toDataUrl(turn: DebateTurn): string {
  return `data:audio/${turn.audio_format};base64,${turn.audio_base64}`;
}

function toDisplayName(voiceName: string): string {
  return voiceName.split(' - ')[0].trim();
}

export default function App() {
  const [topic, setTopic] = useState('Will AI improve education outcomes in the next decade?');
  const [turnCount, setTurnCount] = useState(6);
  const [humorMode, setHumorMode] = useState(false);

  const [voices, setVoices] = useState<Voice[]>([]);
  const [personaAVoiceId, setPersonaAVoiceId] = useState('');
  const [personaBVoiceId, setPersonaBVoiceId] = useState('');
  const [voicesLoading, setVoicesLoading] = useState(true);

  const [loading, setLoading] = useState(false);
  const [loadingSeconds, setLoadingSeconds] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [debate, setDebate] = useState<DebateResponse | null>(null);

  const [currentTurn, setCurrentTurn] = useState<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        setVoicesLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/voices`);
        if (!response.ok) {
          throw new Error(`Voices request failed with ${response.status}`);
        }

        const data = (await response.json()) as VoicesResponse;
        const loadedVoices = data.voices ?? [];
        setVoices(loadedVoices);

        if (loadedVoices.length >= 2) {
          setPersonaAVoiceId(loadedVoices[0].voice_id);
          setPersonaBVoiceId(loadedVoices[1].voice_id);
        } else if (loadedVoices.length === 1) {
          setPersonaAVoiceId(loadedVoices[0].voice_id);
          setPersonaBVoiceId(loadedVoices[0].voice_id);
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        setError(`Unable to load voices: ${message}`);
      } finally {
        setVoicesLoading(false);
      }
    })();
  }, []);

  const personaAName = useMemo(
    () => voices.find((v) => v.voice_id === personaAVoiceId)?.name ?? 'Persona A',
    [voices, personaAVoiceId],
  );

  const personaBName = useMemo(
    () => voices.find((v) => v.voice_id === personaBVoiceId)?.name ?? 'Persona B',
    [voices, personaBVoiceId],
  );

  const canGenerate =
    topic.trim().length > 2 &&
    !voicesLoading &&
    voices.length > 0 &&
    personaAVoiceId.length > 0 &&
    personaBVoiceId.length > 0 &&
    personaAVoiceId !== personaBVoiceId;

  const currentSubtitle = useMemo(() => {
    if (!debate || currentTurn === null) {
      return 'Press Play to start debate narration.';
    }
    return debate.turns[currentTurn]?.text ?? '';
  }, [debate, currentTurn]);

  const loadingStatus = useMemo(() => {
    if (!loading) {
      return '';
    }
    if (loadingSeconds < 3) {
      return 'Generating debate script...';
    }
    if (loadingSeconds < 9) {
      return 'Synthesizing voice audio...';
    }
    return 'Finalizing response payload...';
  }, [loading, loadingSeconds]);

  useEffect(() => {
    if (!loading) {
      setLoadingSeconds(0);
      return;
    }

    const timerId = window.setInterval(() => {
      setLoadingSeconds((prev) => prev + 1);
    }, 1000);

    return () => {
      window.clearInterval(timerId);
    };
  }, [loading]);

  async function generateDebate(event: FormEvent) {
    event.preventDefault();
    if (!canGenerate) {
      setError('Enter a valid topic and choose two different voices.');
      return;
    }

    setLoading(true);
    setError(null);
    setDebate(null);
    setCurrentTurn(null);
    stopPlayback();

    const payload: DebateRequest = {
      topic: topic.trim(),
      persona_a: personaAName,
      persona_b: personaBName,
      turns: turnCount,
      humor_mode: humorMode,
      persona_a_voice_id: personaAVoiceId,
      persona_b_voice_id: personaBVoiceId,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/debate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`${response.status}: ${errorText}`);
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
        <p className="muted">Generate a scripted audio debate between two ElevenLabs voices.</p>

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
            Persona A Voice
            <select value={personaAVoiceId} onChange={(e) => setPersonaAVoiceId(e.target.value)}>
              {voices.map((voice) => (
                <option key={`a-${voice.voice_id}`} value={voice.voice_id}>
                  {voice.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Persona B Voice
            <select value={personaBVoiceId} onChange={(e) => setPersonaBVoiceId(e.target.value)}>
              {voices.map((voice) => (
                <option key={`b-${voice.voice_id}`} value={voice.voice_id}>
                  {voice.name}
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

          <label className="toggle-row">
            Humor Mode
            <input
              type="checkbox"
              checked={humorMode}
              onChange={(e) => setHumorMode(e.target.checked)}
            />
          </label>

          <button type="submit" disabled={loading || !canGenerate}>
            {loading ? 'Generating...' : 'Generate Debate'}
          </button>
        </form>

        {loading ? (
          <div className="progress-box">
            <p className="progress-title">{loadingStatus}</p>
            <div className="progress-bar" aria-hidden="true" />
            <p className="muted">Elapsed: {loadingSeconds}s</p>
          </div>
        ) : null}

        {voicesLoading ? <p className="muted">Loading voices...</p> : null}
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
          <p>{currentSubtitle}</p>
        </div>

        <div>
          <h3>Turns</h3>
          <ol className="turns">
            {(debate?.turns ?? []).map((turn, idx) => (
              <li key={`${idx}-${turn.speaker}`} className={idx === currentTurn ? 'active' : ''}>
                <strong>
                  {turn.speaker === 'persona_a'
                    ? toDisplayName(personaAName)
                    : toDisplayName(personaBName)}
                </strong>
                : {turn.text}
              </li>
            ))}
          </ol>
        </div>
      </section>
    </main>
  );
}
