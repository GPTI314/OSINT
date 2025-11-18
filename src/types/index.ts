// Common types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'analyst' | 'viewer';
  avatar?: string;
  createdAt: string;
  lastLogin?: string;
}

export interface Investigation {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'completed' | 'archived';
  priority: 'low' | 'medium' | 'high' | 'critical';
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  tags: string[];
  targetCount: number;
  findingCount: number;
}

export interface Target {
  id: string;
  investigationId: string;
  type: 'person' | 'organization' | 'domain' | 'ip' | 'email' | 'phone' | 'social' | 'other';
  value: string;
  label?: string;
  status: 'active' | 'inactive';
  riskScore?: number;
  tags: string[];
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface ScrapingJob {
  id: string;
  name: string;
  targetId: string;
  url: string;
  type: 'single' | 'list' | 'sitemap';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
  progress: number;
  itemsCollected: number;
  startedAt?: string;
  completedAt?: string;
  error?: string;
  config: {
    maxDepth: number;
    maxPages: number;
    timeout: number;
    selectors?: string[];
  };
}

export interface CrawlingSession {
  id: string;
  name: string;
  targetId: string;
  seedUrl: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
  progress: number;
  pagesDiscovered: number;
  pagesCrawled: number;
  startedAt?: string;
  completedAt?: string;
  config: {
    maxDepth: number;
    maxPages: number;
    followExternal: boolean;
    respectRobots: boolean;
  };
}

export interface IntelligenceData {
  id: string;
  type: 'domain' | 'ip' | 'email' | 'phone' | 'social' | 'image';
  value: string;
  targetId?: string;
  source: string;
  confidence: number;
  data: Record<string, any>;
  relatedEntities: string[];
  createdAt: string;
  updatedAt: string;
}

export interface Finding {
  id: string;
  investigationId: string;
  title: string;
  description: string;
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical';
  status: 'new' | 'investigating' | 'confirmed' | 'false_positive' | 'resolved';
  category: string;
  targetIds: string[];
  evidence: Evidence[];
  assignedTo?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Evidence {
  id: string;
  type: 'text' | 'image' | 'url' | 'file' | 'data';
  content: string;
  description?: string;
  source?: string;
  timestamp: string;
}

export interface Report {
  id: string;
  investigationId: string;
  title: string;
  type: 'summary' | 'detailed' | 'executive' | 'technical';
  status: 'draft' | 'review' | 'final';
  sections: ReportSection[];
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  exportedAt?: string;
}

export interface ReportSection {
  id: string;
  title: string;
  content: string;
  type: 'text' | 'table' | 'chart' | 'findings' | 'timeline';
  order: number;
  data?: any;
}

export interface CorrelationNode {
  id: string;
  type: string;
  label: string;
  data: any;
  x?: number;
  y?: number;
}

export interface CorrelationEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  type: string;
  weight?: number;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  type: string;
  title: string;
  description: string;
  targetId?: string;
  metadata?: Record<string, any>;
}

export interface Statistics {
  investigations: {
    total: number;
    active: number;
    completed: number;
  };
  targets: {
    total: number;
    byType: Record<string, number>;
  };
  findings: {
    total: number;
    bySeverity: Record<string, number>;
  };
  dataCollected: {
    totalRecords: number;
    recentActivity: number;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface SearchFilters {
  query?: string;
  status?: string[];
  type?: string[];
  dateFrom?: string;
  dateTo?: string;
  tags?: string[];
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}
