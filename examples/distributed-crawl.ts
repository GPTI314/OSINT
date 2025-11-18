/**
 * Distributed crawling example
 * Run multiple instances of this script with different worker IDs
 */

import { WebCrawler, CrawlStrategy } from '../src';

async function distributedCrawl(workerId: string, totalWorkers: number) {
  console.log(`Starting worker ${workerId} of ${totalWorkers}`);

  const crawler = new WebCrawler({
    strategy: CrawlStrategy.BFS,
    maxDepth: 3,
    maxPages: 1000,
    delayMs: 1000,
    maxConcurrent: 5,

    // Distributed crawling configuration
    workerId,
    totalWorkers,

    // Resume capability
    resumable: true,
    stateDir: '.crawl-state',

    onPage: async (result) => {
      console.log(`[${workerId}] Crawled: ${result.url}`);
    },

    onError: async (error) => {
      console.error(`[${workerId}] Error: ${error.url}`);
    },

    onComplete: async (stats) => {
      console.log(`\n[${workerId}] Complete: ${stats.successfulPages} pages`);
    },
  });

  await crawler.crawl('https://example.com');
}

// Get worker ID from command line arguments
const workerId = process.argv[2] || 'worker-0';
const totalWorkers = parseInt(process.argv[3] || '1', 10);

distributedCrawl(workerId, totalWorkers).catch(console.error);

// Usage:
// node distributed-crawl.js worker-0 4
// node distributed-crawl.js worker-1 4
// node distributed-crawl.js worker-2 4
// node distributed-crawl.js worker-3 4
