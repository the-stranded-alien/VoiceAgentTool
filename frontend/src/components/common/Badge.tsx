import React from 'react';
import { CallStatus } from '../../types/index';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'error' | 'warning' | 'info' | 'default';
  color?: 'green' | 'yellow' | 'red' | 'blue' | 'gray';
  status?: CallStatus;
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant,
  color,
  status,
  size = 'md',
  icon,
  className = '',
}) => {
  // Determine variant from color if provided
  let finalVariant = variant || 'default';

  if (color) {
    switch (color) {
      case 'green':
        finalVariant = 'success';
        break;
      case 'blue':
        finalVariant = 'info';
        break;
      case 'red':
        finalVariant = 'error';
        break;
      case 'yellow':
        finalVariant = 'warning';
        break;
      case 'gray':
        finalVariant = 'default';
        break;
    }
  }

  // Determine variant from status if provided
  if (status) {
    switch (status) {
      case CallStatus.COMPLETED:
        finalVariant = 'success';
        break;
      case CallStatus.IN_PROGRESS:
      case CallStatus.RINGING:
      case CallStatus.INITIATED:
        finalVariant = 'info';
        break;
      case CallStatus.FAILED:
      case CallStatus.CANCELLED:
        finalVariant = 'error';
        break;
      case CallStatus.NO_ANSWER:
      case CallStatus.BUSY:
        finalVariant = 'warning';
        break;
      default:
        finalVariant = 'default';
    }
  }

  const variantClasses = {
    success: 'bg-green-100 text-green-800 border-green-200',
    error: 'bg-red-100 text-red-800 border-red-200',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    info: 'bg-blue-100 text-blue-800 border-blue-200',
    default: 'bg-gray-100 text-gray-800 border-gray-200',
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-2.5 py-1 text-sm gap-1.5',
    lg: 'px-3 py-1.5 text-base gap-2',
  };

  return (
    <span
      className={`
        inline-flex items-center font-medium rounded-full border
        ${variantClasses[finalVariant]}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      {icon && <span className="inline-flex">{icon}</span>}
      {children}
    </span>
  );
};
