import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  glass?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hover = false,
  glass = true,
  padding = 'md',
  onClick,
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-6',
    lg: 'p-8',
  };

  const glassClasses = glass
    ? 'bg-white/80 backdrop-blur-sm border border-white/20 shadow-xl'
    : 'bg-white border border-gray-200 shadow-md';

  const hoverClasses = hover
    ? 'hover:shadow-2xl hover:scale-[1.02] cursor-pointer'
    : '';

  return (
    <div
      className={`
        rounded-xl transition-all duration-300
        ${glassClasses}
        ${hoverClasses}
        ${paddingClasses[padding]}
        ${className}
      `}
      onClick={onClick}
    >
      {children}
    </div>
  );
};
