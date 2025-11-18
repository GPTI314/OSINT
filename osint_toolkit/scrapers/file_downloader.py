"""
File Downloader
Downloads files (PDFs, images, documents) with progress tracking and validation
"""

import os
from typing import Optional, Dict, List, Callable
from pathlib import Path
from urllib.parse import urlparse, unquote
import mimetypes
import hashlib
import asyncio
from loguru import logger
from tqdm import tqdm

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("python-magic not installed")

from .base_scraper import BaseScraper, AsyncBaseScraper


class FileDownloader(BaseScraper):
    """
    File downloader with progress tracking and validation
    """

    def __init__(
        self,
        download_dir: str = "./downloads",
        chunk_size: int = 8192,
        verify_mime_type: bool = True,
        **kwargs
    ):
        """
        Initialize file downloader.

        Args:
            download_dir: Directory to save downloaded files
            chunk_size: Download chunk size in bytes
            verify_mime_type: Verify file MIME type after download
            **kwargs: Arguments for BaseScraper
        """
        super().__init__(**kwargs)
        self.download_dir = Path(download_dir)
        self.chunk_size = chunk_size
        self.verify_mime_type = verify_mime_type

        # Create download directory
        self.download_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized FileDownloader (download_dir={download_dir})")

    def scrape(
        self,
        url: str,
        filename: Optional[str] = None,
        progress: bool = True,
        **kwargs
    ) -> str:
        """
        Download a file.

        Args:
            url: URL of file to download
            filename: Custom filename (auto-detected if not provided)
            progress: Show progress bar
            **kwargs: Additional request arguments

        Returns:
            Path to downloaded file
        """
        try:
            # Get filename if not provided
            if not filename:
                filename = self._get_filename_from_url(url)

            filepath = self.download_dir / filename

            logger.info(f"Downloading {url} to {filepath}")

            # Make request
            response = self.get(url, stream=True, **kwargs)
            response.raise_for_status()

            # Get total file size
            total_size = int(response.headers.get('content-length', 0))

            # Download with progress bar
            if progress and total_size > 0:
                with open(filepath, 'wb') as f:
                    with tqdm(
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        desc=filename
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=self.chunk_size):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
            else:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            f.write(chunk)

            logger.info(f"Downloaded {filename} ({self._format_size(filepath.stat().st_size)})")

            # Verify MIME type
            if self.verify_mime_type:
                self._verify_file_type(filepath, url)

            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            raise

    def download_pdf(self, url: str, filename: Optional[str] = None, **kwargs) -> str:
        """Download PDF file"""
        if not filename:
            filename = self._get_filename_from_url(url)
            if not filename.endswith('.pdf'):
                filename += '.pdf'
        return self.scrape(url, filename=filename, **kwargs)

    def download_image(self, url: str, filename: Optional[str] = None, **kwargs) -> str:
        """Download image file"""
        return self.scrape(url, filename=filename, **kwargs)

    def download_multiple(
        self,
        urls: List[str],
        filenames: Optional[List[str]] = None,
        **kwargs
    ) -> List[str]:
        """
        Download multiple files.

        Args:
            urls: List of URLs to download
            filenames: Optional list of filenames
            **kwargs: Additional arguments

        Returns:
            List of downloaded file paths
        """
        downloaded = []

        for i, url in enumerate(urls):
            try:
                filename = filenames[i] if filenames and i < len(filenames) else None
                filepath = self.scrape(url, filename=filename, **kwargs)
                downloaded.append(filepath)
            except Exception as e:
                logger.error(f"Failed to download {url}: {e}")

        logger.info(f"Downloaded {len(downloaded)}/{len(urls)} files")
        return downloaded

    def _get_filename_from_url(self, url: str) -> str:
        """Extract filename from URL"""
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)

        # Decode URL-encoded characters
        filename = unquote(filename)

        # If no filename, generate one
        if not filename or filename == '/':
            filename = f"download_{hashlib.md5(url.encode()).hexdigest()[:8]}"

        return filename

    def _get_filename_from_headers(self, headers: Dict) -> Optional[str]:
        """Extract filename from Content-Disposition header"""
        content_disposition = headers.get('content-disposition', '')
        if 'filename=' in content_disposition:
            # Extract filename
            parts = content_disposition.split('filename=')
            if len(parts) > 1:
                filename = parts[1].strip('"\'')
                return filename
        return None

    def _verify_file_type(self, filepath: Path, url: str):
        """Verify file type matches extension"""
        try:
            if MAGIC_AVAILABLE:
                # Use python-magic for accurate detection
                mime = magic.from_file(str(filepath), mime=True)
                logger.debug(f"Detected MIME type: {mime}")

                # Get expected extension
                guessed_ext = mimetypes.guess_extension(mime)
                actual_ext = filepath.suffix

                if guessed_ext and actual_ext != guessed_ext:
                    logger.warning(
                        f"File extension mismatch: expected {guessed_ext}, got {actual_ext}"
                    )
            else:
                # Fallback to basic validation
                logger.debug("python-magic not available, skipping MIME type verification")

        except Exception as e:
            logger.warning(f"Failed to verify file type: {e}")

    def _format_size(self, size: int) -> str:
        """Format file size for display"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def get_file_info(self, filepath: str) -> Dict:
        """
        Get information about a file.

        Args:
            filepath: Path to file

        Returns:
            Dictionary with file info
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        info = {
            'path': str(path),
            'name': path.name,
            'size': path.stat().st_size,
            'size_formatted': self._format_size(path.stat().st_size),
            'extension': path.suffix,
        }

        # Add MIME type if available
        if MAGIC_AVAILABLE:
            info['mime_type'] = magic.from_file(str(path), mime=True)

        return info


