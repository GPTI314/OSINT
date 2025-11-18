/**
 * Core web crawler with BFS and DFS strategies
 */

import axios, { AxiosResponse } from 'axios';
import {
  CrawlOptions,
  CrawlResult,
  CrawlError,
  CrawlStats,
  CrawlStrategy,
  QueueItem,
  CrawlState,
} from '../types';
import { UrlUtils } from '../utils/url-utils';
import { DelayManager } from '../utils/delay-manager';
import { ContentFilter } from '../utils/content-filter';
import { RobotsParser } from '../parsers/robots-parser';
import { SitemapParser } from '../parsers/sitemap-parser';
import { LinkExtractor } from '../extractors/link-extractor';
import { FormExtractor } from '../extractors/form-extractor';
import { StateManager } from '../utils/state-manager';
import { UrlPartitioner } from '../workers/url-partitioner';

export class WebCrawler {
  private options: Required<CrawlOptions>;
  private queue: QueueItem[] = [];
  private visited: Set<string> = new Set();
  private stats: CrawlStats;
  private delayManager: DelayManager;
  private contentFilter: ContentFilter;
  private robotsParser: RobotsParser;
  private sitemapParser: SitemapParser;
  private stateManager?: StateManager;
  private urlPartitioner?: UrlPartitioner;
  private running: boolean = false;
  private concurrentRequests: number = 0;

  constructor(options: CrawlOptions = {}) {
    this.options = this.normalizeOptions(options);
    this.delayManager = new DelayManager(this.options.delayMs);
    this.contentFilter = new ContentFilter(
      this.options.allowedMimeTypes,
      this.options.blockedMimeTypes
    );
    this.robotsParser = new RobotsParser(this.options.userAgent);
    this.sitemapParser = new SitemapParser(this.options.userAgent);

    // Initialize state manager if resumable
    if (this.options.resumable) {
      this.stateManager = new StateManager(
        this.options.stateDir,
        this.options.workerId || 'default'
      );
    }

    // Initialize URL partitioner if distributed
    if (this.options.totalWorkers > 1) {
      this.urlPartitioner = new UrlPartitioner(
        this.options.workerId,
        this.options.totalWorkers
      );
    }

    this.stats = {
      totalPages: 0,
      successfulPages: 0,
      failedPages: 0,
      totalLinks: 0,
      totalForms: 0,
      startTime: new Date(),
      avgLoadTime: 0,
    };
  }

  /**
   * Start crawling from a seed URL
   */
  async crawl(seedUrl: string): Promise<CrawlStats> {
    this.running = true;
    this.stats.startTime = new Date();

    try {
      // Try to resume from saved state
      if (this.options.resumable && this.stateManager) {
        const resumed = await this.resumeCrawl();
        if (resumed) {
          console.log('Resuming crawl from saved state');
        }
      }

      // If not resumed, initialize new crawl
      if (this.queue.length === 0) {
        await this.initializeCrawl(seedUrl);
      }

      // Start crawling
      await this.processCrawl();

      // Mark completion
      this.stats.endTime = new Date();
      this.stats.duration =
        this.stats.endTime.getTime() - this.stats.startTime.getTime();

      // Call completion callback
      if (this.options.onComplete) {
        await this.options.onComplete(this.stats);
      }

      // Clear state if successful
      if (this.options.resumable && this.stateManager) {
        await this.stateManager.clearState();
      }

      return this.stats;
    } catch (error) {
      console.error('Crawl error:', error);
      throw error;
    } finally {
      this.running = false;
    }
  }

  /**
   * Initialize crawl with seed URL and optional sitemap URLs
   */
  private async initializeCrawl(seedUrl: string): Promise<void> {
    const normalizedUrl = UrlUtils.normalize(seedUrl);

    // Add seed URL to queue
    this.addToQueue({
      url: seedUrl,
      depth: 0,
      hash: UrlUtils.hash(normalizedUrl),
    });

    // Load sitemap URLs if enabled
    if (this.options.followSitemaps) {
      try {
        const robotsSitemaps = await this.robotsParser.getSitemaps(seedUrl);
        const sitemapUrls = await this.sitemapParser.getAllUrls(
          seedUrl,
          robotsSitemaps
        );

        for (const sitemapUrl of sitemapUrls) {
          this.addToQueue({
            url: sitemapUrl.loc,
            depth: 0,
            hash: UrlUtils.hash(UrlUtils.normalize(sitemapUrl.loc)),
          });
        }

        console.log(`Loaded ${sitemapUrls.length} URLs from sitemaps`);
      } catch (error) {
        console.error('Failed to load sitemaps:', error);
      }
    }
  }

