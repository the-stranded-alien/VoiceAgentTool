import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '../../../test/utils';
import { Card } from '../Card';

describe('Card', () => {
  it('renders with children', () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('applies glass effect by default', () => {
    const { container } = render(<Card>Content</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('bg-white/80', 'backdrop-blur-sm');
  });

  it('does not apply glass effect when glass is false', () => {
    const { container } = render(<Card glass={false}>Content</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('bg-white');
    expect(card).not.toHaveClass('bg-white/80');
  });

  it('applies hover classes when hover prop is true', () => {
    const { container } = render(<Card hover>Content</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('hover:shadow-2xl', 'hover:scale-[1.02]', 'cursor-pointer');
  });

  it('calls onClick when clicked and hover is true', async () => {
    const handleClick = vi.fn();
    const { container } = render(<Card hover onClick={handleClick}>Content</Card>);
    const card = container.firstChild as HTMLElement;

    card.click();
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies correct padding classes', () => {
    const { container, rerender } = render(<Card padding="sm">Content</Card>);
    let card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('p-3');

    rerender(<Card padding="md">Content</Card>);
    card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('p-6');

    rerender(<Card padding="lg">Content</Card>);
    card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('p-8');

    rerender(<Card padding="none">Content</Card>);
    card = container.firstChild as HTMLElement;
    expect(card).not.toHaveClass('p-3', 'p-6', 'p-8');
  });

  it('applies custom className', () => {
    const { container } = render(<Card className="custom-class">Content</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('custom-class');
  });
});
