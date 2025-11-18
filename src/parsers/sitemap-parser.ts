/**
 * Sitemap parser for XML sitemaps
 */

import axios from 'axios';
import { XMLParser } from 'fast-xml-parser';
import { SitemapUrl } from '../types';
import { UrlUtils } from '../utils/url-utils';

export class SitemapParser {
  private readonly userAgent: string;
  private readonly parser: XMLParser;

  constructor(userAgent: string = 'OSINT-Crawler/1.0') {
    this.userAgent = userAgent;
    this.parser = new XMLParser({
      ignoreAttributes: false,
      attributeNamePrefix: '@_',
    });
  }

  /**
   * Parse sitemap from URL
   */
  async parseSitemap(sitemapUrl: string): Promise<SitemapUrl[]> {
    try {
      const response = await axios.get(sitemapUrl, {
        timeout: 15000,
        headers: {
          'User-Agent': this.userAgent,
        },
      });

      const xmlData = response.data;
      const parsed = this.parser.parse(xmlData);

      // Handle sitemap index
      if (parsed.sitemapindex) {
        return await this.parseSitemapIndex(parsed.sitemapindex, sitemapUrl);
      }

      // Handle regular sitemap
      if (parsed.urlset) {
        return this.parseUrlSet(parsed.urlset);
      }

      return [];
    } catch (error) {
      console.error(`Failed to parse sitemap ${sitemapUrl}:`, error);
      return [];
    }
  }

  /**
   * Parse sitemap index (contains references to other sitemaps)
   */
  private async parseSitemapIndex(
    sitemapIndex: any,
    baseUrl: string
  ): Promise<SitemapUrl[]> {
    const urls: SitemapUrl[] = [];
    const sitemaps = Array.isArray(sitemapIndex.sitemap)
      ? sitemapIndex.sitemap
      : [sitemapIndex.sitemap];

    for (const sitemap of sitemaps) {
      if (sitemap.loc) {
        const sitemapUrl = UrlUtils.resolve(baseUrl, sitemap.loc);
        const sitemapUrls = await this.parseSitemap(sitemapUrl);
        urls.push(...sitemapUrls);
      }
    }

    return urls;
  }

  /**
   * Parse URL set from sitemap
   */
  private parseUrlSet(urlset: any): SitemapUrl[] {
    const urls: SitemapUrl[] = [];
    const urlEntries = Array.isArray(urlset.url) ? urlset.url : [urlset.url];

    for (const entry of urlEntries) {
      if (entry && entry.loc) {
        const url: SitemapUrl = {
          loc: entry.loc,
          lastmod: entry.lastmod,
          changefreq: entry.changefreq,
          priority: entry.priority ? parseFloat(entry.priority) : undefined,
        };
        urls.push(url);
      }
    }

    return urls;
  }

  /**
   * Discover sitemap URLs for a domain
   */
  async discoverSitemaps(baseUrl: string): Promise<string[]> {
    const sitemaps: string[] = [];
    const parsed = new URL(baseUrl);
    const origin = `${parsed.protocol}//${parsed.host}`;

    // Common sitemap locations
    const commonLocations = [
      '/sitemap.xml',
      '/sitemap_index.xml',
      '/sitemap-index.xml',
      '/sitemap1.xml',
      '/sitemap/sitemap.xml',
    ];

    for (const location of commonLocations) {
      try {
        const sitemapUrl = origin + location;
        const response = await axios.head(sitemapUrl, {
          timeout: 5000,
          headers: {
            'User-Agent': this.userAgent,
          },
          validateStatus: (status) => status === 200,
        });

        if (response.status === 200) {
          sitemaps.push(sitemapUrl);
        }
      } catch {
        // Sitemap doesn't exist at this location
      }
    }

    return sitemaps;
  }

  /**
   * Get all URLs from sitemaps (including from robots.txt)
   */
  async getAllUrls(
    baseUrl: string,
    robotsSitemaps: string[] = []
  ): Promise<SitemapUrl[]> {
    const allUrls: SitemapUrl[] = [];
    const sitemapUrls = new Set<string>();

    // Add sitemaps from robots.txt
    robotsSitemaps.forEach((url) => sitemapUrls.add(url));

    // Discover additional sitemaps
    const discovered = await this.discoverSitemaps(baseUrl);
    discovered.forEach((url) => sitemapUrls.add(url));

    // Parse all sitemaps
    for (const sitemapUrl of sitemapUrls) {
      const urls = await this.parseSitemap(sitemapUrl);
      allUrls.push(...urls);
    }

    return allUrls;
  }
}
