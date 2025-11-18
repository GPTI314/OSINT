/**
 * Robots.txt parser and compliance checker
 */

import axios from 'axios';
import * as robotsParser from 'robots-parser';
import { RobotsInfo } from '../types';
import { UrlUtils } from '../utils/url-utils';

export class RobotsParser {
  private cache: Map<string, RobotsInfo> = new Map();
  private readonly userAgent: string;

  constructor(userAgent: string = 'OSINT-Crawler/1.0') {
    this.userAgent = userAgent;
  }

  /**
   * Get robots.txt information for a domain
   */
  async getRobotsInfo(urlString: string): Promise<RobotsInfo> {
    const domain = UrlUtils.getDomain(urlString);

    // Check cache
    if (this.cache.has(domain)) {
      return this.cache.get(domain)!;
    }

    try {
      const robotsUrl = this.getRobotsUrl(urlString);
      const response = await axios.get(robotsUrl, {
        timeout: 10000,
        headers: {
          'User-Agent': this.userAgent,
        },
        validateStatus: (status) => status === 200 || status === 404,
      });

      let robotsTxt = '';
      if (response.status === 200) {
        robotsTxt = response.data;
      }

      const robots = robotsParser(robotsUrl, robotsTxt);

      const robotsInfo: RobotsInfo = {
        isAllowed: (url: string, userAgent: string = this.userAgent) => {
          return robots.isAllowed(url, userAgent) ?? true;
        },
        getCrawlDelay: (userAgent: string = this.userAgent) => {
          return robots.getCrawlDelay(userAgent);
        },
        getSitemaps: () => {
          return robots.getSitemaps();
        },
      };

      this.cache.set(domain, robotsInfo);
      return robotsInfo;
    } catch (error) {
      // If we can't fetch robots.txt, assume everything is allowed
      const permissiveRobots: RobotsInfo = {
        isAllowed: () => true,
        getCrawlDelay: () => undefined,
        getSitemaps: () => [],
      };

      this.cache.set(domain, permissiveRobots);
      return permissiveRobots;
    }
  }

  /**
   * Check if a URL is allowed to be crawled
   */
  async isAllowed(urlString: string, userAgent?: string): Promise<boolean> {
    const robotsInfo = await this.getRobotsInfo(urlString);
    return robotsInfo.isAllowed(urlString, userAgent || this.userAgent);
  }

  /**
   * Get crawl delay for a URL
   */
  async getCrawlDelay(urlString: string, userAgent?: string): Promise<number | undefined> {
    const robotsInfo = await this.getRobotsInfo(urlString);
    return robotsInfo.getCrawlDelay(userAgent || this.userAgent);
  }

  /**
   * Get sitemaps from robots.txt
   */
  async getSitemaps(urlString: string): Promise<string[]> {
    const robotsInfo = await this.getRobotsInfo(urlString);
    return robotsInfo.getSitemaps();
  }

  /**
   * Get robots.txt URL for a given URL
   */
  private getRobotsUrl(urlString: string): string {
    const parsed = new URL(urlString);
    return `${parsed.protocol}//${parsed.host}/robots.txt`;
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }
}
