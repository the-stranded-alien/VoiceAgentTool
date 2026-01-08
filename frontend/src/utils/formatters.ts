import { format, formatDistance, formatDuration as formatDurationFns, intervalToDuration } from 'date-fns';

/**
 * Format a date string or Date object to a readable format
 */
export const formatDate = (date: string | Date | undefined, formatStr: string = 'PPp'): string => {
  if (!date) return 'N/A';
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return format(dateObj, formatStr);
  } catch (error) {
    return 'Invalid date';
  }
};

/**
 * Alias for formatDate - Format date and time
 */
export const formatDateTime = formatDate;

/**
 * Format a date as relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: string | Date | undefined): string => {
  if (!date) return 'N/A';
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return formatDistance(dateObj, new Date(), { addSuffix: true });
  } catch (error) {
    return 'Invalid date';
  }
};

/**
 * Format duration in seconds to human readable format (e.g., "2m 30s")
 */
export const formatDuration = (seconds: number | undefined): string => {
  if (seconds === undefined || seconds === null) return 'N/A';

  if (seconds === 0) return '0s';

  const duration = intervalToDuration({ start: 0, end: seconds * 1000 });

  const parts: string[] = [];

  if (duration.hours) parts.push(`${duration.hours}h`);
  if (duration.minutes) parts.push(`${duration.minutes}m`);
  if (duration.seconds) parts.push(`${duration.seconds}s`);

  return parts.join(' ') || '0s';
};

/**
 * Format duration in seconds to MM:SS format
 */
export const formatDurationAsTime = (seconds: number | undefined): string => {
  if (seconds === undefined || seconds === null) return '00:00';

  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);

  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

/**
 * Format phone number to US format (e.g., "+1 (555) 123-4567")
 */
export const formatPhoneNumber = (phone: string | undefined): string => {
  if (!phone) return 'N/A';

  // Remove all non-numeric characters
  const cleaned = phone.replace(/\D/g, '');

  // Check if it's a US number (10 or 11 digits)
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  } else if (cleaned.length === 11 && cleaned[0] === '1') {
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  }

  // Return original if format is unexpected
  return phone;
};

/**
 * Format bytes to human readable file size
 */
export const formatFileSize = (bytes: number | undefined): string => {
  if (bytes === undefined || bytes === null) return 'N/A';

  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

/**
 * Truncate text with ellipsis
 */
export const truncate = (text: string | undefined, maxLength: number = 50): string => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
};

/**
 * Format currency (USD)
 */
export const formatCurrency = (amount: number | undefined): string => {
  if (amount === undefined || amount === null) return '$0.00';

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

/**
 * Format percentage
 */
export const formatPercentage = (value: number | undefined, decimals: number = 1): string => {
  if (value === undefined || value === null) return '0%';
  return `${value.toFixed(decimals)}%`;
};

/**
 * Capitalize first letter of each word
 */
export const capitalizeWords = (text: string | undefined): string => {
  if (!text) return '';
  return text
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};
