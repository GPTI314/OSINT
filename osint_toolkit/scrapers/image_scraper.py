"""
Image Scraper
Downloads and processes images with various transformations
"""

from typing import Optional, Dict, List, Tuple
from pathlib import Path
import io
from loguru import logger

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow not installed")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not installed")

from .file_downloader import FileDownloader


class ImageScraper(FileDownloader):
    """
    Image scraper with processing capabilities
    """

    def __init__(
        self,
        download_dir: str = "./images",
        auto_convert: bool = False,
        target_format: str = "PNG",
        **kwargs
    ):
        """
        Initialize image scraper.

        Args:
            download_dir: Directory to save images
            auto_convert: Automatically convert images to target format
            target_format: Target image format (PNG, JPEG, etc.)
            **kwargs: Arguments for FileDownloader
        """
        super().__init__(download_dir=download_dir, **kwargs)

        if not PIL_AVAILABLE:
            logger.warning("Pillow not available - image processing disabled")

        self.auto_convert = auto_convert
        self.target_format = target_format.upper()

        logger.info(f"Initialized ImageScraper (format={target_format})")

    def scrape(
        self,
        url: str,
        filename: Optional[str] = None,
        resize: Optional[Tuple[int, int]] = None,
        convert_format: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Download and optionally process image.

        Args:
            url: Image URL
            filename: Custom filename
            resize: Resize to (width, height)
            convert_format: Convert to format (PNG, JPEG, etc.)
            **kwargs: Additional arguments

        Returns:
            Path to downloaded/processed image
        """
        # Download image
        filepath = super().scrape(url, filename=filename, progress=False, **kwargs)

        # Process image if requested
        if PIL_AVAILABLE and (resize or convert_format or self.auto_convert):
            filepath = self._process_image(
                filepath,
                resize=resize,
                convert_format=convert_format or (self.target_format if self.auto_convert else None)
            )

        return filepath

    def _process_image(
        self,
        filepath: str,
        resize: Optional[Tuple[int, int]] = None,
        convert_format: Optional[str] = None,
        quality: int = 95
    ) -> str:
        """
        Process image (resize, convert format).

        Args:
            filepath: Path to image
            resize: New size (width, height)
            convert_format: Target format
            quality: JPEG quality

        Returns:
            Path to processed image
        """
        try:
            img = Image.open(filepath)
            modified = False

            # Resize
            if resize:
                img = img.resize(resize, Image.Resampling.LANCZOS)
                modified = True
                logger.debug(f"Resized image to {resize}")

            # Convert format
            if convert_format:
                convert_format = convert_format.upper()

                # Handle RGBA to RGB conversion for JPEG
                if convert_format == 'JPEG' and img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])
                    img = rgb_img

                # Update filename
                path = Path(filepath)
                new_ext = f".{convert_format.lower()}"
                if convert_format == 'JPEG':
                    new_ext = '.jpg'

                new_filepath = path.with_suffix(new_ext)

                # Save in new format
                save_kwargs = {}
                if convert_format == 'JPEG':
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True

                img.save(new_filepath, format=convert_format, **save_kwargs)

                # Remove old file if different
                if new_filepath != Path(filepath):
                    Path(filepath).unlink()

                filepath = str(new_filepath)
                modified = True
                logger.debug(f"Converted image to {convert_format}")

            elif modified:
                # Save with modifications
                img.save(filepath)

            return filepath

        except Exception as e:
            logger.error(f"Failed to process image: {e}")
            return filepath

    def resize_image(
        self,
        filepath: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect: bool = True
    ) -> str:
        """
        Resize image.

        Args:
            filepath: Path to image
            width: Target width
            height: Target height
            maintain_aspect: Maintain aspect ratio

        Returns:
            Path to resized image
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow is required for image processing")

        try:
            img = Image.open(filepath)
            original_size = img.size

            if maintain_aspect and (width or height):
                # Calculate new size maintaining aspect ratio
                if width and not height:
                    ratio = width / original_size[0]
                    height = int(original_size[1] * ratio)
                elif height and not width:
                    ratio = height / original_size[1]
                    width = int(original_size[0] * ratio)

            new_size = (width or original_size[0], height or original_size[1])
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            img.save(filepath)

            logger.info(f"Resized image from {original_size} to {new_size}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            raise

    def crop_image(
        self,
        filepath: str,
        box: Tuple[int, int, int, int]
    ) -> str:
        """
        Crop image.

        Args:
            filepath: Path to image
            box: Crop box (left, upper, right, lower)

        Returns:
            Path to cropped image
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow is required for image processing")

        try:
            img = Image.open(filepath)
            img = img.crop(box)
            img.save(filepath)

            logger.info(f"Cropped image to {box}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to crop image: {e}")
            raise

    def apply_filter(
        self,
        filepath: str,
        filter_name: str
    ) -> str:
        """
        Apply filter to image.

        Args:
            filepath: Path to image
            filter_name: Filter name (BLUR, SHARPEN, EDGE_ENHANCE, etc.)

        Returns:
            Path to filtered image
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow is required for image processing")

        try:
            img = Image.open(filepath)

            # Apply filter
            filter_map = {
                'BLUR': ImageFilter.BLUR,
                'SHARPEN': ImageFilter.SHARPEN,
                'EDGE_ENHANCE': ImageFilter.EDGE_ENHANCE,
                'SMOOTH': ImageFilter.SMOOTH,
                'DETAIL': ImageFilter.DETAIL,
                'CONTOUR': ImageFilter.CONTOUR,
            }

            filter_obj = filter_map.get(filter_name.upper())
            if filter_obj:
                img = img.filter(filter_obj)
                img.save(filepath)
                logger.info(f"Applied {filter_name} filter")
            else:
                logger.warning(f"Unknown filter: {filter_name}")

            return filepath

        except Exception as e:
            logger.error(f"Failed to apply filter: {e}")
            raise

    def adjust_brightness(
        self,
        filepath: str,
        factor: float
    ) -> str:
        """
        Adjust image brightness.

        Args:
            filepath: Path to image
            factor: Brightness factor (1.0 = original, >1.0 = brighter, <1.0 = darker)

        Returns:
            Path to adjusted image
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow is required for image processing")

        try:
            img = Image.open(filepath)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(factor)
            img.save(filepath)

            logger.info(f"Adjusted brightness by factor {factor}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to adjust brightness: {e}")
            raise

    def adjust_contrast(
        self,
        filepath: str,
        factor: float
    ) -> str:
        """
        Adjust image contrast.

        Args:
            filepath: Path to image
            factor: Contrast factor (1.0 = original)

        Returns:
            Path to adjusted image
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow is required for image processing")

        try:
            img = Image.open(filepath)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(factor)
            img.save(filepath)

            logger.info(f"Adjusted contrast by factor {factor}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to adjust contrast: {e}")
            raise

    def convert_to_grayscale(self, filepath: str) -> str:
        """Convert image to grayscale"""
        if not PIL_AVAILABLE:
            raise ImportError("Pillow is required for image processing")

        try:
            img = Image.open(filepath)
            img = img.convert('L')
            img.save(filepath)

            logger.info("Converted image to grayscale")
            return filepath

        except Exception as e:
            logger.error(f"Failed to convert to grayscale: {e}")
            raise

    def get_image_metadata(self, filepath: str) -> Dict:
        """
        Get image metadata.

        Args:
            filepath: Path to image

        Returns:
            Dictionary with image metadata
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow is required for image processing")

        try:
            img = Image.open(filepath)

            metadata = {
                'size': img.size,
                'width': img.width,
                'height': img.height,
                'mode': img.mode,
                'format': img.format,
            }

            # Add EXIF data if available
            if hasattr(img, '_getexif') and img._getexif():
                metadata['exif'] = img._getexif()

            return metadata

        except Exception as e:
            logger.error(f"Failed to get image metadata: {e}")
            raise

    def detect_faces(self, filepath: str) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in image using OpenCV.

        Args:
            filepath: Path to image

        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV is required for face detection")

        try:
            # Load cascade classifier
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)

            # Read image
            img = cv2.imread(filepath)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            logger.info(f"Detected {len(faces)} faces")
            return [tuple(face) for face in faces]

        except Exception as e:
            logger.error(f"Failed to detect faces: {e}")
            raise

    def extract_dominant_colors(
        self,
        filepath: str,
        num_colors: int = 5
    ) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors from image.

        Args:
            filepath: Path to image
            num_colors: Number of dominant colors to extract

        Returns:
            List of RGB color tuples
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow is required for color extraction")

        try:
            img = Image.open(filepath)
            img = img.convert('RGB')

            # Resize for faster processing
            img = img.resize((150, 150))

            # Get colors
            pixels = list(img.getdata())

            # Simple clustering (get most common colors)
            from collections import Counter
            color_counts = Counter(pixels)
            dominant = color_counts.most_common(num_colors)

            colors = [color for color, count in dominant]
            logger.info(f"Extracted {len(colors)} dominant colors")

            return colors

        except Exception as e:
            logger.error(f"Failed to extract colors: {e}")
            raise
