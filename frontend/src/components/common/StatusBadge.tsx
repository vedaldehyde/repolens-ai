import React from 'react';

interface StatusBadgeProps {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'loading' | 'offline';
  label?: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label, className = '' }) => {
  const configs = {
    healthy: {
      dot: 'bg-emerald-400',
      badge: 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60',
      text: 'Healthy',
    },
    degraded: {
      dot: 'bg-amber-400',
      badge: 'bg-amber-950/60 text-amber-300 border-amber-800/60',
      text: 'Degraded',
    },
    unhealthy: {
      dot: 'bg-rose-400',
      badge: 'bg-rose-950/60 text-rose-300 border-rose-800/60',
      text: 'Unhealthy',
    },
    loading: {
      dot: 'bg-sky-400 animate-ping',
      badge: 'bg-sky-950/60 text-sky-300 border-sky-800/60',
      text: 'Checking...',
    },
    offline: {
      dot: 'bg-slate-500',
      badge: 'bg-slate-900/60 text-slate-400 border-slate-700/60',
      text: 'Offline',
    },
  };

  const current = configs[status] || configs.offline;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium border ${current.badge} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${current.dot}`} />
      {label || current.text}
    </span>
  );
};
