import React from 'react';
import { Sparkles, Terminal, Github, ExternalLink } from 'lucide-react';
import { StatusBadge } from '../common/StatusBadge';
import { HealthStatusResponse } from '../../types';

interface HeaderProps {
  health: HealthStatusResponse | null;
  loading: boolean;
  onRefreshHealth: () => void;
}

export const Header: React.FC<HeaderProps> = ({ health, loading, onRefreshHealth }) => {
  return (
    <header className="h-16 border-b border-dev-border bg-dev-surface/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-base tracking-tight text-white">RepoLens AI</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800/80 font-medium">
              v0.1.0-alpha
            </span>
          </div>
          <p className="text-xs text-dev-muted hidden sm:block">Agentic GitHub Codebase Explorer</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Backend health indicator */}
        <button
          onClick={onRefreshHealth}
          title="Click to re-check backend health"
          className="flex items-center gap-2 hover:opacity-80 transition cursor-pointer"
        >
          <span className="text-xs text-dev-muted hidden md:inline font-mono">Backend:</span>
          {loading ? (
            <StatusBadge status="loading" />
          ) : health ? (
            <StatusBadge status={health.status} label={`${health.status} (${health.environment})`} />
          ) : (
            <StatusBadge status="offline" label="Backend unreachable" />
          )}
        </button>

        <div className="h-4 w-px bg-dev-border hidden sm:block" />

        {/* Quick links */}
        <div className="flex items-center gap-2">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 text-xs text-dev-muted hover:text-white px-2.5 py-1.5 rounded-md hover:bg-dev-hover transition font-mono border border-transparent hover:border-dev-border"
          >
            <Terminal className="w-3.5 h-3.5 text-sky-400" />
            <span className="hidden sm:inline">Swagger API</span>
            <ExternalLink className="w-3 h-3 opacity-60" />
          </a>

          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="p-1.5 rounded-md text-dev-muted hover:text-white hover:bg-dev-hover transition"
            aria-label="GitHub"
          >
            <Github className="w-4 h-4" />
          </a>
        </div>
      </div>
    </header>
  );
};
