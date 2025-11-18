# OSINT Web Crawler Engine

Open-Source Intelligence (OSINT) toolkit: modular collectors, enrichment pipeline, link analysis, risk scoring, and investigative workflow automation.

## Web Crawler Engine

An intelligent, feature-rich web crawler designed for OSINT investigations with advanced capabilities for reconnaissance, data collection, and web analysis.

## Features

### Core Crawling Components

- **Multiple Crawling Strategies**
  - Breadth-First Search (BFS) - crawl level by level
  - Depth-First Search (DFS) - crawl deep into each path

- **Domain Restrictions and Filtering**
  - Allow/block specific domains
  - Wildcard domain matching (`*.example.com`)
  - Stay within origin domain option

- **Pattern Matching**
  - URL pattern filtering with regex
  - Exclude patterns to avoid unwanted content

- **Duplicate Detection**
  - URL normalization (protocol, domain, path, query params)
  - Hash-based duplicate detection
  - Efficient visited URL tracking

- **Politeness and Rate Limiting**
  - Configurable delays between requests
  - Per-domain request throttling
  - Concurrent request limiting

- **Robots.txt Compliance**
  - Automatic robots.txt parsing
  - Respect crawl delays
  - Respect disallow rules

### Advanced Features

- **Sitemap Integration**
  - Automatic sitemap discovery
  - XML sitemap parsing
  - Sitemap index support
  - Priority and frequency-based filtering

- **Content Filtering**
  - MIME type filtering
  - Extension-based filtering
  - Configurable allow/block lists

- **Link Extraction**
  - HTML anchor tags
  - Images, scripts, stylesheets
  - Frames and iframes
  - Form actions
  - JavaScript-embedded URLs

- **Form Discovery**
  - Complete form extraction
  - Input field analysis
  - Form action URL extraction
  - Method detection (GET/POST)

- **Resume Capability**
  - Persistent crawl state
  - Automatic checkpointing
  - Resume interrupted crawls
  - State recovery

- **Distributed Crawling**
  - Multi-worker support
  - Consistent URL partitioning
  - Worker coordination
  - Scalable architecture

## Installation

```bash
npm install
npm run build
```

## Quick Start

```typescript
import { WebCrawler, CrawlStrategy } from '@osint/web-crawler';

const crawler = new WebCrawler({
  strategy: CrawlStrategy.BFS,
  maxDepth: 2,
  maxPages: 50,
  delayMs: 1000,
  respectRobotsTxt: true,

  onPage: async (result) => {
    console.log(`Crawled: ${result.url}`);
    console.log(`Links: ${result.links.length}`);
  }
});

await crawler.crawl('https://example.com');
```

## Configuration Options

### Basic Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `strategy` | `CrawlStrategy` | `BFS` | Crawling strategy (BFS or DFS) |
| `maxDepth` | `number` | `3` | Maximum crawl depth |
| `maxPages` | `number` | `1000` | Maximum pages to crawl |
| `delayMs` | `number` | `1000` | Delay between requests (ms) |
| `maxConcurrent` | `number` | `5` | Maximum concurrent requests |
| `userAgent` | `string` | `OSINT-Crawler/1.0` | User agent string |

### Domain Restrictions

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `allowedDomains` | `string[]` | `[]` | Whitelist of domains to crawl |
| `blockedDomains` | `string[]` | `[]` | Blacklist of domains to avoid |
| `stayInDomain` | `boolean` | `false` | Only crawl the starting domain |

### URL Filtering

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `urlPatterns` | `RegExp[]` | `[]` | Regex patterns URLs must match |
| `excludePatterns` | `RegExp[]` | `[]` | Regex patterns to exclude |

### Content Filtering

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `allowedMimeTypes` | `string[]` | `CRAWLABLE` | Allowed MIME types |
| `blockedMimeTypes` | `string[]` | `[]` | Blocked MIME types |

### Advanced Features

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `respectRobotsTxt` | `boolean` | `true` | Respect robots.txt rules |
| `followSitemaps` | `boolean` | `false` | Crawl URLs from sitemaps |
| `extractForms` | `boolean` | `false` | Extract form information |
| `extractJsLinks` | `boolean` | `false` | Extract links from JavaScript |
| `resumable` | `boolean` | `false` | Enable crawl resumption |
| `stateDir` | `string` | `.crawl-state` | Directory for state files |

### Distributed Crawling

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `workerId` | `string` | `worker-0` | Unique worker identifier |
| `totalWorkers` | `number` | `1` | Total number of workers |

### Callbacks

| Option | Type | Description |
|--------|------|-------------|
| `onPage` | `(result: CrawlResult) => void` | Called for each crawled page |
| `onError` | `(error: CrawlError) => void` | Called when errors occur |
| `onComplete` | `(stats: CrawlStats) => void` | Called when crawl completes |

## Examples

