import React from 'react';
import { Plus, MessageSquare, Trash2, Library } from 'lucide-react';
import type { SessionListItem } from '../../types';

interface SessionSidebarProps {
  sessions: SessionListItem[];
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string, e: React.MouseEvent) => void;
}

export const SessionSidebar: React.FC<SessionSidebarProps> = ({
  sessions,
  currentSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
}) => {
  return (
    <div className="flex flex-col flex-1 min-h-0 w-72 bg-[#F7F3EB]">
      {/* Brand Masthead */}
      <div className="p-4 border-b border-neutral-200">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-6 h-6 rounded bg-[#E05338] flex items-center justify-center text-white font-bold text-xs">
            L
          </div>
          <span className="font-serif-editorial font-bold text-base tracking-tight text-[#1B1E1B]">
            The Lenny Assistant
          </span>
        </div>
        <p className="text-[11px] text-neutral-500">
          Editorial PM & Growth Research Studio
        </p>

        <button
          onClick={onNewSession}
          className="mt-3 w-full flex items-center justify-center gap-2 bg-[#E05338] hover:bg-[#C63D23] text-white py-2 px-3 rounded-lg text-xs font-semibold shadow-sm transition-all cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5" />
          New Research Session
        </button>
      </div>

      {/* Session History List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        <div className="px-2 py-1 text-[11px] font-semibold text-neutral-500 uppercase tracking-wider flex items-center gap-1.5">
          <Library className="w-3 h-3" />
          <span>Research Sessions</span>
        </div>

        {sessions.map((s) => {
          const isActive = s.id === currentSessionId;
          return (
            <div
              key={s.id}
              onClick={() => onSelectSession(s.id)}
              className={`group flex items-center justify-between p-2 rounded-lg text-xs cursor-pointer transition-colors ${
                isActive
                  ? 'bg-white text-neutral-900 shadow-sm border border-neutral-200 font-medium'
                  : 'text-neutral-600 hover:bg-neutral-200/50'
              }`}
            >
              <div className="flex items-center gap-2 truncate">
                <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-[#E05338]' : 'text-neutral-400'}`} />
                <span className="truncate">{s.title}</span>
              </div>

              <button
                onClick={(e) => onDeleteSession(s.id, e)}
                className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-600 text-neutral-400 transition-opacity"
                title="Delete Session"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          );
        })}

        {sessions.length === 0 && (
          <div className="p-4 text-center text-xs text-neutral-400 italic">
            No research sessions yet.
          </div>
        )}
      </div>
    </div>
  );
};