  /**
   * Process crawl queue
   */
  private async processCrawl(): Promise<void> {
    while (this.running && this.queue.length > 0) {
      // Check if max pages reached
      if (this.stats.totalPages >= this.options.maxPages) {
        console.log('Max pages reached');
        break;
      }

      // Wait if too many concurrent requests
      while (this.concurrentRequests >= this.options.maxConcurrent) {
        await this.sleep(100);
      }

      // Get next URL from queue based on strategy
      const item = this.getNextQueueItem();
      if (!item) continue;

      // Process URL
      this.concurrentRequests++;
      this.processUrl(item)
        .catch((error) => {
          console.error(`Error processing ${item.url}:`, error);
        })
        .finally(() => {
          this.concurrentRequests--;
        });

      // Save checkpoint periodically
      if (
        this.options.resumable &&
        this.stateManager &&
        this.stats.totalPages % 100 === 0
      ) {
        await this.stateManager.saveCheckpoint(
          this.visited,
          this.queue,
          this.stats
        );
      }
    }

    // Wait for all concurrent requests to complete
    while (this.concurrentRequests > 0) {
      await this.sleep(100);
    }
  }

  /**
   * Process a single URL
   */
  private async processUrl(item: QueueItem): Promise<void> {
    const { url, depth } = item;

    try {
      // Mark as visited
      const normalizedUrl = UrlUtils.normalize(url);
      this.visited.add(normalizedUrl);

      // Check robots.txt
      if (this.options.respectRobotsTxt) {
        const allowed = await this.robotsParser.isAllowed(url);
        if (!allowed) {
          console.log(`Blocked by robots.txt: ${url}`);
          return;
        }

        // Get crawl delay from robots.txt
        const robotsDelay = await this.robotsParser.getCrawlDelay(url);
        const delay = robotsDelay
          ? robotsDelay * 1000
          : this.options.delayMs;

        // Wait for politeness delay
        const domain = UrlUtils.getDomain(url);
        await this.delayManager.waitForDomain(domain, delay);
      } else {
        // Wait for configured delay
        const domain = UrlUtils.getDomain(url);
        await this.delayManager.waitForDomain(domain);
      }

      // Fetch the page
      const startTime = Date.now();
      const response = await this.fetchUrl(url);
      const loadTime = Date.now() - startTime;

      // Check content type
      const contentType = response.headers['content-type'] || '';
      if (!this.contentFilter.isAllowed(contentType)) {
        console.log(`Filtered by content type: ${url} (${contentType})`);
        return;
      }

      // Extract content
      const content = response.data;

      // Extract links
      const links = LinkExtractor.extractLinks(
        content,
        url,
        this.options.extractJsLinks
      );

      // Extract forms
      const forms = this.options.extractForms
        ? FormExtractor.extractForms(content, url)
        : [];

      // Add form action links
      if (this.options.extractForms) {
        const formLinks = FormExtractor.extractFormLinks(content, url);
        links.push(...formLinks);
      }

      // Create result
      const result: CrawlResult = {
        url,
        normalizedUrl,
        depth,
        statusCode: response.status,
        contentType,
        content,
        links,
        forms,
        headers: response.headers as Record<string, string>,
        timestamp: new Date(),
        loadTime,
        fromUrl: item.fromUrl,
      };

      // Update stats
      this.stats.totalPages++;
      this.stats.successfulPages++;
      this.stats.totalLinks += links.length;
      this.stats.totalForms += forms.length;
      this.stats.avgLoadTime =
        (this.stats.avgLoadTime * (this.stats.totalPages - 1) + loadTime) /
        this.stats.totalPages;

      // Call page callback
      if (this.options.onPage) {
        await this.options.onPage(result);
      }

      // Add discovered links to queue
      if (depth < this.options.maxDepth) {
        for (const link of links) {
          this.addToQueue({
            url: link.url,
            depth: depth + 1,
            fromUrl: url,
            hash: UrlUtils.hash(link.normalizedUrl),
          });
        }
      }
    } catch (error) {
      this.stats.totalPages++;
      this.stats.failedPages++;

      const crawlError: CrawlError = {
        url,
        error: error as Error,
        timestamp: new Date(),
        depth,
      };

      if (this.options.onError) {
        await this.options.onError(crawlError);
      }
    }
  }

