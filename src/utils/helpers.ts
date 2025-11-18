import { format, formatDistanceToNow } from 'date-fns';

export const formatDate = (date: string | Date): string => {
  return format(new Date(date), 'MMM dd, yyyy HH:mm');
};

export const formatRelativeTime = (date: string | Date): string => {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const getSeverityColor = (
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical'
): string => {
  const colors = {
    info: '#2196f3',
    low: '#4caf50',
    medium: '#ff9800',
    high: '#ff5722',
    critical: '#f44336',
  };
  return colors[severity];
};

export const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    active: '#4caf50',
    pending: '#ff9800',
    completed: '#2196f3',
    failed: '#f44336',
    paused: '#9e9e9e',
    running: '#2196f3',
    archived: '#757575',
  };
  return colors[status] || '#9e9e9e';
};

export const calculateRiskScore = (data: any): number => {
  // Simplified risk score calculation
  let score = 0;
  if (data.findings) score += data.findings.length * 10;
  if (data.threats) score += data.threats.length * 15;
  if (data.vulnerabilities) score += data.vulnerabilities.length * 20;
  return Math.min(score, 100);
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

export const generateId = (): string => {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
};

export const validateEmail = (email: string): boolean => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

export const validateUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const validateIP = (ip: string): boolean => {
  const ipv4Regex = /^(\d{1,3}\.){3}\d{1,3}$/;
  const ipv6Regex = /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/;
  return ipv4Regex.test(ip) || ipv6Regex.test(ip);
};
