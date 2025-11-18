/**
 * URL partitioner for distributed crawling
 */

import * as crypto from 'crypto';

export class UrlPartitioner {
  private readonly workerId: string;
  private readonly totalWorkers: number;

  constructor(workerId: string, totalWorkers: number) {
    this.workerId = workerId;
    this.totalWorkers = totalWorkers;
  }

  /**
   * Check if this worker should process the given URL
   */
  shouldProcess(url: string): boolean {
    const partition = this.getPartition(url);
    const workerIndex = this.getWorkerIndex();
    return partition === workerIndex;
  }

  /**
   * Get partition number for a URL (0 to totalWorkers-1)
   */
  private getPartition(url: string): number {
    // Use consistent hashing to assign URLs to partitions
    const hash = crypto.createHash('md5').update(url).digest('hex');
    // Convert first 8 characters of hash to integer
    const hashInt = parseInt(hash.substring(0, 8), 16);
    return hashInt % this.totalWorkers;
  }

  /**
   * Get this worker's index
   */
  private getWorkerIndex(): number {
    // Parse worker ID to get index (e.g., "worker-0", "worker-1")
    const match = this.workerId.match(/\d+$/);
    if (match) {
      return parseInt(match[0], 10) % this.totalWorkers;
    }
    // Fallback: hash the worker ID
    const hash = crypto.createHash('md5').update(this.workerId).digest('hex');
    const hashInt = parseInt(hash.substring(0, 8), 16);
    return hashInt % this.totalWorkers;
  }

  /**
   * Get worker ID
   */
  getWorkerId(): string {
    return this.workerId;
  }

  /**
   * Get total workers
   */
  getTotalWorkers(): number {
    return this.totalWorkers;
  }

  /**
   * Get partition statistics
   */
  getPartitionStats(urls: string[]): Record<number, number> {
    const stats: Record<number, number> = {};

    for (let i = 0; i < this.totalWorkers; i++) {
      stats[i] = 0;
    }

    for (const url of urls) {
      const partition = this.getPartition(url);
      stats[partition]++;
    }

    return stats;
  }
}