  /**
   * Fetch URL with axios
   */
  private async fetchUrl(url: string): Promise<AxiosResponse> {
    return await axios.get(url, {
      timeout: 30000,
      maxRedirects: 5,
      headers: {
        'User-Agent': this.options.userAgent,
      },
      validateStatus: (status) => status >= 200 && status < 400,
    });
  }

  /**
   * Add URL to queue
   */
  private addToQueue(item: QueueItem): void {
    const normalizedUrl = UrlUtils.normalize(item.url);

    // Check if already visited
    if (this.visited.has(normalizedUrl)) {
      return;
    }

    // Check if already in queue
    if (this.queue.some((q) => q.hash === item.hash)) {
      return;
    }

    // Check domain restrictions
    if (this.options.stayInDomain) {
      const seedDomain = this.queue.length > 0 ? this.queue[0].url : item.url;
      if (!UrlUtils.isSameDomain(item.url, seedDomain)) {
        return;
      }
    }

    if (this.options.allowedDomains.length > 0) {
      if (!UrlUtils.matchesDomain(item.url, this.options.allowedDomains)) {
        return;
      }
    }

    if (this.options.blockedDomains.length > 0) {
      if (UrlUtils.matchesDomain(item.url, this.options.blockedDomains)) {
        return;
      }
    }

    // Check URL patterns
    if (this.options.urlPatterns.length > 0) {
      if (!UrlUtils.matchesPattern(item.url, this.options.urlPatterns)) {
        return;
      }
    }

    if (this.options.excludePatterns.length > 0) {
      if (UrlUtils.matchesPattern(item.url, this.options.excludePatterns)) {
        return;
      }
    }

    // Check distributed crawling
    if (this.urlPartitioner && !this.urlPartitioner.shouldProcess(item.url)) {
      return;
    }

    this.queue.push(item);
  }

  /**
   * Get next item from queue based on strategy
   */
  private getNextQueueItem(): QueueItem | undefined {
    if (this.queue.length === 0) return undefined;

    if (this.options.strategy === CrawlStrategy.DFS) {
      // Depth-first: take from end (stack)
      return this.queue.pop();
    } else {
      // Breadth-first: take from beginning (queue)
      return this.queue.shift();
    }
  }

  /**
   * Resume crawl from saved state
   */
  private async resumeCrawl(): Promise<boolean> {
    if (!this.stateManager) return false;

    const state = await this.stateManager.loadState();
    if (!state) return false;

    this.visited = new Set(state.visited);
    this.queue = state.queue;
    this.stats = state.stats;

    return true;
  }

  /**
   * Stop crawling
   */
  stop(): void {
    this.running = false;
  }

  /**
   * Get current statistics
   */
  getStats(): CrawlStats {
    return { ...this.stats };
  }

  /**
   * Sleep helper
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Normalize options with defaults
   */
  private normalizeOptions(options: CrawlOptions): Required<CrawlOptions> {
    return {
      strategy: options.strategy || CrawlStrategy.BFS,
      maxDepth: options.maxDepth ?? 3,
      maxPages: options.maxPages ?? 1000,
      allowedDomains: options.allowedDomains || [],
      blockedDomains: options.blockedDomains || [],
      stayInDomain: options.stayInDomain ?? false,
      urlPatterns: options.urlPatterns || [],
      excludePatterns: options.excludePatterns || [],
      allowedMimeTypes: options.allowedMimeTypes || ContentFilter.PRESETS.CRAWLABLE,
      blockedMimeTypes: options.blockedMimeTypes || [],
      delayMs: options.delayMs ?? 1000,
      maxConcurrent: options.maxConcurrent ?? 5,
      userAgent: options.userAgent || 'OSINT-Crawler/1.0',
      respectRobotsTxt: options.respectRobotsTxt ?? true,
      followSitemaps: options.followSitemaps ?? false,
      extractForms: options.extractForms ?? false,
      extractJsLinks: options.extractJsLinks ?? false,
      resumable: options.resumable ?? false,
      stateDir: options.stateDir || '.crawl-state',
      workerId: options.workerId || 'worker-0',
      totalWorkers: options.totalWorkers ?? 1,
      onPage: options.onPage,
      onError: options.onError,
      onComplete: options.onComplete,
    };
  }
}
