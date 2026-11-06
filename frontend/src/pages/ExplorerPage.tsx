import React, { useEffect, useState, useMemo } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import {
  FolderGit2,
  FileCode,
  FileText,
  FileCog,
  Search,
  GitCommit,
  ExternalLink,
  Copy,
  Check,
  BookOpen,
  Layers,
  ArrowLeft,
  RotateCw,
  HardDrive,
  AlertCircle,
} from 'lucide-react';
import { fetchRepositories, fetchRepositoryFiles } from '../services/repositories';
import { DiscoveredFile, RepositoryMetadata } from '../types';

export const ExplorerPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const repoIdParam = searchParams.get('repo');

  const [repositories, setRepositories] = useState<RepositoryMetadata[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<RepositoryMetadata | null>(null);
  const [files, setFiles] = useState<DiscoveredFile[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filesLoading, setFilesLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<'all' | 'code' | 'documentation' | 'configuration'>('all');
  const [copiedSha, setCopiedSha] = useState(false);

  // Load list of all ingested repositories
  const loadRepositories = async () => {
    try {
      setLoading(true);
      setError(null);
      const list = await fetchRepositories();
      setRepositories(list);

      // Auto-select repository from URL parameter or first available
      if (list.length > 0) {
        const target = repoIdParam ? list.find((r) => r.id === repoIdParam) || list[0] : list[0];
        setSelectedRepo(target);
        if (target.id !== repoIdParam) {
          setSearchParams({ repo: target.id });
        }
      } else {
        setSelectedRepo(null);
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load ingested repositories.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRepositories();
  }, []);

  // When selected repo changes, load its files
  useEffect(() => {
    if (!selectedRepo) {
      setFiles([]);
      return;
    }

    const loadFiles = async () => {
      try {
        setFilesLoading(true);
        const res = await fetchRepositoryFiles(selectedRepo.id);
        setFiles(res.files);
      } catch (err: any) {
        console.error('Failed to load files:', err);
      } finally {
        setFilesLoading(false);
      }
    };

    loadFiles();
  }, [selectedRepo]);

  const handleSelectRepo = (repo: RepositoryMetadata) => {
    setSelectedRepo(repo);
    setSearchParams({ repo: repo.id });
  };

  const handleCopySha = (sha: string) => {
    navigator.clipboard.writeText(sha);
    setCopiedSha(true);
    setTimeout(() => setCopiedSha(false), 2000);
  };

  // Filtered files calculation
  const filteredFiles = useMemo(() => {
    return files.filter((file) => {
      const matchesSearch = file.path.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = categoryFilter === 'all' || file.category === categoryFilter;
      return matchesSearch && matchesCategory;
    });
  }, [files, searchTerm, categoryFilter]);

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const getFileIcon = (file: DiscoveredFile) => {
    if (file.category === 'code') return <FileCode className="w-4 h-4 text-sky-400" />;
    if (file.category === 'documentation') return <FileText className="w-4 h-4 text-emerald-400" />;
    return <FileCog className="w-4 h-4 text-amber-400" />;
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto py-12 flex flex-col items-center justify-center space-y-3">
        <RotateCw className="w-8 h-8 text-sky-400 animate-spin" />
        <p className="text-sm text-dev-muted font-mono">Loading ingested repositories...</p>
      </div>
    );
  }

  if (repositories.length === 0) {
    return (
      <div className="max-w-3xl mx-auto py-12 text-center space-y-6">
        <div className="w-16 h-16 mx-auto rounded-2xl bg-dev-card border border-dev-border flex items-center justify-center text-sky-400 shadow-lg">
          <FolderGit2 className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-white">No Repositories Ingested Yet</h2>
          <p className="text-sm text-dev-muted max-w-md mx-auto">
            Submit a public GitHub repository on the dashboard to clone, scan, and inspect its source files.
          </p>
        </div>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-sm transition shadow-lg shadow-sky-500/20"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Go to Ingestion Dashboard</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Top Bar with Repo Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-dev-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-sky-400" />
            <span>Codebase Explorer</span>
          </h1>
          <p className="text-xs text-dev-muted font-mono mt-0.5">
            Discovered source files & Git metadata (Phase 2)
          </p>
        </div>

        {/* Repository selector pills / dropdown */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
          <span className="text-xs text-dev-muted font-mono whitespace-nowrap">Repository:</span>
          <select
            value={selectedRepo?.id || ''}
            onChange={(e) => {
              const target = repositories.find((r) => r.id === e.target.value);
              if (target) handleSelectRepo(target);
            }}
            className="bg-dev-card border border-dev-border text-white text-xs rounded-lg px-3 py-1.5 font-mono focus:outline-none focus:border-sky-500 transition"
          >
            {repositories.map((repo) => (
              <option key={repo.id} value={repo.id}>
                {repo.owner}/{repo.name} ({repo.file_count} files)
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800 text-rose-300 text-xs font-mono flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {selectedRepo && (
        <>
          {/* Repository Overview Metadata Card */}
          <div className="rounded-xl bg-dev-card border border-dev-border p-5 space-y-4 shadow-sm">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <h2 className="text-lg font-bold text-white tracking-tight">
                    {selectedRepo.owner} / <span className="text-sky-400">{selectedRepo.name}</span>
                  </h2>
                  <a
                    href={selectedRepo.github_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-sky-400 hover:text-sky-300 font-mono"
                  >
                    <span>GitHub</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
                <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-dev-muted">
                  <span className="flex items-center gap-1.5">
                    <GitCommit className="w-3.5 h-3.5 text-sky-400" />
                    <span>Commit:</span>
                    <button
                      onClick={() => handleCopySha(selectedRepo.commit_sha)}
                      title="Click to copy full commit SHA"
                      className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-dev-surface text-slate-300 hover:text-white border border-dev-border transition"
                    >
                      <span>{selectedRepo.commit_sha.slice(0, 8)}</span>
                      {copiedSha ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3 text-dev-muted" />}
                    </button>
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Layers className="w-3.5 h-3.5 text-purple-400" />
                    <span>{selectedRepo.file_count} files</span>
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <HardDrive className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{formatBytes(selectedRepo.total_size_bytes)}</span>
                  </span>
                  {selectedRepo.has_readme && (
                    <>
                      <span>•</span>
                      <span className="flex items-center gap-1 text-emerald-400 font-medium">
                        <BookOpen className="w-3.5 h-3.5" />
                        <span>{selectedRepo.readme_path || 'README'}</span>
                      </span>
                    </>
                  )}
                </div>
              </div>

              {/* Detected Languages Badges */}
              <div className="flex flex-wrap items-center gap-1.5">
                {selectedRepo.detected_languages.map((lang) => (
                  <span
                    key={lang}
                    className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-dev-surface text-sky-300 border border-dev-border"
                  >
                    {lang}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Discovered Files Browser */}
          <div className="rounded-xl bg-dev-card border border-dev-border overflow-hidden">
            {/* Search and Filters Header */}
            <div className="p-4 border-b border-dev-border flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-dev-surface/40">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dev-muted" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Filter files by path or name..."
                  className="w-full bg-dev-bg border border-dev-border rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-dev-muted focus:outline-none focus:border-sky-500 font-mono transition"
                />
              </div>

              {/* Category Filter Chips */}
              <div className="flex items-center gap-1.5 text-xs font-mono">
                {[
                  { key: 'all', label: 'All' },
                  { key: 'code', label: 'Code' },
                  { key: 'documentation', label: 'Docs' },
                  { key: 'configuration', label: 'Config' },
                ].map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setCategoryFilter(tab.key as any)}
                    className={`px-2.5 py-1 rounded-md transition ${
                      categoryFilter === tab.key
                        ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 font-semibold'
                        : 'text-dev-muted hover:text-white hover:bg-dev-surface'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Files List Table */}
            {filesLoading ? (
              <div className="p-12 text-center text-xs font-mono text-dev-muted space-y-2">
                <RotateCw className="w-5 h-5 animate-spin mx-auto text-sky-400" />
                <p>Loading repository files...</p>
              </div>
            ) : filteredFiles.length === 0 ? (
              <div className="p-12 text-center text-xs font-mono text-dev-muted">
                {searchTerm ? 'No files match your search filter.' : 'No files discovered in repository.'}
              </div>
            ) : (
              <div className="divide-y divide-dev-border/50 max-h-[500px] overflow-y-auto">
                {filteredFiles.map((file) => (
                  <div
                    key={file.path}
                    className="flex items-center justify-between p-3 px-4 hover:bg-dev-surface/60 transition text-xs font-mono group"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      {getFileIcon(file)}
                      <span className="text-slate-200 group-hover:text-white truncate">
                        {file.path}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 flex-shrink-0 text-dev-muted">
                      <span className="px-2 py-0.5 rounded bg-dev-surface text-[10px] text-slate-300 border border-dev-border/70">
                        {file.language}
                      </span>
                      <span className="text-[11px] w-16 text-right">
                        {formatBytes(file.size_bytes)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Footer Summary */}
            <div className="p-3 px-4 bg-dev-surface/60 border-t border-dev-border text-[11px] font-mono text-dev-muted flex items-center justify-between">
              <span>Showing {filteredFiles.length} of {files.length} discovered files</span>
              <span>Ready for Phase 3 Code Parsing & AST Symbol Extraction</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
