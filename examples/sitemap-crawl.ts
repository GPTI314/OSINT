/**
 * Sitemap-based crawling example
 */

import { WebCrawler, SitemapParser } from '../src';

async function sitemapCrawl() {
  const sitemapParser = new SitemapParser();

  // First, get all URLs from sitemaps
  console.log('Discovering sitemaps...');
  const sitemapUrls = await sitemapParser.getAllUrls('https://example.com');
  console.log(`Found ${sitemapUrls.length} URLs in sitemaps`);

  // Filter URLs by priority or change frequency if needed
  const highPriorityUrls = sitemapUrls.filter(
    (url) => !url.priority || url.priority >= 0.5
  );
  console.log(`High priority URLs: ${highPriorityUrls.length}`);

  // Create crawler with sitemap integration
  const crawler = new WebCrawler({
    maxDepth: 1, // Don't follow links, just crawl sitemap URLs
    maxPages: 500,
    delayMs: 1000,
    followSitemaps: true, // Automatically load sitemaps
    respectRobotsTxt: true,

    onPage: async (result) => {
      console.log(`Crawled: ${result.url} (${result.statusCode})`);
    },

    onComplete: async (stats) => {
      console.log('\nSitemap crawl complete!');
      console.log(`Pages: ${stats.successfulPages}/${stats.totalPages}`);
    },
  });

  await crawler.crawl('https://example.com');
}

sitemapCrawl().catch(console.error);
