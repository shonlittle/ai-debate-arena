export type DebateRequest = {
  topic: string;
  persona_a: string;
  persona_b: string;
  turns: number;
  humor_mode?: boolean;
  persona_a_voice_id?: string;
  persona_b_voice_id?: string;
};

export type DebateTurn = {
  speaker: 'persona_a' | 'persona_b';
  text: string;
  audio_format: 'mp3';
  audio_base64: string;
};

export type DebateResponse = {
  topic: string;
  turns: DebateTurn[];
};

export type Voice = {
  voice_id: string;
  name: string;
};

export type VoicesResponse = {
  voices: Voice[];
};
