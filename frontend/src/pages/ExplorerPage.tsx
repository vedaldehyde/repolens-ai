import React from 'react';
import { FolderGit2, Code2, Sparkles, AlertCircle } from 'lucide-react';

export const ExplorerPage: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between border-b border-dev-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-sky-400" />
            <span>Codebase Explorer</span>
          </h1>
          <p className="text-xs text-dev-muted font-mono mt-0.5">
            AST Symbol Navigation & Vector Indexing Workspace
          </p>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded bg-amber-950/60 text-amber-300 border border-amber-800">
          Planned for Phase 2
        </span>
      </div>

      <div className="rounded-xl bg-dev-card border border-dev-border p-12 text-center space-y-4">
        <div className="w-14 h-14 mx-auto rounded-2xl bg-dev-surface border border-dev-border flex items-center justify-center text-sky-400">
          <Code2 className="w-7 h-7" />
        </div>
        <div className="max-w-md mx-auto space-y-2">
          <h2 className="text-base font-semibold text-white">Repository Ingestion & Tree-Sitter / AST Parser</h2>
          <p className="text-xs text-dev-muted leading-relaxed">
            Phase 1 sets up the architectural contracts in <code className="text-sky-300 font-mono">app/ingestion</code> and{' '}
            <code className="text-sky-300 font-mono">app/parsing</code>. In Phase 2, this view will feature an interactive
            file tree explorer, AST symbol breakdown, and dependency call graph visualization.
          </p>
        </div>

        <div className="inline-flex items-center gap-2 text-xs font-mono text-dev-muted p-2.5 rounded-lg bg-dev-surface border border-dev-border/70">
          <Sparkles className="w-3.5 h-3.5 text-sky-400" />
          <span>Next step: Phase 2 Git CLI shallow ingestion</span>
        </div>
      </div>

      <div className="p-4 rounded-lg bg-sky-950/20 border border-sky-800/40 text-xs flex items-start gap-3 text-sky-200">
        <AlertCircle className="w-4 h-4 flex-shrink-0 text-sky-400 mt-0.5" />
        <div>
          <p className="font-semibold">Architectural Isolation Guarantee</p>
          <p className="text-sky-300/80 mt-0.5">
            Phase 1 maintains modular boundaries without implementing premature business logic, ensuring clean extensibility.
          </p>
        </div>
      </div>
    </div>
  );
};
