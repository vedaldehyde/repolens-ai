import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../src/App';

vi.mock('../src/services/health', () => ({
  fetchHealthStatus: vi.fn().mockResolvedValue({
    status: 'healthy',
    timestamp: '2026-11-06T12:00:00Z',
    version: '0.1.0',
    environment: 'development',
    uptime_seconds: 42.5,
    details: {
      storage: {
        repos_dir_exists: true,
        chroma_dir_exists: true,
      },
      environment: 'development',
      debug: true,
    },
  }),
}));

vi.mock('../src/services/repositories', () => ({
  fetchRepositories: vi.fn().mockResolvedValue([]),
  fetchRepository: vi.fn().mockResolvedValue(null),
  fetchRepositoryFiles: vi.fn().mockResolvedValue({ repository_id: '', file_count: 0, files: [] }),
  ingestRepository: vi.fn().mockResolvedValue({}),
}));

describe('RepoLens AI Application', () => {
  it('renders application brand and navigation shell', async () => {
    render(<App />);
    expect(screen.getByText('RepoLens AI')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Code Explorer')).toBeInTheDocument();
    expect(screen.getByText('Configuration')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/healthy \(development\)/i)).toBeInTheDocument();
    });
  });

  it('renders hero title on dashboard', async () => {
    render(<App />);
    expect(screen.getByText(/Explore Codebases with/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText('https://github.com/psf/requests')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Service Health')).toBeInTheDocument();
    });
  });
});
