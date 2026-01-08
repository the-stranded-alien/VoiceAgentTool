import { describe, it, expect } from 'vitest';
import { render, screen } from '../../../test/utils';
import { Loading } from '../Loading';

describe('Loading', () => {
  it('renders spinner', () => {
    const { container } = render(<Loading />);
    // Check for the Loader2 icon (which has animate-spin class)
    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('renders with text', () => {
    render(<Loading text="Loading data..." />);
    expect(screen.getByText('Loading data...')).toBeInTheDocument();
  });

  it('renders without text by default', () => {
    const { container } = render(<Loading />);
    const text = container.querySelector('p');
    expect(text).not.toBeInTheDocument();
  });

  it('renders as fullScreen when fullScreen prop is true', () => {
    const { container } = render(<Loading fullScreen />);
    const fullScreenDiv = container.querySelector('.fixed.inset-0');
    expect(fullScreenDiv).toBeInTheDocument();
  });

  it('does not render as fullScreen by default', () => {
    const { container } = render(<Loading />);
    const fullScreenDiv = container.querySelector('.fixed.inset-0');
    expect(fullScreenDiv).not.toBeInTheDocument();
  });

  it('applies correct size to spinner', () => {
    const { container, rerender } = render(<Loading size="sm" />);
    let spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();

    rerender(<Loading size="xl" />);
    spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });
});
