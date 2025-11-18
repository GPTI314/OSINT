"""
HTML extraction examples
"""
from osint_pipeline.extractors import HTMLExtractor


def example_basic_extraction():
    """Basic HTML extraction"""
    print("=" * 60)
    print("Example 1: Basic HTML Extraction")
    print("=" * 60)

    html_content = """
    <html>
        <head>
            <title>Sample Page</title>
            <meta name="description" content="A sample page for testing">
            <meta property="og:title" content="Sample Page">
        </head>
        <body>
            <h1>Welcome to the Sample Page</h1>
            <p>This is a sample paragraph with <a href="https://example.com">a link</a>.</p>
            <img src="image.jpg" alt="Sample Image">
        </body>
    </html>
    """

    extractor = HTMLExtractor()
    data = extractor.extract(html_content)

    print(f"Title: {data['title']}")
    print(f"Links found: {len(data['links'])}")
    print(f"Images found: {len(data['images'])}")
    print(f"Text preview: {data['text'][:100]}...")


def example_css_selectors():
    """Extract data using CSS selectors"""
    print("\n" + "=" * 60)
    print("Example 2: CSS Selector Extraction")
    print("=" * 60)

    html_content = """
    <html>
        <body>
            <div class="article">
                <h2 class="title">Article Title</h2>
                <p class="author">By John Doe</p>
                <div class="content">Article content goes here...</div>
            </div>
        </body>
    </html>
    """

    extractor = HTMLExtractor()

    css_selectors = {
        'title': '.title',
        'author': '.author',
        'content': '.content'
    }

    data = extractor.extract(html_content, css_selectors=css_selectors)

    print("Extracted data using CSS selectors:")
    for key, value in data['custom_data']['css'].items():
        print(f"{key}: {value}")


def example_xpath_queries():
    """Extract data using XPath"""
    print("\n" + "=" * 60)
    print("Example 3: XPath Extraction")
    print("=" * 60)

    html_content = """
    <html>
        <body>
            <table>
                <tr>
                    <td>Name</td>
                    <td>Age</td>
                </tr>
                <tr>
                    <td>John</td>
                    <td>30</td>
                </tr>
            </table>
        </body>
    </html>
    """

    extractor = HTMLExtractor()

    xpath_queries = {
        'table_rows': '//tr',
        'first_cell': '//tr[2]/td[1]/text()',
        'all_cells': '//td/text()'
    }

    data = extractor.extract(html_content, xpath_queries=xpath_queries)

    print("Extracted data using XPath:")
    for key, value in data['custom_data']['xpath'].items():
        print(f"{key}: {value}")


def example_regex_patterns():
    """Extract data using regex patterns"""
    print("\n" + "=" * 60)
    print("Example 4: Regex Pattern Extraction")
    print("=" * 60)

    html_content = """
    <html>
        <body>
            <p>Contact us at info@example.com or support@example.org</p>
            <p>Phone: 555-123-4567 or 555-987-6543</p>
        </body>
    </html>
    """

    extractor = HTMLExtractor()

    regex_patterns = {
        'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phones': r'\d{3}-\d{3}-\d{4}'
    }

    data = extractor.extract(html_content, regex_patterns=regex_patterns)

    print("Extracted data using regex:")
    for key, value in data['custom_data']['regex'].items():
        print(f"{key}: {value}")


if __name__ == '__main__':
    example_basic_extraction()
    example_css_selectors()
    example_xpath_queries()
    example_regex_patterns()
