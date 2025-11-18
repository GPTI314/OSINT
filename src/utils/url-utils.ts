/**
 * URL normalization and duplicate detection utilities
 */

import * as crypto from 'crypto';
import * as url from 'url';

export class UrlUtils {
  /**
   * Normalize a URL to prevent duplicate crawling of the same resource
   */
  static normalize(urlString: string, baseUrl?: string): string {
    try {
      // Resolve relative URLs
      const parsedUrl = new URL(urlString, baseUrl);

      // Convert protocol and hostname to lowercase
      parsedUrl.protocol = parsedUrl.protocol.toLowerCase();
      parsedUrl.hostname = parsedUrl.hostname.toLowerCase();

      // Remove default ports
      if (
        (parsedUrl.protocol === 'http:' && parsedUrl.port === '80') ||
        (parsedUrl.protocol === 'https:' && parsedUrl.port === '443')
      ) {
        parsedUrl.port = '';
      }

      // Remove fragment (hash)
      parsedUrl.hash = '';

      // Sort query parameters
      if (parsedUrl.search) {
        const params = new URLSearchParams(parsedUrl.search);
        const sortedParams = new URLSearchParams(
          Array.from(params.entries()).sort(([a], [b]) => a.localeCompare(b))
        );
        parsedUrl.search = sortedParams.toString();
      }

      // Remove trailing slash from path (except for root)
      if (parsedUrl.pathname !== '/' && parsedUrl.pathname.endsWith('/')) {
        parsedUrl.pathname = parsedUrl.pathname.slice(0, -1);
      }

      // Remove index files
      parsedUrl.pathname = parsedUrl.pathname.replace(
        /\/(index|default)\.(html?|php|asp|aspx|jsp)$/i,
        ''
      );

      return parsedUrl.toString();
    } catch (error) {
      throw new Error(`Failed to normalize URL "${urlString}": ${error}`);
    }
  }

  /**
   * Generate a hash for a URL for duplicate detection
   */
  static hash(urlString: string): string {
    return crypto.createHash('sha256').update(urlString).digest('hex');
  }

  /**
   * Check if a URL belongs to a specific domain
   */
  static isSameDomain(url1: string, url2: string): boolean {
    try {
      const parsed1 = new URL(url1);
      const parsed2 = new URL(url2);
      return parsed1.hostname === parsed2.hostname;
    } catch {
      return false;
    }
  }

  /**
   * Check if a URL matches any of the allowed domains
   */
  static matchesDomain(urlString: string, domains: string[]): boolean {
    try {
      const parsed = new URL(urlString);
      return domains.some((domain) => {
        // Support wildcard subdomains
        if (domain.startsWith('*.')) {
          const baseDomain = domain.slice(2);
          return (
            parsed.hostname === baseDomain ||
            parsed.hostname.endsWith('.' + baseDomain)
          );
        }
        return parsed.hostname === domain;
      });
    } catch {
      return false;
    }
  }

  /**
   * Check if a URL matches any of the patterns
   */
  static matchesPattern(urlString: string, patterns: RegExp[]): boolean {
    return patterns.some((pattern) => pattern.test(urlString));
  }

  /**
   * Extract domain from URL
   */
  static getDomain(urlString: string): string {
    try {
      const parsed = new URL(urlString);
      return parsed.hostname;
    } catch {
      return '';
    }
  }

  /**
   * Check if URL is absolute
   */
  static isAbsolute(urlString: string): boolean {
    try {
      new URL(urlString);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Resolve relative URL against base URL
   */
  static resolve(baseUrl: string, relativeUrl: string): string {
    try {
      return new URL(relativeUrl, baseUrl).toString();
    } catch (error) {
      throw new Error(
        `Failed to resolve URL "${relativeUrl}" against base "${baseUrl}": ${error}`
      );
    }
  }

  /**
   * Check if URL is valid HTTP/HTTPS
   */
  static isValidHttpUrl(urlString: string): boolean {
    try {
      const parsed = new URL(urlString);
      return parsed.protocol === 'http:' || parsed.protocol === 'https:';
    } catch {
      return false;
    }
  }

  /**
   * Get URL without query string and fragment
   */
  static getBaseUrl(urlString: string): string {
    try {
      const parsed = new URL(urlString);
      parsed.search = '';
      parsed.hash = '';
      return parsed.toString();
    } catch {
      return urlString;
    }
  }
}
