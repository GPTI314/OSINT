/**
 * Politeness delay manager for respectful crawling
 */

export class DelayManager {
  private lastAccessTime: Map<string, number> = new Map();
  private readonly defaultDelay: number;

  constructor(defaultDelayMs: number = 1000) {
    this.defaultDelay = defaultDelayMs;
  }

  /**
   * Wait for appropriate delay before accessing a domain
   */
  async waitForDomain(domain: string, customDelay?: number): Promise<void> {
    const delay = customDelay ?? this.defaultDelay;
    const lastAccess = this.lastAccessTime.get(domain);

    if (lastAccess) {
      const timeSinceLastAccess = Date.now() - lastAccess;
      const remainingDelay = delay - timeSinceLastAccess;

      if (remainingDelay > 0) {
        await this.sleep(remainingDelay);
      }
    }

    this.lastAccessTime.set(domain, Date.now());
  }

  /**
   * Sleep for specified milliseconds
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Clear all delay records
   */
  clear(): void {
    this.lastAccessTime.clear();
  }

  /**
   * Get last access time for a domain
   */
  getLastAccessTime(domain: string): number | undefined {
    return this.lastAccessTime.get(domain);
  }
}
