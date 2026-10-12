import React from 'react';
import { User, Sparkles, ChevronRight } from 'lucide-react';
import type { Message, Artifact } from '../../types';
import { CitationsDrawer } from '../sources/CitationsDrawer';

interface MessageListProps {
  messages: Message[];
  loading: boolean;
  onOpenArtifact?: (artifact: Artifact) => void;
  onSelectPrompt: (prompt: string, workflow?: string) => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  loading,
  onSelectPrompt,
}) => {
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 max-w-2xl mx-auto text-center">
        <div className="w-12 h-12 rounded-2xl bg-[#FCECE9] text-[#E05338] flex items-center justify-center mb-4 shadow-sm">
          <Sparkles className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold font-serif-editorial text-[#1B1E1B] mb-2">
          The Lenny Growth Assistant
        </h1>
        <p className="text-sm text-neutral-600 mb-8 max-w-md">
          A dedicated editorial research partner grounded in Lenny Rachitsky’s podcast & newsletter archive.
        </p>

        <div className="w-full text-left space-y-2">
          <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider block px-1">
            Curated Research Starters
          </span>

          <button
            onClick={() => onSelectPrompt("What is Elena Verna's advice on growth loops and why AI companies must reinvent solutions rather than optimize?", "qa")}
            className="w-full text-left p-3 rounded-xl bg-white border border-neutral-200 hover:border-[#E05338] shadow-card transition-all flex items-center justify-between group"
          >
            <div>
              <div className="text-xs font-semibold text-neutral-900 group-hover:text-[#E05338]">
                Elena Verna on AI Growth Loops & PMF
              </div>
              <div className="text-[11px] text-neutral-500">
                Explore the 95/5 innovation ratio and why traditional funnels fail.
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-neutral-400 group-hover:text-[#E05338]" />
          </button>

          <button
            onClick={() => onSelectPrompt("The 95% Innovation Rule: Why High-Velocity AI Startups Break Traditional SaaS Growth", "ship30")}
            className="w-full text-left p-3 rounded-xl bg-white border border-neutral-200 hover:border-[#E05338] shadow-card transition-all flex items-center justify-between group"
          >
            <div>
              <div className="text-xs font-semibold text-neutral-900 group-hover:text-[#E05338]">
                Draft a 1,250-word Ship 30 for 30 Essay
              </div>
              <div className="text-[11px] text-neutral-500">
                Generate an atomic, high-impact digital essay using transcript evidence.
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-neutral-400 group-hover:text-[#E05338]" />
          </button>

          <button
            onClick={() => onSelectPrompt("Create a comprehensive, responsive Product-Led Sales readiness scorecard HTML artifact with interactive metric cards", "artifact")}
            className="w-full text-left p-3 rounded-xl bg-white border border-neutral-200 hover:border-[#E05338] shadow-card transition-all flex items-center justify-between group"
          >
            <div>
              <div className="text-xs font-semibold text-neutral-900 group-hover:text-[#E05338]">
                Generate an Interactive HTML Artifact
              </div>
              <div className="text-[11px] text-neutral-500">
                Render an isolated, sandboxed product artifact in the workspace.
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-neutral-400 group-hover:text-[#E05338]" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 max-w-4xl w-full mx-auto">
      {messages.map((m) => {
        const isUser = m.role === 'user';
        return (
          <div
            key={m.id}
            className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}
          >
            {!isUser && (
              <div className="w-8 h-8 rounded-full bg-[#E05338] text-white flex items-center justify-center shrink-0 text-xs font-bold shadow-sm">
                L
              </div>
            )}

            <div
              className={`max-w-2xl rounded-2xl p-5 ${
                isUser
                  ? 'bg-white border border-neutral-300 text-neutral-900 shadow-sm'
                  : 'bg-white border border-neutral-200 text-neutral-900 shadow-card'
              }`}
            >
              {/* Content */}
              <div className="prose prose-neutral max-w-none text-sm font-sans leading-relaxed whitespace-pre-wrap">
                {m.content}
              </div>

              {/* Citations if assistant */}
              {!isUser && m.sources && m.sources.length > 0 && (
                <CitationsDrawer citations={m.sources} />
              )}
            </div>

            {isUser && (
              <div className="w-8 h-8 rounded-full bg-neutral-800 text-white flex items-center justify-center shrink-0 text-xs shadow-sm">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        );
      })}

      {loading && (
        <div className="flex gap-4 items-center text-xs text-neutral-500 italic pl-12">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-[#E05338] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-[#E05338] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-[#E05338] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span>Retrieving Lenny's transcripts and synthesizing grounded response...</span>
        </div>
      )}
    </div>
  );
};
