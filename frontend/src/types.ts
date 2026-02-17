export type DebateRequest = {
  topic: string;
  persona_a: string;
  persona_b: string;
  turns: number;
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
