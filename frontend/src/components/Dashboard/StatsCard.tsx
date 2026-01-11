import React from 'react';
import { Card } from '../common/Card';

interface StatsCardProps {
  title: string;
  value: number | string;
  icon: React.ComponentType<{ size?: number; className?: string; strokeWidth?: number }>;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color: 'purple' | 'green' | 'blue' | 'red' | 'orange';
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  icon: Icon,
  trend,
  color,
}) => {
  const colorClasses = {
    purple: {
      bg: 'bg-purple-500',
      text: 'text-purple-600',
      lightBg: 'bg-purple-50',
      gradient: 'from-purple-500 to-purple-600',
    },
    green: {
      bg: 'bg-green-500',
      text: 'text-green-600',
      lightBg: 'bg-green-50',
      gradient: 'from-green-500 to-green-600',
    },
    blue: {
      bg: 'bg-blue-500',
      text: 'text-blue-600',
      lightBg: 'bg-blue-50',
      gradient: 'from-blue-500 to-blue-600',
    },
    red: {
      bg: 'bg-red-500',
      text: 'text-red-600',
      lightBg: 'bg-red-50',
      gradient: 'from-red-500 to-red-600',
    },
    orange: {
      bg: 'bg-orange-500',
      text: 'text-orange-600',
      lightBg: 'bg-orange-50',
      gradient: 'from-orange-500 to-orange-600',
    },
  };

  const colors = colorClasses[color];

  return (
    <Card hover className="relative overflow-hidden">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mb-2">{value}</p>
        </div>
        <div
          className={`w-16 h-16 rounded-xl bg-gradient-to-br ${colors.gradient} flex items-center justify-center shadow-lg`}
        >
          <Icon size={32} className="text-white" strokeWidth={2} />
        </div>
      </div>

      {/* Decorative gradient background */}
      <div
        className={`absolute -right-8 -bottom-8 w-32 h-32 rounded-full opacity-5 ${colors.bg}`}
      />
    </Card>
  );
};

