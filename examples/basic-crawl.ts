/**
 * Basic web crawling example
 */

import { WebCrawler, CrawlStrategy } from '../src';

async function basicCrawl() {
  const crawler = new WebCrawler({
    strategy: CrawlStrategy.BFS,
    maxDepth: 2,
    maxPages: 50,
    delayMs: 1000,
    respectRobotsTxt: true,
    stayInDomain: true,

    onPage: async (result) => {
      console.log(`Crawled: ${result.url}`);
      console.log(`  Status: ${result.statusCode}`);
      console.log(`  Links found: ${result.links.length}`);
      console.log(`  Forms found: ${result.forms.length}`);
    },

    onError: async (error) => {
      console.error(`Error crawling ${error.url}:`, error.error.message);
    },

    onComplete: async (stats) => {
      console.log('\nCrawl complete!');
      console.log(`Total pages: ${stats.totalPages}`);
      console.log(`Successful: ${stats.successfulPages}`);
      console.log(`Failed: ${stats.failedPages}`);
      console.log(`Total links: ${stats.totalLinks}`);
      console.log(`Average load time: ${stats.avgLoadTime}ms`);
    },
  });

  const stats = await crawler.crawl('https://example.com');
  console.log('Final stats:', stats);
}

basicCrawl().catch(console.error);
