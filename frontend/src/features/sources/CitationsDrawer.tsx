import React, { useState } from 'react';
import { ChevronDown, ChevronUp, BookOpen, ExternalLink } from 'lucide-react';
import type { SourceCitation } from '../../types';

interface CitationsDrawerProps {
  citations: SourceCitation[];
}

export const CitationsDrawer: React.FC<CitationsDrawerProps> = ({ citations }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-neutral-200">
      <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-neutral-600 uppercase tracking-wider">
        <BookOpen className="w-3.5 h-3.5 text-[#E05338]" />
        <span>Grounded Transcript Sources ({citations.length})</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {citations.map((c) => {
          const isExpanded = expandedId === c.id;
          return (
            <div
              key={c.id}
              className="bg-[#F7F3EB] border border-neutral-300 rounded-lg text-xs overflow-hidden transition-all shadow-sm"
            >
              <button
                onClick={() => setExpandedId(isExpanded ? null : c.id)}
                className="flex items-center gap-2 px-3 py-1.5 hover:bg-neutral-200/50 transition-colors text-left"
              >
                <span className="font-semibold text-neutral-800">
                  {c.title}
                </span>
                {c.timestamp && (
                  <span className="font-mono text-[10px] bg-neutral-200 text-neutral-700 px-1.5 py-0.5 rounded">
                    {c.timestamp}
                  </span>
                )}
                {isExpanded ? (
                  <ChevronUp className="w-3 h-3 text-neutral-500" />
                ) : (
                  <ChevronDown className="w-3 h-3 text-neutral-500" />
                )}
              </button>

              {isExpanded && (
                <div className="p-3 bg-white border-t border-neutral-200 max-w-lg">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[11px] font-medium text-[#E05338]">
                      Speaker: {c.speaker || c.guest || 'Interview'}
                    </span>
                    {c.url && (
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-1 text-[11px] text-neutral-500 hover:text-neutral-900"
                      >
                        Source <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                  <blockquote className="text-xs text-neutral-700 italic border-l-2 border-[#E05338] pl-2.5 my-1 font-serif-editorial">
                    "{c.quote}"
                  </blockquote>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
