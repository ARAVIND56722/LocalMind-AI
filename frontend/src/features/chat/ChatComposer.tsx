import React, { useState } from 'react';
import { Send, Sparkles, PenTool, Layout, Loader2 } from 'lucide-react';

interface ChatComposerProps {
  onSendMessage: (message: string, workflow: string) => void;
  loading: boolean;
}

export const ChatComposer: React.FC<ChatComposerProps> = ({ onSendMessage, loading }) => {
  const [input, setInput] = useState('');
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>('auto');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSendMessage(input.trim(), selectedWorkflow);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-neutral-300 bg-[#FDFAF5] p-4">
      {/* Workflow Mode Tabs */}
      <div className="flex items-center gap-2 mb-2 text-xs">
        <span className="text-neutral-500 font-medium">Mode:</span>
        <button
          type="button"
          onClick={() => setSelectedWorkflow('auto')}
          className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition-colors ${
            selectedWorkflow === 'auto'
              ? 'bg-neutral-800 text-white font-medium shadow-sm'
              : 'bg-neutral-200 text-neutral-600 hover:bg-neutral-300'
          }`}
        >
          <Sparkles className="w-3 h-3" />
          Auto Dispatch
        </button>
        <button
          type="button"
          onClick={() => setSelectedWorkflow('ship30')}
          className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition-colors ${
            selectedWorkflow === 'ship30'
              ? 'bg-[#E05338] text-white font-medium shadow-sm'
              : 'bg-neutral-200 text-neutral-600 hover:bg-neutral-300'
          }`}
        >
          <PenTool className="w-3 h-3" />
          Ship 30 for 30 Essay
        </button>
        <button
          type="button"
          onClick={() => setSelectedWorkflow('artifact')}
          className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition-colors ${
            selectedWorkflow === 'artifact'
              ? 'bg-emerald-700 text-white font-medium shadow-sm'
              : 'bg-neutral-200 text-neutral-600 hover:bg-neutral-300'
          }`}
        >
          <Layout className="w-3 h-3" />
          Artifact Generator
        </button>
      </div>

      {/* Input Textarea & Send Button */}
      <div className="relative flex items-end bg-white border border-neutral-300 focus-within:border-[#E05338] rounded-xl shadow-sm transition-all overflow-hidden p-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            selectedWorkflow === 'ship30'
              ? 'Enter an essay topic (e.g. "Elena Verna on why AI startups need new growth loops")...'
              : selectedWorkflow === 'artifact'
              ? 'Request a document or artifact (e.g. "Create a PRD checklist for an AI onboarding flow in HTML")...'
              : 'Ask a product management or growth question grounded in Lenny\'s transcripts...'
          }
          className="w-full resize-none outline-none text-sm text-neutral-900 placeholder:text-neutral-400 bg-transparent max-h-32 min-h-[48px] p-1 font-sans"
          rows={2}
          disabled={loading}
        />

        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="ml-2 mb-1 p-2 bg-[#E05338] hover:bg-[#C63D23] disabled:bg-neutral-300 text-white rounded-lg transition-colors shadow-sm cursor-pointer disabled:cursor-not-allowed shrink-0"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </div>
    </form>
  );
};
