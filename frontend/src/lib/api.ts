import type { Session, SessionListItem, Artifact, ModelListResponse } from '../types';

const API_BASE = '/api';

export const api = {
  // Health
  async getHealth(): Promise<{ status: string; service: string; version: string }> {
    const res = await fetch('/health');
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async getHealthReady(): Promise<{ ready: boolean; database: string; retrieval_engine: string; ollama_local: string }> {
    const res = await fetch('/health/ready');
    return res.json();
  },

  // Sessions
  async listSessions(): Promise<SessionListItem[]> {
    const res = await fetch(`${API_BASE}/sessions`);
    if (!res.ok) throw new Error('Failed to load sessions');
    return res.json();
  },

  async createSession(title: string = 'New Research Session'): Promise<Session> {
    const res = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
  },

  async getSession(sessionId: string): Promise<Session> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
    if (!res.ok) throw new Error('Failed to get session');
    return res.json();
  },

  async deleteSession(sessionId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete session');
  },

  // Chat
  async sendChat(params: {
    sessionId: string;
    message: string;
    provider?: string;
    model?: string;
    workflow?: string;
  }): Promise<{
    session_id: string;
    message_id: string;
    role: string;
    content: string;
    sources: any[];
    artifact?: Artifact;
    execution_metadata: Record<string, any>;
  }> {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: params.sessionId,
        message: params.message,
        provider: params.provider,
        model: params.model,
        workflow: params.workflow || 'auto',
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Chat request failed' }));
      throw new Error(err.detail || 'Chat request failed');
    }
    return res.json();
  },

  // Ship 30 Skill
  async generateShip30(params: {
    sessionId: string;
    topic: string;
    instructions?: string;
    targetWordCount?: number;
    provider?: string;
    model?: string;
  }): Promise<{
    artifact_id: string;
    title: string;
    content: string;
    sources: any[];
    metadata: Record<string, any>;
  }> {
    const res = await fetch(`${API_BASE}/skills/ship30`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: params.sessionId,
        topic: params.topic,
        instructions: params.instructions,
        target_word_count: params.targetWordCount || 1250,
        provider: params.provider,
        model: params.model,
      }),
    });
    if (!res.ok) throw new Error('Ship 30 essay generation failed');
    return res.json();
  },

  // Artifacts
  async getArtifact(artifactId: string): Promise<Artifact> {
    const res = await fetch(`${API_BASE}/artifacts/${artifactId}`);
    if (!res.ok) throw new Error('Failed to load artifact');
    return res.json();
  },

  async listSessionArtifacts(sessionId: string): Promise<Artifact[]> {
    const res = await fetch(`${API_BASE}/artifacts/session/${sessionId}`);
    if (!res.ok) throw new Error('Failed to load session artifacts');
    return res.json();
  },

  // Models
  async listModels(): Promise<ModelListResponse> {
    const res = await fetch(`${API_BASE}/models`);
    if (!res.ok) throw new Error('Failed to fetch models');
    return res.json();
  },
};
