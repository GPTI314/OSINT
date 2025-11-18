/**
 * Content filtering based on MIME types
 */

import * as mime from 'mime-types';

export class ContentFilter {
  private readonly allowedTypes: Set<string>;
  private readonly blockedTypes: Set<string>;

  constructor(allowedTypes?: string[], blockedTypes?: string[]) {
    this.allowedTypes = new Set(allowedTypes || []);
    this.blockedTypes = new Set(blockedTypes || []);
  }

  /**
   * Check if a content type is allowed
   */
  isAllowed(contentType: string): boolean {
    const normalizedType = this.normalizeContentType(contentType);

    // If blocked types are specified, check if content is blocked
    if (this.blockedTypes.size > 0) {
      if (this.isBlocked(normalizedType)) {
        return false;
      }
    }

    // If allowed types are specified, check if content is allowed
    if (this.allowedTypes.size > 0) {
      return this.isInAllowedList(normalizedType);
    }

    // If no restrictions specified, allow all non-blocked types
    return true;
  }

  /**
   * Check if content type is blocked
   */
  private isBlocked(contentType: string): boolean {
    const type = contentType.toLowerCase();

    // Check exact match
    if (this.blockedTypes.has(type)) {
      return true;
    }

    // Check wildcard match (e.g., "image/*")
    const [category] = type.split('/');
    if (this.blockedTypes.has(`${category}/*`)) {
      return true;
    }

    return false;
  }

  /**
   * Check if content type is in allowed list
   */
  private isInAllowedList(contentType: string): boolean {
    const type = contentType.toLowerCase();

    // Check exact match
    if (this.allowedTypes.has(type)) {
      return true;
    }

    // Check wildcard match (e.g., "text/*")
    const [category] = type.split('/');
    if (this.allowedTypes.has(`${category}/*`)) {
      return true;
    }

    return false;
  }

  /**
   * Normalize content type (remove charset and other parameters)
   */
  private normalizeContentType(contentType: string): string {
    return contentType.split(';')[0].trim().toLowerCase();
  }

  /**
   * Get MIME type from URL extension
   */
  static getMimeTypeFromUrl(url: string): string | null {
    try {
      const parsed = new URL(url);
      const pathname = parsed.pathname;
      return mime.lookup(pathname) || null;
    } catch {
      return null;
    }
  }

  /**
   * Check if URL extension suggests crawlable content
   */
  static isCrawlableExtension(url: string): boolean {
    const crawlableExtensions = [
      '.html',
      '.htm',
      '.php',
      '.asp',
      '.aspx',
      '.jsp',
      '.do',
      '.action',
      '', // No extension
    ];

    try {
      const parsed = new URL(url);
      const pathname = parsed.pathname;
      const extension = pathname.substring(pathname.lastIndexOf('.')).toLowerCase();

      // If no extension or crawlable extension
      if (!extension || crawlableExtensions.includes(extension)) {
        return true;
      }

      return false;
    } catch {
      return false;
    }
  }

  /**
   * Common MIME type presets
   */
  static readonly PRESETS = {
    HTML_ONLY: ['text/html', 'application/xhtml+xml'],
    TEXT_TYPES: ['text/*'],
    IMAGES: ['image/*'],
    DOCUMENTS: [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ],
    CRAWLABLE: [
      'text/html',
      'application/xhtml+xml',
      'text/plain',
      'application/xml',
      'text/xml',
    ],
  };
}
