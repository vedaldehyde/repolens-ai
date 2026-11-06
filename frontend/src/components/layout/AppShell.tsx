import React, { useEffect, useState, useCallback } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { fetchHealthStatus } from '../../services/health';
import { HealthStatusResponse } from '../../types';

export const AppShell: React.FC = () => {
  const [health, setHealth] = useState<HealthStatusResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadHealth = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchHealthStatus();
      setHealth(data);
    } catch {
      setHealth(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHealth();
    // Periodically poll backend health every 30 seconds
    const interval = setInterval(loadHealth, 30000);
    return () => clearInterval(interval);
  }, [loadHealth]);

  return (
    <div className="min-h-screen bg-dev-bg text-dev-text flex flex-col font-sans">
      <Header health={health} loading={loading} onRefreshHealth={loadHealth} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6 lg:p-8 bg-dev-bg/90">
          <Outlet context={{ health, loading, refreshHealth: loadHealth }} />
        </main>
      </div>
    </div>
  );
};
