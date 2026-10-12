export interface SourceCitation {
  id: string;
  title: string;
  guest?: string;
  timestamp?: string;
  speaker?: string;
  url?: string;
  quote: string;
  score?: number;
}

export interface Artifact {
  id: string;
  session_id: string;
  title: string;
  artifact_type: 'markdown' | 'html' | 'ship30_essay';
  content: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources: SourceCitation[];
  artifact_id?: string;
  execution_metadata?: Record<string, any>;
  created_at: string;
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
  messages?: Message[];
}

export interface SessionListItem {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  available: boolean;
  is_default: boolean;
  details?: string;
}

export interface ModelListResponse {
  active_provider: string;
  active_model: string;
  models: ModelInfo[];
}
