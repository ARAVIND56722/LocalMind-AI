import React from 'react';
import { Cpu, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import type { ModelListResponse } from '../../types';

interface ModelSelectorProps {
  modelsData: ModelListResponse | null;
  selectedProvider: string;
  selectedModel?: string;
  onSelect: (provider: string, model: string) => void;
  onRefresh: () => void;
  loading: boolean;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  modelsData,
  selectedProvider,
  onSelect,
  onRefresh,
  loading,
}) => {
  return (
    <div className="p-3 bg-[#F7F3EB] border-t border-neutral-200">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-neutral-700">
          <Cpu className="w-3.5 h-3.5 text-[#E05338]" />
          <span>Active Provider & Model</span>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="text-neutral-500 hover:text-neutral-800 transition-colors"
          title="Refresh availability"
        >
          <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="space-y-1.5">
        {modelsData?.models.map((m) => {
          const isSelected = selectedProvider === m.provider;
          return (
            <button
              key={`${m.provider}-${m.id}`}
              onClick={() => onSelect(m.provider, m.id)}
              className={`w-full text-left p-2 rounded-lg border text-xs transition-all flex items-center justify-between ${
                isSelected
                  ? 'border-[#E05338] bg-white shadow-sm font-medium'
                  : 'border-neutral-200 hover:bg-neutral-200/60 bg-transparent text-neutral-600'
              }`}
            >
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-medium text-neutral-900">{m.name}</span>
                </div>
                <div className="text-[10px] text-neutral-500 truncate max-w-[190px]">
                  {m.details}
                </div>
              </div>

              <div>
                {m.available ? (
                  <span className="flex items-center gap-1 text-[10px] text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded font-mono">
                    <CheckCircle2 className="w-2.5 h-2.5" /> Ready
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-[10px] text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded font-mono">
                    <AlertCircle className="w-2.5 h-2.5" /> Offline
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
