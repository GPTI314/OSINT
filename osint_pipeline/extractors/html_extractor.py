"""
HTML data extractor with CSS selectors, XPath, and regex support
"""
from typing import Any, Dict, List, Optional, Union
from bs4 import BeautifulSoup
from lxml import etree, html
import re
import requests
from datetime import datetime


class HTMLExtractor:
    """Extract data from HTML using CSS selectors, XPath, and regex"""

    def __init__(self, parser: str = 'lxml'):
        """
        Initialize HTML extractor

        Args:
            parser: BeautifulSoup parser to use (lxml, html.parser, etc.)
        """
        self.parser = parser

    def extract(self, source: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """
        Extract data from HTML source

        Args:
            source: HTML string, bytes, or URL
            **kwargs: Additional extraction options

        Returns:
            Extracted data dictionary
        """
        # Handle URL source
        if isinstance(source, str) and source.startswith(('http://', 'https://')):
            html_content = self._fetch_url(source)
        else:
            html_content = source

        soup = BeautifulSoup(html_content, self.parser)
        tree = html.fromstring(str(soup))

        extracted_data = {
            'source_type': 'html',
            'extracted_at': datetime.utcnow().isoformat(),
            'url': source if isinstance(source, str) and source.startswith('http') else None,
            'title': self.extract_title(soup),
            'metadata': self.extract_metadata(soup),
            'links': self.extract_links(soup),
            'images': self.extract_images(soup),
            'text': self.extract_text(soup),
            'custom_data': {}
        }

        # Apply custom selectors if provided
        if 'css_selectors' in kwargs:
            extracted_data['custom_data']['css'] = self.extract_with_css(
                soup, kwargs['css_selectors']
            )

        if 'xpath_queries' in kwargs:
            extracted_data['custom_data']['xpath'] = self.extract_with_xpath(
                tree, kwargs['xpath_queries']
            )

        if 'regex_patterns' in kwargs:
            extracted_data['custom_data']['regex'] = self.extract_with_regex(
                str(soup), kwargs['regex_patterns']
            )

        return extracted_data

    def _fetch_url(self, url: str, timeout: int = 10) -> str:
        """
        Fetch HTML content from URL

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds

        Returns:
            HTML content as string
        """
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text

    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else None

    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract meta tags and metadata"""
        metadata = {}

        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content

        # Extract Open Graph tags
        og_tags = {}
        for meta in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
            property_name = meta.get('property')
            content = meta.get('content')
            if property_name and content:
                og_tags[property_name] = content

        if og_tags:
            metadata['open_graph'] = og_tags

        # Extract Twitter Card tags
        twitter_tags = {}
        for meta in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
            name = meta.get('name')
            content = meta.get('content')
            if name and content:
                twitter_tags[name] = content

        if twitter_tags:
            metadata['twitter'] = twitter_tags

        return metadata

    def extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all links from HTML"""
        links = []

        for a_tag in soup.find_all('a', href=True):
            links.append({
                'url': a_tag['href'],
                'text': a_tag.get_text(strip=True),
                'title': a_tag.get('title', '')
            })

        return links

    def extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all images from HTML"""
        images = []

        for img_tag in soup.find_all('img'):
            images.append({
                'src': img_tag.get('src', ''),
                'alt': img_tag.get('alt', ''),
                'title': img_tag.get('title', ''),
                'width': img_tag.get('width', ''),
                'height': img_tag.get('height', '')
            })

        return images

    def extract_text(self, soup: BeautifulSoup) -> str:
        """Extract all visible text from HTML"""
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()

        text = soup.get_text(separator=' ', strip=True)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)

        return text

    def extract_with_css(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract data using CSS selectors

        Args:
            soup: BeautifulSoup object
            selectors: Dictionary mapping field names to CSS selectors

        Returns:
            Extracted data dictionary
        """
        results = {}

        for field_name, selector in selectors.items():
            elements = soup.select(selector)

            if len(elements) == 1:
                results[field_name] = elements[0].get_text(strip=True)
            elif len(elements) > 1:
                results[field_name] = [el.get_text(strip=True) for el in elements]
            else:
                results[field_name] = None

        return results

    def extract_with_xpath(self, tree: etree.Element, queries: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract data using XPath queries

        Args:
            tree: lxml HTML tree
            queries: Dictionary mapping field names to XPath queries

        Returns:
            Extracted data dictionary
        """
        results = {}

        for field_name, query in queries.items():
            try:
                elements = tree.xpath(query)

                if isinstance(elements, list):
                    if len(elements) == 1:
                        element = elements[0]
                        if isinstance(element, str):
                            results[field_name] = element
                        else:
                            results[field_name] = element.text_content() if hasattr(element, 'text_content') else str(element)
                    elif len(elements) > 1:
                        results[field_name] = [
                            el.text_content() if hasattr(el, 'text_content') else str(el)
                            for el in elements
                        ]
                    else:
                        results[field_name] = None
                else:
                    results[field_name] = str(elements)

            except Exception as e:
                results[field_name] = f"Error: {str(e)}"

        return results

    def extract_with_regex(self, html_content: str, patterns: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract data using regex patterns

        Args:
            html_content: HTML content as string
            patterns: Dictionary mapping field names to regex patterns

        Returns:
            Extracted data dictionary
        """
        results = {}

        for field_name, pattern in patterns.items():
            try:
                matches = re.findall(pattern, html_content)

                if len(matches) == 1:
                    results[field_name] = matches[0]
                elif len(matches) > 1:
                    results[field_name] = matches
                else:
                    results[field_name] = None

            except Exception as e:
                results[field_name] = f"Error: {str(e)}"

        return results

    def extract_tables(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        """
        Extract all tables from HTML

        Returns:
            List of tables, where each table is a list of rows,
            and each row is a list of cell values
        """
        tables = []

        for table in soup.find_all('table'):
            table_data = []

            for row in table.find_all('tr'):
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    row_data.append(cell.get_text(strip=True))
                table_data.append(row_data)

            tables.append(table_data)

        return tables

    def extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract form information from HTML

        Returns:
            List of form dictionaries with action, method, and fields
        """
        forms = []

        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'fields': []
            }

            for input_tag in form.find_all(['input', 'textarea', 'select']):
                field = {
                    'name': input_tag.get('name', ''),
                    'type': input_tag.get('type', 'text'),
                    'value': input_tag.get('value', ''),
                    'required': input_tag.has_attr('required')
                }
                form_data['fields'].append(field)

            forms.append(form_data)

        return forms
