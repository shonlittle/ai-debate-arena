export type DebateRequest = {
  topic: string;
  persona_a: string;
  persona_b: string;
  turns: number;
};

export type DebateTurn = {
  turn_index: number;
  speaker: 'persona_a' | 'persona_b';
  persona: string;
  text: string;
  audio_mime_type: string;
  audio_base64: string;
};

export type DebateResponse = {
  topic: string;
  turns: DebateTurn[];
};