### Basic Crawl

See `examples/basic-crawl.ts`:

```typescript
const crawler = new WebCrawler({
  maxDepth: 2,
  maxPages: 50,
  stayInDomain: true,

  onPage: async (result) => {
    console.log(`${result.url} - ${result.links.length} links`);
  }
});

await crawler.crawl('https://example.com');
```

### Advanced Crawl with All Features

See `examples/advanced-crawl.ts`:

```typescript
const crawler = new WebCrawler({
  strategy: CrawlStrategy.DFS,
  maxDepth: 3,
  allowedDomains: ['example.com', '*.example.com'],
  urlPatterns: [/\/articles\//, /\/blog\//],
  followSitemaps: true,
  extractForms: true,
  extractJsLinks: true,
  resumable: true,
  // ... more options
});
```

### Distributed Crawling

See `examples/distributed-crawl.ts`:

```bash
# Terminal 1
node examples/distributed-crawl.js worker-0 4

# Terminal 2
node examples/distributed-crawl.js worker-1 4

# Terminal 3
node examples/distributed-crawl.js worker-2 4

# Terminal 4
node examples/distributed-crawl.js worker-3 4
```

### Sitemap-Based Crawling

See `examples/sitemap-crawl.ts`:

```typescript
const crawler = new WebCrawler({
  followSitemaps: true,
  maxDepth: 1,
  // ... more options
});
```

## API Reference

### WebCrawler

Main crawler class.

#### Methods

- `crawl(seedUrl: string): Promise<CrawlStats>` - Start crawling from seed URL
- `stop(): void` - Stop the crawler
- `getStats(): CrawlStats` - Get current statistics

### UrlUtils

URL normalization and manipulation utilities.

#### Methods

- `normalize(url: string): string` - Normalize URL
- `hash(url: string): string` - Generate URL hash
- `isSameDomain(url1: string, url2: string): boolean` - Check domain match
- `matchesDomain(url: string, domains: string[]): boolean` - Check domain list
- `matchesPattern(url: string, patterns: RegExp[]): boolean` - Check pattern match

### LinkExtractor

Extract links from HTML content.

#### Methods

- `extractLinks(html: string, baseUrl: string, extractJsLinks?: boolean): ExtractedLink[]`

### FormExtractor

Extract forms from HTML content.

#### Methods

- `extractForms(html: string, baseUrl: string): FormInfo[]`
- `extractFormLinks(html: string, baseUrl: string): ExtractedLink[]`

### SitemapParser

Parse XML sitemaps.

#### Methods

- `parseSitemap(url: string): Promise<SitemapUrl[]>`
- `discoverSitemaps(baseUrl: string): Promise<string[]>`
- `getAllUrls(baseUrl: string, robotsSitemaps?: string[]): Promise<SitemapUrl[]>`

### RobotsParser

Parse and check robots.txt compliance.

#### Methods

- `getRobotsInfo(url: string): Promise<RobotsInfo>`
- `isAllowed(url: string, userAgent?: string): Promise<boolean>`
- `getCrawlDelay(url: string, userAgent?: string): Promise<number | undefined>`
- `getSitemaps(url: string): Promise<string[]>`

## Architecture

```
src/
├── core/
│   └── crawler.ts          # Main crawler implementation
├── utils/
│   ├── url-utils.ts        # URL normalization & hashing
│   ├── delay-manager.ts    # Politeness delays
│   ├── content-filter.ts   # MIME type filtering
│   └── state-manager.ts    # Crawl state persistence
├── parsers/
│   ├── robots-parser.ts    # robots.txt parsing
│   └── sitemap-parser.ts   # XML sitemap parsing
├── extractors/
│   ├── link-extractor.ts   # Link extraction
│   └── form-extractor.ts   # Form extraction
├── workers/
│   └── url-partitioner.ts  # Distributed crawling
└── types.ts                # TypeScript type definitions
```

## Best Practices

### Respectful Crawling

1. Always respect `robots.txt` unless you have explicit permission
2. Use appropriate delays (1000ms minimum recommended)
3. Set a descriptive user agent
4. Limit concurrent requests
5. Don't crawl too deep or too many pages

### Performance Optimization

1. Use appropriate `maxConcurrent` setting (3-5 recommended)
2. Enable content filtering to skip unwanted files
3. Use URL patterns to focus on relevant content
4. Consider distributed crawling for large sites
5. Enable resume capability for long crawls

### Error Handling

1. Always implement `onError` callback
2. Monitor failed pages ratio
3. Check `robots.txt` compliance issues
4. Handle network timeouts gracefully

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Disclaimer

This tool is for legitimate OSINT research and authorized security testing only. Always:
- Obtain proper authorization before crawling
- Respect website terms of service
- Follow robots.txt guidelines
- Use appropriate rate limiting
- Comply with applicable laws and regulations
