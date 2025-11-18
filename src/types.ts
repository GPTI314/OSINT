/**
 * Type definitions for the web crawler engine
 */

export enum CrawlStrategy {
  BFS = 'breadth-first',
  DFS = 'depth-first'
}

export enum LinkType {
  ANCHOR = 'anchor',
  IMAGE = 'image',
  SCRIPT = 'script',
  STYLESHEET = 'stylesheet',
  FRAME = 'frame',
  FORM_ACTION = 'form-action',
  JAVASCRIPT = 'javascript',
  OTHER = 'other'
}

export interface CrawlOptions {
  // Strategy
  strategy?: CrawlStrategy;
  maxDepth?: number;
  maxPages?: number;

  // Domain restrictions
  allowedDomains?: string[];
  blockedDomains?: string[];
  stayInDomain?: boolean;

  // URL patterns
  urlPatterns?: RegExp[];
  excludePatterns?: RegExp[];

  // Content filtering
  allowedMimeTypes?: string[];
  blockedMimeTypes?: string[];

  // Politeness
  delayMs?: number;
  maxConcurrent?: number;
  userAgent?: string;
  respectRobotsTxt?: boolean;

  // Features
  followSitemaps?: boolean;
  extractForms?: boolean;
  extractJsLinks?: boolean;

  // Resume capability
  resumable?: boolean;
  stateDir?: string;

  // Distributed crawling
  workerId?: string;
  totalWorkers?: number;

  // Callbacks
  onPage?: (result: CrawlResult) => void | Promise<void>;
  onError?: (error: CrawlError) => void | Promise<void>;
  onComplete?: (stats: CrawlStats) => void | Promise<void>;
}

export interface CrawlResult {
  url: string;
  normalizedUrl: string;
  depth: number;
  statusCode: number;
  contentType: string;
  content: string;
  links: ExtractedLink[];
  forms: FormInfo[];
  headers: Record<string, string>;
  timestamp: Date;
  loadTime: number;
  fromUrl?: string;
}

export interface ExtractedLink {
  url: string;
  normalizedUrl: string;
  type: LinkType;
  text?: string;
  attributes?: Record<string, string>;
}

export interface FormInfo {
  action: string;
  method: string;
  inputs: FormInput[];
  attributes?: Record<string, string>;
}

export interface FormInput {
  name: string;
  type: string;
  value?: string;
  required?: boolean;
  attributes?: Record<string, string>;
}

export interface CrawlError {
  url: string;
  error: Error;
  timestamp: Date;
  depth: number;
}

export interface CrawlStats {
  totalPages: number;
  successfulPages: number;
  failedPages: number;
  totalLinks: number;
  totalForms: number;
  startTime: Date;
  endTime?: Date;
  duration?: number;
  avgLoadTime: number;
}

export interface RobotsInfo {
  isAllowed: (url: string, userAgent: string) => boolean;
  getCrawlDelay: (userAgent: string) => number | undefined;
  getSitemaps: () => string[];
}

export interface CrawlState {
  version: string;
  options: CrawlOptions;
  stats: CrawlStats;
  visited: string[];
  queue: QueueItem[];
  errors: CrawlError[];
  timestamp: Date;
}

export interface QueueItem {
  url: string;
  depth: number;
  fromUrl?: string;
  hash: string;
}

export interface SitemapUrl {
  loc: string;
  lastmod?: string;
  changefreq?: string;
  priority?: number;
}
