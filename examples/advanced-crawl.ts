/**
 * Advanced web crawling with all features
 */

import { WebCrawler, CrawlStrategy, ContentFilter } from '../src';
import * as fs from 'fs';

async function advancedCrawl() {
  const results: any[] = [];

  const crawler = new WebCrawler({
    // Strategy configuration
    strategy: CrawlStrategy.DFS,
    maxDepth: 3,
    maxPages: 100,

    // Domain restrictions
    allowedDomains: ['example.com', '*.example.com'],
    blockedDomains: ['ads.example.com'],
    stayInDomain: false,

    // URL filtering
    urlPatterns: [/\/articles\//, /\/blog\//],
    excludePatterns: [/\.(jpg|png|gif|pdf)$/i],

    // Content filtering
    allowedMimeTypes: ContentFilter.PRESETS.CRAWLABLE,

    // Politeness
    delayMs: 2000,
    maxConcurrent: 3,
    userAgent: 'OSINT-Research-Bot/1.0',
    respectRobotsTxt: true,

    // Advanced features
    followSitemaps: true,
    extractForms: true,
    extractJsLinks: true,

    // Resume capability
    resumable: true,
    stateDir: '.crawl-state',

    // Callbacks
    onPage: async (result) => {
      console.log(`[${result.depth}] ${result.url}`);

      // Save page data
      results.push({
        url: result.url,
        depth: result.depth,
        title: extractTitle(result.content),
        links: result.links.length,
        forms: result.forms.length,
        statusCode: result.statusCode,
        loadTime: result.loadTime,
      });

      // Log forms found
      if (result.forms.length > 0) {
        console.log(`  Found ${result.forms.length} forms:`);
        result.forms.forEach((form) => {
          console.log(`    - ${form.method} ${form.action}`);
        });
      }
    },

    onError: async (error) => {
      console.error(`[ERROR] ${error.url}: ${error.error.message}`);
    },

    onComplete: async (stats) => {
      console.log('\n=== Crawl Complete ===');
      console.log(`Duration: ${stats.duration}ms`);
      console.log(`Pages crawled: ${stats.successfulPages}/${stats.totalPages}`);
      console.log(`Links discovered: ${stats.totalLinks}`);
      console.log(`Forms discovered: ${stats.totalForms}`);
      console.log(`Avg load time: ${stats.avgLoadTime.toFixed(2)}ms`);

      // Save results to JSON
      fs.writeFileSync(
        'crawl-results.json',
        JSON.stringify(results, null, 2)
      );
      console.log('\nResults saved to crawl-results.json');
    },
  });

  try {
    await crawler.crawl('https://example.com');
  } catch (error) {
    console.error('Crawl failed:', error);
  }
}

function extractTitle(html: string): string {
  const match = html.match(/<title[^>]*>([^<]+)<\/title>/i);
  return match ? match[1].trim() : '';
}

advancedCrawl().catch(console.error);
