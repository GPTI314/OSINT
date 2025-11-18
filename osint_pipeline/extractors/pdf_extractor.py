"""
PDF data extractor for text, metadata, and structure
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import io


class PDFExtractor:
    """Extract data from PDF files"""

    def __init__(self):
        """Initialize PDF extractor"""
        pass

    def extract(self, source: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """
        Extract data from PDF

        Args:
            source: PDF file path or bytes
            **kwargs: Additional extraction options

        Returns:
            Extracted data dictionary
        """
        extracted_data = {
            'source_type': 'pdf',
            'extracted_at': datetime.utcnow().isoformat(),
            'source_path': source if isinstance(source, str) else None,
            'metadata': {},
            'pages': [],
            'text': '',
            'custom_data': {}
        }

        try:
            # Try PyPDF2 first
            extracted_data.update(self._extract_with_pypdf2(source, **kwargs))
        except Exception as e:
            extracted_data['pypdf2_error'] = str(e)

            # Fallback to pdfplumber
            try:
                extracted_data.update(self._extract_with_pdfplumber(source, **kwargs))
            except Exception as e2:
                extracted_data['pdfplumber_error'] = str(e2)

        return extracted_data

    def _extract_with_pypdf2(self, source: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """
        Extract using PyPDF2

        Args:
            source: PDF file path or bytes
            **kwargs: Extraction options

        Returns:
            Extracted data
        """
        from PyPDF2 import PdfReader

        # Open PDF
        if isinstance(source, bytes):
            reader = PdfReader(io.BytesIO(source))
        else:
            reader = PdfReader(source)

        # Extract metadata
        metadata = {}
        if reader.metadata:
            for key, value in reader.metadata.items():
                metadata[key.replace('/', '')] = str(value)

        # Extract text from pages
        pages = []
        full_text = []

        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            pages.append({
                'page_number': i + 1,
                'text': page_text,
                'char_count': len(page_text),
                'word_count': len(page_text.split())
            })
            full_text.append(page_text)

        return {
            'metadata': metadata,
            'pages': pages,
            'text': '\n'.join(full_text),
            'page_count': len(reader.pages),
            'is_encrypted': reader.is_encrypted
        }

    def _extract_with_pdfplumber(self, source: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """
        Extract using pdfplumber (better for tables and layout)

        Args:
            source: PDF file path or bytes
            **kwargs: Extraction options

        Returns:
            Extracted data
        """
        import pdfplumber

        # Open PDF
        if isinstance(source, bytes):
            pdf = pdfplumber.open(io.BytesIO(source))
        else:
            pdf = pdfplumber.open(source)

        # Extract metadata
        metadata = pdf.metadata or {}

        # Extract text and tables from pages
        pages = []
        full_text = []
        all_tables = []

        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ''
            page_tables = page.extract_tables() if kwargs.get('extract_tables', True) else []

            page_data = {
                'page_number': i + 1,
                'text': page_text,
                'char_count': len(page_text),
                'word_count': len(page_text.split()),
                'width': page.width,
                'height': page.height
            }

            if page_tables:
                page_data['tables'] = page_tables
                all_tables.extend(page_tables)

            pages.append(page_data)
            full_text.append(page_text)

        pdf.close()

        result = {
            'metadata': metadata,
            'pages': pages,
            'text': '\n'.join(full_text),
            'page_count': len(pages)
        }

        if all_tables:
            result['tables'] = all_tables
            result['table_count'] = len(all_tables)

        return result

    def extract_metadata(self, source: Union[str, bytes]) -> Dict[str, Any]:
        """
        Extract PDF metadata only

        Args:
            source: PDF file path or bytes

        Returns:
            Metadata dictionary
        """
        try:
            from PyPDF2 import PdfReader

            if isinstance(source, bytes):
                reader = PdfReader(io.BytesIO(source))
            else:
                reader = PdfReader(source)

            metadata = {}
            if reader.metadata:
                for key, value in reader.metadata.items():
                    metadata[key.replace('/', '')] = str(value)

            metadata['page_count'] = len(reader.pages)
            metadata['is_encrypted'] = reader.is_encrypted

            return metadata

        except Exception as e:
            return {'error': str(e)}

    def extract_text_by_page(self, source: Union[str, bytes], page_numbers: List[int]) -> Dict[int, str]:
        """
        Extract text from specific pages

        Args:
            source: PDF file path or bytes
            page_numbers: List of page numbers (1-indexed)

        Returns:
            Dictionary mapping page numbers to text
        """
        try:
            from PyPDF2 import PdfReader

            if isinstance(source, bytes):
                reader = PdfReader(io.BytesIO(source))
            else:
                reader = PdfReader(source)

            results = {}
            for page_num in page_numbers:
                if 1 <= page_num <= len(reader.pages):
                    page = reader.pages[page_num - 1]
                    results[page_num] = page.extract_text()

            return results

        except Exception as e:
            return {'error': str(e)}

    def extract_links(self, source: Union[str, bytes]) -> List[Dict[str, Any]]:
        """
        Extract links from PDF

        Args:
            source: PDF file path or bytes

        Returns:
            List of link dictionaries
        """
        try:
            from PyPDF2 import PdfReader

            if isinstance(source, bytes):
                reader = PdfReader(io.BytesIO(source))
            else:
                reader = PdfReader(source)

            links = []

            for page_num, page in enumerate(reader.pages, 1):
                if '/Annots' in page:
                    annotations = page['/Annots']

                    for annotation in annotations:
                        obj = annotation.get_object()
                        if obj.get('/Subtype') == '/Link':
                            link_data = {
                                'page': page_num,
                                'type': 'link'
                            }

                            if '/A' in obj:
                                action = obj['/A']
                                if '/URI' in action:
                                    link_data['uri'] = action['/URI']

                            links.append(link_data)

            return links

        except Exception as e:
            return [{'error': str(e)}]

    def extract_images(self, source: Union[str, bytes]) -> List[Dict[str, Any]]:
        """
        Extract images from PDF

        Args:
            source: PDF file path or bytes

        Returns:
            List of image dictionaries
        """
        try:
            from PyPDF2 import PdfReader

            if isinstance(source, bytes):
                reader = PdfReader(io.BytesIO(source))
            else:
                reader = PdfReader(source)

            images = []

            for page_num, page in enumerate(reader.pages, 1):
                if '/XObject' in page['/Resources']:
                    xobjects = page['/Resources']['/XObject'].get_object()

                    for obj_name in xobjects:
                        obj = xobjects[obj_name]

                        if obj['/Subtype'] == '/Image':
                            image_data = {
                                'page': page_num,
                                'name': obj_name,
                                'width': obj.get('/Width'),
                                'height': obj.get('/Height'),
                                'color_space': str(obj.get('/ColorSpace', 'Unknown')),
                                'bits_per_component': obj.get('/BitsPerComponent')
                            }
                            images.append(image_data)

            return images

        except Exception as e:
            return [{'error': str(e)}]

    def extract_structure(self, source: Union[str, bytes]) -> Dict[str, Any]:
        """
        Extract PDF document structure

        Args:
            source: PDF file path or bytes

        Returns:
            Structure dictionary
        """
        try:
            from PyPDF2 import PdfReader

            if isinstance(source, bytes):
                reader = PdfReader(io.BytesIO(source))
            else:
                reader = PdfReader(source)

            structure = {
                'page_count': len(reader.pages),
                'is_encrypted': reader.is_encrypted,
                'pages': []
            }

            for i, page in enumerate(reader.pages):
                page_info = {
                    'page_number': i + 1,
                    'width': float(page.mediabox.width),
                    'height': float(page.mediabox.height),
                    'rotation': page.get('/Rotate', 0)
                }

                # Check for resources
                if '/Resources' in page:
                    resources = page['/Resources']
                    page_info['has_fonts'] = '/Font' in resources
                    page_info['has_images'] = '/XObject' in resources

                structure['pages'].append(page_info)

            return structure

        except Exception as e:
            return {'error': str(e)}