class AsyncFileDownloader(AsyncBaseScraper):
    """
    Async file downloader for concurrent downloads
    """

    def __init__(
        self,
        download_dir: str = "./downloads",
        chunk_size: int = 8192,
        **kwargs
    ):
        """
        Initialize async file downloader.

        Args:
            download_dir: Directory to save downloads
            chunk_size: Download chunk size
            **kwargs: Arguments for AsyncBaseScraper
        """
        super().__init__(**kwargs)
        self.download_dir = Path(download_dir)
        self.chunk_size = chunk_size

        self.download_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized AsyncFileDownloader (download_dir={download_dir})")

    async def scrape_async(
        self,
        url: str,
        filename: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Async download file.

        Args:
            url: URL to download
            filename: Custom filename
            **kwargs: Additional arguments

        Returns:
            Path to downloaded file
        """
        try:
            # Get filename
            if not filename:
                parsed = urlparse(url)
                filename = os.path.basename(parsed.path) or f"download_{hashlib.md5(url.encode()).hexdigest()[:8]}"

            filepath = self.download_dir / filename

            logger.info(f"Downloading {url} (async)")

            # Download
            response = await self.get_async(url, **kwargs)
            response.raise_for_status()

            # Write file
            import aiofiles
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(response.content)

            logger.info(f"Downloaded {filename}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            raise

    async def download_multiple_async(
        self,
        urls: List[str],
        filenames: Optional[List[str]] = None,
        **kwargs
    ) -> List[str]:
        """
        Download multiple files concurrently.

        Args:
            urls: List of URLs
            filenames: Optional list of filenames
            **kwargs: Additional arguments

        Returns:
            List of downloaded file paths
        """
        tasks = []
        for i, url in enumerate(urls):
            filename = filenames[i] if filenames and i < len(filenames) else None
            tasks.append(self.scrape_async(url, filename=filename, **kwargs))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        downloaded = []
        failed = 0
        for result in results:
            if isinstance(result, Exception):
                failed += 1
            else:
                downloaded.append(result)

        logger.info(f"Downloaded {len(downloaded)}/{len(urls)} files (async)")
        if failed:
            logger.warning(f"{failed} downloads failed")

        return downloaded
