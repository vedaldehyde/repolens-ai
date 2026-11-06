import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderGit2,
  Settings as SettingsIcon,
  Cpu,
  Workflow,
  Layers,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    {
      to: '/',
      label: 'Dashboard',
      icon: LayoutDashboard,
      activeExact: true,
    },
    {
      to: '/explorer',
      label: 'Code Explorer',
      icon: FolderGit2,
      badge: 'Phase 2',
    },
    {
      to: '/settings',
      label: 'Configuration',
      icon: SettingsIcon,
    },
  ];

  const techStackBadges = [
    { name: 'FastAPI', icon: Cpu, color: 'text-emerald-400' },
    { name: 'LangGraph', icon: Workflow, color: 'text-indigo-400' },
    { name: 'ChromaDB', icon: Layers, color: 'text-sky-400' },
  ];

  return (
    <aside className="w-64 border-r border-dev-border bg-dev-surface/40 flex flex-col justify-between p-4 flex-shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div>
          <div className="text-[11px] font-mono uppercase tracking-wider text-dev-muted px-3 mb-2 font-semibold">
            Platform
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.activeExact}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition ${
                      isActive
                        ? 'bg-dev-card text-sky-400 border border-sky-500/30 shadow-sm'
                        : 'text-dev-muted hover:text-white hover:bg-dev-hover/60'
                    }`
                  }
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-dev-border/70 text-slate-400">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        <div>
          <div className="text-[11px] font-mono uppercase tracking-wider text-dev-muted px-3 mb-2 font-semibold">
            Core Engine
          </div>
          <div className="space-y-1.5 px-3">
            {techStackBadges.map((tech) => {
              const TechIcon = tech.icon;
              return (
                <div
                  key={tech.name}
                  className="flex items-center gap-2 text-xs text-dev-muted font-mono py-1"
                >
                  <TechIcon className={`w-3.5 h-3.5 ${tech.color}`} />
                  <span>{tech.name}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Environment status banner */}
      <div className="p-3 rounded-lg bg-dev-card border border-dev-border text-xs space-y-1 font-mono">
        <div className="flex items-center justify-between text-dev-muted">
          <span>Architecture:</span>
          <span className="text-white font-semibold">Phase 2</span>
        </div>
        <div className="flex items-center justify-between text-dev-muted">
          <span>Ingestion:</span>
          <span className="text-emerald-400">Git CLI Active</span>
        </div>
      </div>
    </aside>
  );
};
