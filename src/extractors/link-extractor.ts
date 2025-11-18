/**
 * Link extractor for HTML, CSS, and JavaScript
 */

import * as cheerio from 'cheerio';
import { ExtractedLink, LinkType } from '../types';
import { UrlUtils } from '../utils/url-utils';

export class LinkExtractor {
  /**
   * Extract all links from HTML content
   */
  static extractLinks(
    html: string,
    baseUrl: string,
    extractJsLinks: boolean = false
  ): ExtractedLink[] {
    const links: ExtractedLink[] = [];
    const $ = cheerio.load(html);

    // Extract anchor links
    $('a[href]').each((_, elem) => {
      const href = $(elem).attr('href');
      if (href) {
        try {
          const absoluteUrl = UrlUtils.resolve(baseUrl, href);
          if (UrlUtils.isValidHttpUrl(absoluteUrl)) {
            links.push({
              url: absoluteUrl,
              normalizedUrl: UrlUtils.normalize(absoluteUrl),
              type: LinkType.ANCHOR,
              text: $(elem).text().trim(),
              attributes: this.getAttributes(elem),
            });
          }
        } catch {
          // Skip invalid URLs
        }
      }
    });

    // Extract image sources
    $('img[src]').each((_, elem) => {
      const src = $(elem).attr('src');
      if (src) {
        try {
          const absoluteUrl = UrlUtils.resolve(baseUrl, src);
          if (UrlUtils.isValidHttpUrl(absoluteUrl)) {
            links.push({
              url: absoluteUrl,
              normalizedUrl: UrlUtils.normalize(absoluteUrl),
              type: LinkType.IMAGE,
              attributes: this.getAttributes(elem),
            });
          }
        } catch {
          // Skip invalid URLs
        }
      }
    });

    // Extract script sources
    $('script[src]').each((_, elem) => {
      const src = $(elem).attr('src');
      if (src) {
        try {
          const absoluteUrl = UrlUtils.resolve(baseUrl, src);
          if (UrlUtils.isValidHttpUrl(absoluteUrl)) {
            links.push({
              url: absoluteUrl,
              normalizedUrl: UrlUtils.normalize(absoluteUrl),
              type: LinkType.SCRIPT,
              attributes: this.getAttributes(elem),
            });
          }
        } catch {
          // Skip invalid URLs
        }
      }
    });

    // Extract stylesheet links
    $('link[rel="stylesheet"][href]').each((_, elem) => {
      const href = $(elem).attr('href');
      if (href) {
        try {
          const absoluteUrl = UrlUtils.resolve(baseUrl, href);
          if (UrlUtils.isValidHttpUrl(absoluteUrl)) {
            links.push({
              url: absoluteUrl,
              normalizedUrl: UrlUtils.normalize(absoluteUrl),
              type: LinkType.STYLESHEET,
              attributes: this.getAttributes(elem),
            });
          }
        } catch {
          // Skip invalid URLs
        }
      }
    });

    // Extract other link tags
    $('link[href]:not([rel="stylesheet"])').each((_, elem) => {
      const href = $(elem).attr('href');
      if (href) {
        try {
          const absoluteUrl = UrlUtils.resolve(baseUrl, href);
          if (UrlUtils.isValidHttpUrl(absoluteUrl)) {
            links.push({
              url: absoluteUrl,
              normalizedUrl: UrlUtils.normalize(absoluteUrl),
              type: LinkType.OTHER,
              attributes: this.getAttributes(elem),
            });
          }
        } catch {
          // Skip invalid URLs
        }
      }
    });

    // Extract frame sources
    $('iframe[src], frame[src]').each((_, elem) => {
      const src = $(elem).attr('src');
      if (src) {
        try {
          const absoluteUrl = UrlUtils.resolve(baseUrl, src);
          if (UrlUtils.isValidHttpUrl(absoluteUrl)) {
            links.push({
              url: absoluteUrl,
              normalizedUrl: UrlUtils.normalize(absoluteUrl),
              type: LinkType.FRAME,
              attributes: this.getAttributes(elem),
            });
          }
        } catch {
          // Skip invalid URLs
        }
      }
    });

    // Extract JavaScript links if enabled
    if (extractJsLinks) {
      const jsLinks = this.extractJavaScriptLinks(html, baseUrl);
      links.push(...jsLinks);
    }

    return links;
  }

  /**
   * Extract links from JavaScript code
   */
  private static extractJavaScriptLinks(
    html: string,
    baseUrl: string
  ): ExtractedLink[] {
    const links: ExtractedLink[] = [];

    // Common patterns for URLs in JavaScript
    const patterns = [
      // String literals with URLs
      /(["'])((https?:)?\/\/[^"']+)\1/g,
      // window.location assignments
      /window\.location(?:\.href)?\s*=\s*(["'])([^"']+)\1/g,
      // fetch/ajax calls
      /(?:fetch|ajax|get|post)\s*\(\s*(["'])([^"']+)\1/g,
    ];

    for (const pattern of patterns) {
      let match;
      while ((match = pattern.exec(html)) !== null) {
        const potentialUrl = match[2];
        try {
          let absoluteUrl;
          if (potentialUrl.startsWith('//')) {
            const parsedBase = new URL(baseUrl);
            absoluteUrl = `${parsedBase.protocol}${potentialUrl}`;
          } else if (potentialUrl.startsWith('http')) {
            absoluteUrl = potentialUrl;
          } else {
            absoluteUrl = UrlUtils.resolve(baseUrl, potentialUrl);
          }

          if (UrlUtils.isValidHttpUrl(absoluteUrl)) {
            links.push({
              url: absoluteUrl,
              normalizedUrl: UrlUtils.normalize(absoluteUrl),
              type: LinkType.JAVASCRIPT,
            });
          }
        } catch {
          // Skip invalid URLs
        }
      }
    }

    return links;
  }

  /**
   * Get all attributes from an element
   */
  private static getAttributes(elem: any): Record<string, string> {
    const attributes: Record<string, string> = {};
    const attribs = elem.attribs || {};

    for (const [key, value] of Object.entries(attribs)) {
      attributes[key] = value as string;
    }

    return attributes;
  }
}
