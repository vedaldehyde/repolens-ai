import React, { useState, useEffect } from 'react';
import { useOutletContext, Link } from 'react-router-dom';
import {
  Github,
  Search,
  Activity,
  Layers,
  AlertCircle,
  GitBranch,
  ShieldCheck,
  Bot,
  Binary,
  ArrowRight,
  Database,
  Terminal,
  RotateCw,
  GitCommit,
  FolderGit2,
  HardDrive,
  BookOpen,
} from 'lucide-react';
import { HealthStatusResponse, RepositoryMetadata } from '../types';
import { ingestRepository, fetchRepositories } from '../services/repositories';

interface OutletContextType {
  health: HealthStatusResponse | null;
  loading: boolean;
  refreshHealth: () => void;
}

export const DashboardPage: React.FC = () => {
  const { health, loading, refreshHealth } = useOutletContext<OutletContextType>();

  const [repoUrl, setRepoUrl] = useState('');
  const [ingesting, setIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [latestIngested, setLatestIngested] = useState<RepositoryMetadata | null>(null);
  const [recentRepos, setRecentRepos] = useState<RepositoryMetadata[]>([]);

  // Load existing ingested repositories
  const loadRecentRepos = async () => {
    try {
      const list = await fetchRepositories();
      setRecentRepos(list);
      if (list.length > 0 && !latestIngested) {
        setLatestIngested(list[0]);
      }
    } catch {
      // Ignore initial background load error
    }
  };

  useEffect(() => {
    loadRecentRepos();
  }, []);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    const clean = repoUrl.trim();
    if (!clean) {
      setErrorMsg('Please enter a GitHub repository URL.');
      return;
    }

    const githubRegex = /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/;
    if (!githubRegex.test(clean)) {
      setErrorMsg('Invalid URL. Expected format: https://github.com/owner/repository');
      return;
    }

    try {
      setIngesting(true);
      setIngestStatus('Cloning repository via Git CLI (depth=1)...');

      // Progress ticker for developer feedback
      const timer = setTimeout(() => {
        setIngestStatus('Scanning source files, filtering binaries & extracting metadata...');
      }, 1500);

      const result = await ingestRepository({ github_url: clean });
      clearTimeout(timer);

      setLatestIngested(result);
      setRepoUrl('');
      await loadRecentRepos();
    } catch (err: any) {
      setErrorMsg(err?.message || 'Repository ingestion failed. Please verify the URL and access permissions.');
    } finally {
      setIngesting(false);
      setIngestStatus('');
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const architecturePillars = [
    {
      title: 'FastAPI Backend',
      desc: 'High-performance async REST API with Pydantic v2 schemas and CORS security.',
      icon: Activity,
      color: 'text-emerald-400',
      border: 'border-emerald-500/20',
      status: 'Implemented (Phase 1)',
      badge: 'bg-emerald-950/70 text-emerald-300 border-emerald-800',
    },
    {
      title: 'Git CLI Ingestion',
      desc: 'Safe subprocess shallow-cloning, SSRF prevention, commit SHA tracking, and binary filtering.',
      icon: GitBranch,
      color: 'text-sky-400',
      border: 'border-sky-500/20',
      status: 'Implemented (Phase 2)',
      badge: 'bg-sky-950/70 text-sky-300 border-sky-800',
    },
    {
      title: 'AST & Code Parsing',
      desc: 'Python AST extraction for functions, classes, docstrings, and symbol tables.',
      icon: Binary,
      color: 'text-purple-400',
      border: 'border-purple-500/20',
      status: 'Ready for Phase 3',
      badge: 'bg-purple-950/70 text-purple-300 border-purple-800',
    },
    {
      title: 'ChromaDB Vector Store',
      desc: 'Locally persisted embedding vectors via SentenceTransformers for RAG semantic search.',
      icon: Database,
      color: 'text-amber-400',
      border: 'border-amber-500/20',
      status: 'Ready for Phase 3',
      badge: 'bg-amber-950/70 text-amber-300 border-amber-800',
    },
    {
      title: 'LangGraph Orchestrator',
      desc: 'Agentic multi-step reasoning, retrieval augmentation, and Groq LLM synthesis.',
      icon: Bot,
      color: 'text-indigo-400',
      border: 'border-indigo-500/20',
      status: 'Ready for Phase 4',
      badge: 'bg-indigo-950/70 text-indigo-300 border-indigo-800',
    },
    {
      title: 'FastMCP Tools Interface',
      desc: 'Standardized Model Context Protocol exposing codebase exploration to external agents.',
      icon: Layers,
      color: 'text-rose-400',
      border: 'border-rose-500/20',
      status: 'Ready for Phase 5',
      badge: 'bg-rose-950/70 text-rose-300 border-rose-800',
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Hero & Ingestion Form */}
      <div className="relative rounded-2xl bg-gradient-to-b from-dev-card to-dev-surface p-8 border border-dev-border shadow-xl overflow-hidden">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-sky-950/60 border border-sky-800/60 text-sky-300">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Phase 2 Ingestion Active</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
            Explore Codebases with <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-400">Agentic Precision</span>
          </h1>

          <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
            Submit any public GitHub repository to shallow-clone, scan, and inspect its source files and dependencies.
          </p>

          {/* Repo Input Form */}
          <form onSubmit={handleIngest} className="mt-6 flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Github className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-dev-muted" />
              <input
                type="url"
                value={repoUrl}
                disabled={ingesting}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/psf/requests"
                className="w-full bg-dev-bg border border-dev-border rounded-lg pl-10 pr-4 py-2.5 text-sm text-white placeholder-dev-muted focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition font-mono disabled:opacity-60"
              />
            </div>
            <button
              type="submit"
              disabled={ingesting}
              className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 disabled:bg-sky-700 text-slate-950 font-semibold text-sm transition shadow-lg shadow-sky-500/20 cursor-pointer disabled:cursor-not-allowed"
            >
              {ingesting ? (
                <>
                  <RotateCw className="w-4 h-4 animate-spin" />
                  <span>Ingesting...</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  <span>Ingest Repository</span>
                </>
              )}
            </button>
          </form>

          {/* Progress / Status feedback */}
          {ingesting && (
            <div className="text-xs font-mono p-3 rounded-lg border bg-sky-950/40 border-sky-800 text-sky-300 flex items-center gap-2.5">
              <RotateCw className="w-4 h-4 animate-spin flex-shrink-0 text-sky-400" />
              <span>{ingestStatus}</span>
            </div>
          )}

          {errorMsg && (
            <div className="text-xs font-mono p-3 rounded-lg border bg-rose-950/50 border-rose-800 text-rose-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>
      </div>

      {/* Successfully Ingested Result Card */}
      {latestIngested && (
        <div className="rounded-xl bg-dev-card border border-sky-500/30 p-6 space-y-4 shadow-lg shadow-sky-500/5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-dev-border pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-dev-surface border border-dev-border flex items-center justify-center text-sky-400">
                <FolderGit2 className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-white">
                    {latestIngested.owner} / <span className="text-sky-400">{latestIngested.name}</span>
                  </h3>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800">
                    Ingested
                  </span>
                </div>
                <p className="text-xs font-mono text-dev-muted mt-0.5">
                  ID: <span className="text-slate-300">{latestIngested.id}</span>
                </p>
              </div>
            </div>

            <Link
              to={`/explorer?repo=${latestIngested.id}`}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-dev-surface hover:bg-dev-hover text-sky-400 text-xs font-mono font-medium border border-dev-border transition"
            >
              <span>Explore Discovered Files</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-3 rounded-lg bg-dev-surface/70 border border-dev-border">
              <span className="text-dev-muted block">Commit SHA</span>
              <span className="text-white font-semibold flex items-center gap-1 mt-1">
                <GitCommit className="w-3.5 h-3.5 text-sky-400" />
                {latestIngested.commit_sha.slice(0, 8)}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-dev-surface/70 border border-dev-border">
              <span className="text-dev-muted block">Files Discovered</span>
              <span className="text-white font-semibold flex items-center gap-1 mt-1">
                <Layers className="w-3.5 h-3.5 text-purple-400" />
                {latestIngested.file_count} files
              </span>
            </div>

            <div className="p-3 rounded-lg bg-dev-surface/70 border border-dev-border">
              <span className="text-dev-muted block">Indexed Size</span>
              <span className="text-white font-semibold flex items-center gap-1 mt-1">
                <HardDrive className="w-3.5 h-3.5 text-emerald-400" />
                {formatBytes(latestIngested.total_size_bytes)}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-dev-surface/70 border border-dev-border">
              <span className="text-dev-muted block">README</span>
              <span className="text-white font-semibold flex items-center gap-1 mt-1">
                <BookOpen className="w-3.5 h-3.5 text-amber-400" />
                {latestIngested.has_readme ? 'Available' : 'None'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 pt-1">
            <span className="text-xs font-mono text-dev-muted">Languages:</span>
            <div className="flex flex-wrap gap-1.5">
              {latestIngested.detected_languages.map((lang) => (
                <span
                  key={lang}
                  className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-dev-surface text-slate-300 border border-dev-border"
                >
                  {lang}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Backend Live Diagnostics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl bg-dev-card border border-dev-border p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-dev-muted">Service Health</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">
              {loading ? 'Checking...' : health ? health.status.toUpperCase() : 'OFFLINE'}
            </span>
          </div>
          <div className="text-xs text-dev-muted flex items-center justify-between pt-1 border-t border-dev-border/50 font-mono">
            <span>Uptime:</span>
            <span className="text-slate-300">
              {health ? `${health.uptime_seconds}s` : 'N/A'}
            </span>
          </div>
        </div>

        <div className="rounded-xl bg-dev-card border border-dev-border p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-dev-muted">Environment</span>
            <Terminal className="w-4 h-4 text-sky-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">
              {health?.environment || 'development'}
            </span>
          </div>
          <div className="text-xs text-dev-muted flex items-center justify-between pt-1 border-t border-dev-border/50 font-mono">
            <span>API Version:</span>
            <span className="text-slate-300">{health?.version || '0.1.0'}</span>
          </div>
        </div>

        <div className="rounded-xl bg-dev-card border border-dev-border p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-dev-muted">Ingested Repositories</span>
            <Database className="w-4 h-4 text-purple-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">
              {recentRepos.length}
            </span>
            <span className="text-xs font-mono text-dev-muted">repositories</span>
          </div>
          <div className="text-xs text-dev-muted flex items-center justify-between pt-1 border-t border-dev-border/50 font-mono">
            <span>Storage Status:</span>
            <span className="text-emerald-400 font-semibold">Active</span>
          </div>
        </div>
      </div>

      {/* Architecture Roadmap Cards */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-white">Project Architectural Modules</h2>
            <p className="text-xs text-dev-muted font-mono">
              Clean separation of concerns across ingestion, parsing, retrieval, and agents
            </p>
          </div>
          <button
            onClick={refreshHealth}
            className="text-xs font-mono text-sky-400 hover:text-sky-300 flex items-center gap-1 cursor-pointer"
          >
            <span>Diagnostics Re-check</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {architecturePillars.map((pillar) => {
            const Icon = pillar.icon;
            return (
              <div
                key={pillar.title}
                className={`rounded-xl bg-dev-card/80 border ${pillar.border} p-5 space-y-3 hover:border-dev-hover transition`}
              >
                <div className="flex items-center justify-between">
                  <div className="p-2 rounded-lg bg-dev-surface border border-dev-border">
                    <Icon className={`w-5 h-5 ${pillar.color}`} />
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${pillar.badge}`}>
                    {pillar.status}
                  </span>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">{pillar.title}</h3>
                  <p className="text-xs text-dev-muted mt-1 leading-relaxed">{pillar.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
