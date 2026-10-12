import React, { useState, useEffect } from 'react';
import { api } from './lib/api';
import type { Session, SessionListItem, Artifact, ModelListResponse } from './types';
import { SessionSidebar } from './features/sessions/SessionSidebar';
import { ModelSelector } from './features/models/ModelSelector';
import { MessageList } from './features/chat/MessageList';
import { ChatComposer } from './features/chat/ChatComposer';
import { ArtifactViewer } from './features/artifacts/ArtifactViewer';

export function App() {
  const [sessions, setSessions] = useState<SessionListItem[]>([]);
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [modelsData, setModelsData] = useState<ModelListResponse | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string>('ollama');
  const [selectedModel, setSelectedModel] = useState<string>('llama3.2');
  const [loading, setLoading] = useState<boolean>(false);
  const [modelsLoading, setModelsLoading] = useState<boolean>(false);

  // Load Initial Sessions & Models
  useEffect(() => {
    loadSessions();
    loadModels();
  }, []);

  const loadSessions = async () => {
    try {
      const list = await api.listSessions();
      setSessions(list);
      if (list.length > 0 && !currentSessionId) {
        selectSession(list[0].id);
      } else if (list.length === 0) {
        handleNewSession();
      }
    } catch (e) {
      console.error('Failed to load sessions:', e);
    }
  };

  const loadModels = async () => {
    setModelsLoading(true);
    try {
      const data = await api.listModels();
      setModelsData(data);
      setSelectedProvider(data.active_provider);
      setSelectedModel(data.active_model);
    } catch (e) {
      console.error('Failed to load models:', e);
    } finally {
      setModelsLoading(false);
    }
  };

  const selectSession = async (id: string) => {
    setCurrentSessionId(id);
    try {
      const s = await api.getSession(id);
      setCurrentSession(s);
      // Check if session has artifacts
      const arts = await api.listSessionArtifacts(id);
      if (arts.length > 0) {
        setActiveArtifact(arts[0]);
      } else {
        setActiveArtifact(null);
      }
    } catch (e) {
      console.error('Failed to load session details:', e);
    }
  };

  const handleNewSession = async () => {
    try {
      const s = await api.createSession('New Editorial Session');
      setSessions((prev) => [
        { id: s.id, title: s.title, created_at: s.created_at, updated_at: s.updated_at, message_count: 0 },
        ...prev,
      ]);
      setCurrentSessionId(s.id);
      setCurrentSession(s);
      setActiveArtifact(null);
    } catch (e) {
      console.error('Failed to create new session:', e);
    }
  };

  const handleDeleteSession = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteSession(id);
      const remaining = sessions.filter((s) => s.id !== id);
      setSessions(remaining);
      if (currentSessionId === id) {
        if (remaining.length > 0) {
          selectSession(remaining[0].id);
        } else {
          handleNewSession();
        }
      }
    } catch (e) {
      console.error('Failed to delete session:', e);
    }
  };

  const handleSendMessage = async (message: string, workflow: string) => {
    if (!currentSessionId) return;
    setLoading(true);

    // Optimistically append user message to UI
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      session_id: currentSessionId,
      role: 'user' as const,
      content: message,
      sources: [],
      created_at: new Date().toISOString(),
    };

    setCurrentSession((prev) =>
      prev ? { ...prev, messages: [...(prev.messages || []), tempUserMsg] } : null
    );

    try {
      const response = await api.sendChat({
        sessionId: currentSessionId,
        message,
        provider: selectedProvider,
        model: selectedModel,
        workflow,
      });

      // Reload fresh session state
      await selectSession(currentSessionId);
      await loadSessions();

      if (response.artifact) {
        setActiveArtifact(response.artifact);
      }
    } catch (e) {
      console.error('Error sending message:', e);
      // Append error message to thread
      const errorMsg = {
        id: `err-${Date.now()}`,
        session_id: currentSessionId,
        role: 'assistant' as const,
        content: `Error: Unable to process request. ${e instanceof Error ? e.message : 'Please try again.'}`,
        sources: [],
        created_at: new Date().toISOString(),
      };
      setCurrentSession((prev) =>
        prev ? { ...prev, messages: [...(prev.messages || []), errorMsg] } : null
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#F7F3EB]">
      {/* Sidebar: Navigation & Model Status */}
      <div className="flex flex-col h-full w-72 shrink-0 border-r border-neutral-300 bg-[#F7F3EB] overflow-hidden">
        <SessionSidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={selectSession}
          onNewSession={handleNewSession}
          onDeleteSession={handleDeleteSession}
        />
        <div className="shrink-0">
          <ModelSelector
            modelsData={modelsData}
            selectedProvider={selectedProvider}
            selectedModel={selectedModel}
            onSelect={(prov, mod) => {
              setSelectedProvider(prov);
              setSelectedModel(mod);
            }}
            onRefresh={loadModels}
            loading={modelsLoading}
          />
        </div>
      </div>

      {/* Main Research Workspace */}
      <div className="flex flex-1 h-full overflow-hidden">
        {/* Chat Studio */}
        <div className="flex flex-col flex-1 h-full min-w-0 bg-[#FDFAF5]">
          <div className="px-6 py-3 border-b border-neutral-200 bg-[#F7F3EB] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">
                Active Session:
              </span>
              <span className="text-sm font-semibold text-[#1B1E1B] truncate max-w-lg font-serif-editorial">
                {currentSession?.title || 'Editorial Session'}
              </span>
            </div>

            {activeArtifact && (
              <button
                onClick={() => setActiveArtifact(null)}
                className="text-xs px-2.5 py-1 bg-white border border-neutral-300 rounded-lg text-neutral-700 hover:bg-neutral-100 transition-colors"
              >
                Toggle Workspace
              </button>
            )}
          </div>

          <MessageList
            messages={currentSession?.messages || []}
            loading={loading}
            onOpenArtifact={(art) => setActiveArtifact(art)}
            onSelectPrompt={(prompt, wf) => handleSendMessage(prompt, wf || 'auto')}
          />

          <ChatComposer onSendMessage={handleSendMessage} loading={loading} />
        </div>

        {/* Sandboxed Artifact Viewer Side Panel */}
        {activeArtifact && (
          <ArtifactViewer
            artifact={activeArtifact}
            onClose={() => setActiveArtifact(null)}
          />
        )}
      </div>
    </div>
  );
}

export default App;
