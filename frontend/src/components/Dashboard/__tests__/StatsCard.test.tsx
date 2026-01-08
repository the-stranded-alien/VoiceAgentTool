import { describe, it, expect } from 'vitest';
import { render, screen } from '../../../test/utils';
import { StatsCard } from '../StatsCard';
import { Phone } from 'lucide-react';

describe('StatsCard', () => {
  it('renders with title and value', () => {
    render(<StatsCard title="Total Calls" value={100} icon={Phone} color="purple" />);
    expect(screen.getByText('Total Calls')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('renders with string value', () => {
    render(<StatsCard title="Status" value="Active" icon={Phone} color="green" />);
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('renders icon', () => {
    const { container } = render(<StatsCard title="Calls" value={50} icon={Phone} color="blue" />);
    // Phone icon from lucide-react will be rendered
    const iconContainer = container.querySelector('.from-blue-500');
    expect(iconContainer).toBeInTheDocument();
  });

  it('renders trend indicator when trend is provided', () => {
    render(
      <StatsCard
        title="Calls"
        value={100}
        icon={Phone}
        color="purple"
        trend={{ value: 15, isPositive: true }}
      />
    );
    expect(screen.getByText('↑')).toBeInTheDocument();
    expect(screen.getByText('15%')).toBeInTheDocument();
    expect(screen.getByText('vs last week')).toBeInTheDocument();
  });

  it('shows negative trend indicator', () => {
    render(
      <StatsCard
        title="Calls"
        value={80}
        icon={Phone}
        color="red"
        trend={{ value: 10, isPositive: false }}
      />
    );
    expect(screen.getByText('↓')).toBeInTheDocument();
    expect(screen.getByText('10%')).toBeInTheDocument();
  });

  it('applies correct color classes', () => {
    const { container } = render(
      <StatsCard title="Test" value={10} icon={Phone} color="green" />
    );
    const gradientDiv = container.querySelector('.from-green-500');
    expect(gradientDiv).toBeInTheDocument();
  });

  it('does not render trend when not provided', () => {
    render(<StatsCard title="Calls" value={100} icon={Phone} color="purple" />);
    expect(screen.queryByText('vs last week')).not.toBeInTheDocument();
  });
});
