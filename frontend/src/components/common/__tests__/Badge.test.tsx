import { describe, it, expect } from 'vitest';
import { render, screen } from '../../../test/utils';
import { Badge } from '../Badge';
import { CallStatus } from '../../../types/index';

describe('Badge', () => {
  it('renders with children', () => {
    render(<Badge>Badge text</Badge>);
    expect(screen.getByText('Badge text')).toBeInTheDocument();
  });

  it('applies success variant for completed status', () => {
    render(<Badge status={CallStatus.COMPLETED}>Completed</Badge>);
    const badge = screen.getByText('Completed');
    expect(badge).toHaveClass('bg-green-100', 'text-green-800');
  });

  it('applies info variant for in_progress status', () => {
    render(<Badge status={CallStatus.IN_PROGRESS}>In Progress</Badge>);
    const badge = screen.getByText('In Progress');
    expect(badge).toHaveClass('bg-blue-100', 'text-blue-800');
  });

  it('applies error variant for failed status', () => {
    render(<Badge status={CallStatus.FAILED}>Failed</Badge>);
    const badge = screen.getByText('Failed');
    expect(badge).toHaveClass('bg-red-100', 'text-red-800');
  });

  it('applies warning variant for no_answer status', () => {
    render(<Badge status={CallStatus.NO_ANSWER}>No Answer</Badge>);
    const badge = screen.getByText('No Answer');
    expect(badge).toHaveClass('bg-yellow-100', 'text-yellow-800');
  });

  it('applies correct size classes', () => {
    const { rerender } = render(<Badge size="sm">Small</Badge>);
    let badge = screen.getByText('Small');
    expect(badge).toHaveClass('px-2', 'py-0.5', 'text-xs');

    rerender(<Badge size="md">Medium</Badge>);
    badge = screen.getByText('Medium');
    expect(badge).toHaveClass('px-2.5', 'py-1', 'text-sm');

    rerender(<Badge size="lg">Large</Badge>);
    badge = screen.getByText('Large');
    expect(badge).toHaveClass('px-3', 'py-1.5', 'text-base');
  });

  it('renders with icon', () => {
    const Icon = () => <span data-testid="test-icon">★</span>;
    render(<Badge icon={<Icon />}>With Icon</Badge>);
    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    expect(screen.getByText('With Icon')).toBeInTheDocument();
  });

  it('applies color variants correctly', () => {
    const { rerender } = render(<Badge color="green">Green</Badge>);
    let badge = screen.getByText('Green');
    expect(badge).toHaveClass('bg-green-100');

    rerender(<Badge color="red">Red</Badge>);
    badge = screen.getByText('Red');
    expect(badge).toHaveClass('bg-red-100');

    rerender(<Badge color="blue">Blue</Badge>);
    badge = screen.getByText('Blue');
    expect(badge).toHaveClass('bg-blue-100');
  });
});
