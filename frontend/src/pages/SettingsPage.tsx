import React from 'react';
import { Sliders, Shield, Database, Cpu, CheckCircle } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const configs = [
    {
      group: 'LLM & Orchestration (Groq + LangGraph)',
      icon: Cpu,
      items: [
        { key: 'GROQ_MODEL', value: 'llama-3.3-70b-versatile', source: '.env' },
        { key: 'AI_ORCHESTRATION', value: 'LangGraph StateGraph', source: 'Internal' },
      ],
    },
    {
      group: 'Vector Store & Embeddings',
      icon: Database,
      items: [
        { key: 'EMBEDDING_MODEL', value: 'all-MiniLM-L6-v2', source: '.env' },
        { key: 'VECTOR_DB', value: 'ChromaDB (Local Persistence)', source: 'Internal' },
        { key: 'CHROMA_PERSIST_DIR', value: 'data/chroma', source: '.env' },
      ],
    },
    {
      group: 'Network & Security',
      icon: Shield,
      items: [
        { key: 'CORS_POLICY', value: 'Explicit Allowlist Only', source: 'Config' },
        { key: 'ALLOWED_ORIGINS', value: 'http://localhost:5173, http://127.0.0.1:5173', source: '.env' },
        { key: 'CENTRALIZED_ERROR_HANDLING', value: 'Enabled (JSON Envelopes)', source: 'FastAPI' },
      ],
    },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between border-b border-dev-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-sky-400" />
            <span>Application Settings & Environment</span>
          </h1>
          <p className="text-xs text-dev-muted font-mono mt-0.5">
            Phase 1 configuration validation and runtime parameters
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {configs.map((group) => {
          const GroupIcon = group.icon;
          return (
            <div key={group.group} className="rounded-xl bg-dev-card border border-dev-border p-5 space-y-4">
              <div className="flex items-center gap-2.5 text-sm font-semibold text-white">
                <GroupIcon className="w-4 h-4 text-sky-400" />
                <span>{group.group}</span>
              </div>

              <div className="space-y-2">
                {group.items.map((item) => (
                  <div
                    key={item.key}
                    className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-lg bg-dev-surface/70 border border-dev-border/60 text-xs font-mono"
                  >
                    <span className="text-slate-400">{item.key}</span>
                    <div className="flex items-center gap-2 mt-1 sm:mt-0">
                      <span className="text-sky-300 font-semibold">{item.value}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-dev-border text-dev-muted">
                        {item.source}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-4 rounded-xl bg-dev-card border border-dev-border flex items-center justify-between text-xs font-mono">
        <div className="flex items-center gap-2 text-slate-300">
          <CheckCircle className="w-4 h-4 text-emerald-400" />
          <span>Strict Environment Validation active via Pydantic Settings</span>
        </div>
        <span className="text-dev-muted">No secrets stored in source control</span>
      </div>
    </div>
  );
};
