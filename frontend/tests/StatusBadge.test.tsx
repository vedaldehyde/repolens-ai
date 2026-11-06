import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatusBadge } from '../src/components/common/StatusBadge';

describe('StatusBadge', () => {
  it('renders healthy status with default label', () => {
    render(<StatusBadge status="healthy" />);
    expect(screen.getByText('Healthy')).toBeInTheDocument();
  });

  it('renders custom label when provided', () => {
    render(<StatusBadge status="healthy" label="System Operational" />);
    expect(screen.getByText('System Operational')).toBeInTheDocument();
  });

  it('renders offline status', () => {
    render(<StatusBadge status="offline" />);
    expect(screen.getByText('Offline')).toBeInTheDocument();
  });
});
