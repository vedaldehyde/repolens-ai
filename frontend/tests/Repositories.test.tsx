import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../src/App';
import * as repoService from '../src/services/repositories';

vi.mock('../src/services/health', () => ({
  fetchHealthStatus: vi.fn().mockResolvedValue({
    status: 'healthy',
    timestamp: '2026-11-06T12:00:00Z',
    version: '0.1.0',
    environment: 'development',
    uptime_seconds: 42.5,
    details: {
      storage: { repos_dir_exists: true, chroma_dir_exists: true },
      environment: 'development',
      debug: true,
    },
  }),
}));

vi.mock('../src/services/repositories', () => ({
  fetchRepositories: vi.fn().mockResolvedValue([
    {
      id: 'octocat__Hello-World',
      name: 'Hello-World',
      owner: 'octocat',
      github_url: 'https://github.com/octocat/Hello-World',
      commit_sha: '7fd1a60b01f91b314f59955a4e4d4e80d8edf11d',
      file_count: 3,
      total_size_bytes: 4096,
      detected_languages: ['Python', 'Markdown'],
      has_readme: true,
      readme_path: 'README.md',
      ingested_at: '2026-11-06T12:00:00Z',
      status: 'completed',
    },
  ]),
  fetchRepository: vi.fn().mockResolvedValue({
    id: 'octocat__Hello-World',
    name: 'Hello-World',
    owner: 'octocat',
    github_url: 'https://github.com/octocat/Hello-World',
    commit_sha: '7fd1a60b01f91b314f59955a4e4d4e80d8edf11d',
    file_count: 3,
    total_size_bytes: 4096,
    detected_languages: ['Python', 'Markdown'],
    has_readme: true,
    readme_path: 'README.md',
    ingested_at: '2026-11-06T12:00:00Z',
    status: 'completed',
  }),
  fetchRepositoryFiles: vi.fn().mockResolvedValue({
    repository_id: 'octocat__Hello-World',
    file_count: 3,
    files: [
      {
        path: 'main.py',
        size_bytes: 256,
        extension: '.py',
        language: 'Python',
        category: 'code',
      },
      {
        path: 'README.md',
        size_bytes: 512,
        extension: '.md',
        language: 'Markdown',
        category: 'documentation',
      },
    ],
  }),
  ingestRepository: vi.fn().mockResolvedValue({
    id: 'psf__requests',
    name: 'requests',
    owner: 'psf',
    github_url: 'https://github.com/psf/requests',
    commit_sha: 'b148c3453b341f2747d7c6722d515a28f8acfa9b',
    file_count: 15,
    total_size_bytes: 32000,
    detected_languages: ['Python', 'Markdown'],
    has_readme: true,
    readme_path: 'README.md',
    ingested_at: '2026-11-06T12:00:00Z',
    status: 'completed',
  }),
}));

describe('Repository Ingestion and Explorer Frontend', () => {
  it('renders ingestion form and handles successful submission', async () => {
    render(<App />);

    const input = screen.getByPlaceholderText('https://github.com/psf/requests');
    const submitBtn = screen.getByText('Ingest Repository');

    fireEvent.change(input, { target: { value: 'https://github.com/psf/requests' } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(repoService.ingestRepository).toHaveBeenCalledWith({
        github_url: 'https://github.com/psf/requests',
      });
    });

    await waitFor(() => {
      expect(screen.getByText('Explore Discovered Files')).toBeInTheDocument();
    });
  });

  it('rejects invalid URLs with client validation message', async () => {
    render(<App />);

    const input = screen.getByPlaceholderText('https://github.com/psf/requests');
    const submitBtn = screen.getByText('Ingest Repository');

    fireEvent.change(input, { target: { value: 'http://insecure-url.com' } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/Invalid URL\. Expected format/i)).toBeInTheDocument();
    });
  });
});
