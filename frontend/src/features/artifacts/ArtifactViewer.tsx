import React, { useState } from 'react';
import { X, Code, Eye, Copy, Check, ShieldCheck, FileText } from 'lucide-react';
import type { Artifact } from '../../types';

interface ArtifactViewerProps {
  artifact: Artifact | null;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({ artifact, onClose }) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'source'>('preview');
  const [copied, setCopied] = useState(false);

  if (!artifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const wordCount = artifact.content.trim().split(/\s+/).length;

  return (
    <div className="flex flex-col h-full bg-[#FDFAF5] border-l border-neutral-300 w-full max-w-2xl shadow-xl z-20">
      {/* Header Bar */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-200 bg-[#F7F3EB]">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-[#FCECE9] rounded-lg text-[#E05338]">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-neutral-200 text-neutral-700">
                {artifact.artifact_type}
              </span>
              <span className="text-xs text-neutral-500 font-mono">
                {wordCount} words
              </span>
            </div>
            <h2 className="text-base font-semibold text-[#1B1E1B] truncate max-w-md font-serif-editorial">
              {artifact.title}
            </h2>
          </div>
        </div>

        {/* Tab Controls & Actions */}
        <div className="flex items-center gap-2">
          <div className="flex bg-neutral-200 p-0.5 rounded-lg text-xs font-medium">
            <button
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
                activeTab === 'preview'
                  ? 'bg-white text-neutral-900 shadow-sm font-semibold'
                  : 'text-neutral-600 hover:text-neutral-900'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              Preview
            </button>
            <button
              onClick={() => setActiveTab('source')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
                activeTab === 'source'
                  ? 'bg-white text-neutral-900 shadow-sm font-semibold'
                  : 'text-neutral-600 hover:text-neutral-900'
              }`}
            >
              <Code className="w-3.5 h-3.5" />
              Source
            </button>
          </div>

          <button
            onClick={handleCopy}
            title="Copy Source"
            className="p-2 hover:bg-neutral-200 rounded-lg text-neutral-600 transition-colors"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
          </button>

          <button
            onClick={onClose}
            title="Close Workspace"
            className="p-2 hover:bg-neutral-200 rounded-lg text-neutral-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Security Isolation Banner for HTML */}
      {artifact.artifact_type === 'html' && (
        <div className="bg-[#F4F8E5] border-b border-[#E1EDBD] px-6 py-2 flex items-center justify-between text-xs text-neutral-700">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#7C9A20]" />
            <span>Sandboxed View: Restrictive CSP applied. Arbitrary scripts and parent DOM access are blocked.</span>
          </div>
        </div>
      )}

      {/* Workspace Content Body */}
      <div className="flex-1 overflow-auto p-6">
        {activeTab === 'preview' ? (
          artifact.artifact_type === 'html' ? (
            <div className="w-full h-full bg-white rounded-xl shadow-card border border-neutral-200 overflow-hidden">
              <iframe
                title={artifact.title}
                srcDoc={artifact.content}
                sandbox="allow-same-origin"
                className="w-full h-full border-none"
              />
            </div>
          ) : (
            <div className="prose prose-neutral max-w-none bg-white p-8 rounded-xl shadow-card border border-neutral-200">
              <div className="whitespace-pre-wrap font-serif-editorial text-[#1B1E1B] leading-relaxed text-sm">
                {artifact.content}
              </div>
            </div>
          )
        ) : (
          <div className="h-full bg-neutral-900 text-neutral-100 p-4 rounded-xl font-mono text-xs overflow-auto">
            <pre className="whitespace-pre-wrap">{artifact.content}</pre>
          </div>
        )}
      </div>
    </div>
  );
};
