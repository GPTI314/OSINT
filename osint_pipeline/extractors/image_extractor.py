"""
Image data extractor with OCR, metadata, and visual analysis
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io


class ImageExtractor:
    """Extract data from images including OCR, metadata, and visual features"""

    def __init__(self, ocr_lang: str = 'eng'):
        """
        Initialize image extractor

        Args:
            ocr_lang: Language for OCR (default: English)
        """
        self.ocr_lang = ocr_lang

    def extract(self, source: Union[str, bytes, Image.Image], **kwargs) -> Dict[str, Any]:
        """
        Extract data from image

        Args:
            source: Image file path, bytes, or PIL Image
            **kwargs: Additional extraction options

        Returns:
            Extracted data dictionary
        """
        # Load image
        if isinstance(source, str):
            image = Image.open(source)
            source_path = source
        elif isinstance(source, bytes):
            image = Image.open(io.BytesIO(source))
            source_path = None
        else:
            image = source
            source_path = None

        extracted_data = {
            'source_type': 'image',
            'extracted_at': datetime.utcnow().isoformat(),
            'source_path': source_path,
            'metadata': self.extract_metadata(image),
            'properties': self.extract_properties(image),
            'exif': self.extract_exif(image),
            'custom_data': {}
        }

        # Extract OCR text if requested
        if kwargs.get('extract_ocr', False):
            extracted_data['ocr'] = self.extract_text_ocr(image)

        # Extract visual features if requested
        if kwargs.get('extract_visual', False):
            extracted_data['visual'] = self.extract_visual_features(image)

        return extracted_data

    def extract_metadata(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract basic image metadata

        Args:
            image: PIL Image object

        Returns:
            Metadata dictionary
        """
        return {
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
            'width': image.width,
            'height': image.height,
            'aspect_ratio': round(image.width / image.height, 2) if image.height > 0 else 0,
            'megapixels': round((image.width * image.height) / 1000000, 2)
        }

    def extract_properties(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract image properties

        Args:
            image: PIL Image object

        Returns:
            Properties dictionary
        """
        properties = {
            'has_transparency': image.mode in ('RGBA', 'LA', 'P'),
            'is_animated': getattr(image, 'is_animated', False),
            'n_frames': getattr(image, 'n_frames', 1)
        }

        # Get image info
        if hasattr(image, 'info'):
            properties['info'] = image.info

        return properties

    def extract_exif(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract EXIF metadata from image

        Args:
            image: PIL Image object

        Returns:
            EXIF data dictionary
        """
        exif_data = {}

        try:
            exif = image._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)

                    # Handle GPS data specially
                    if tag == 'GPSInfo':
                        gps_data = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[gps_tag] = str(gps_value)
                        exif_data['GPSInfo'] = gps_data
                    else:
                        # Convert to string to handle non-serializable types
                        exif_data[tag] = str(value) if not isinstance(value, (str, int, float, bool)) else value

        except (AttributeError, KeyError, IndexError):
            pass

        return exif_data

    def extract_text_ocr(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract text from image using OCR

        Args:
            image: PIL Image object

        Returns:
            OCR results dictionary
        """
        try:
            import pytesseract

            # Extract text
            text = pytesseract.image_to_string(image, lang=self.ocr_lang)

            # Get detailed data
            data = pytesseract.image_to_data(image, lang=self.ocr_lang, output_type=pytesseract.Output.DICT)

            # Extract bounding boxes for detected text
            boxes = []
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 0:  # Only include confident detections
                    boxes.append({
                        'text': data['text'][i],
                        'confidence': data['conf'][i],
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })

            return {
                'text': text.strip(),
                'language': self.ocr_lang,
                'boxes': boxes,
                'word_count': len(text.split())
            }

        except ImportError:
            return {
                'error': 'pytesseract not installed',
                'text': None
            }
        except Exception as e:
            return {
                'error': str(e),
                'text': None
            }

    def extract_visual_features(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract visual features from image

        Args:
            image: PIL Image object

        Returns:
            Visual features dictionary
        """
        features = {}

        try:
            # Get dominant colors
            features['colors'] = self._extract_dominant_colors(image)

            # Get brightness
            features['brightness'] = self._calculate_brightness(image)

            # Get color histogram
            features['histogram'] = self._get_color_histogram(image)

        except Exception as e:
            features['error'] = str(e)

        return features

    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[Dict[str, Any]]:
        """
        Extract dominant colors from image

        Args:
            image: PIL Image object
            num_colors: Number of dominant colors to extract

        Returns:
            List of color dictionaries
        """
        # Resize image for faster processing
        small_image = image.copy()
        small_image.thumbnail((150, 150))

        # Convert to RGB if needed
        if small_image.mode != 'RGB':
            small_image = small_image.convert('RGB')

        # Get colors
        colors = small_image.getcolors(small_image.width * small_image.height)

        if not colors:
            return []

        # Sort by frequency
        colors.sort(reverse=True)

        # Get top colors
        dominant_colors = []
        for count, color in colors[:num_colors]:
            if isinstance(color, int):
                # Grayscale
                rgb = (color, color, color)
            else:
                rgb = color[:3]  # Take only RGB, ignore alpha

            dominant_colors.append({
                'rgb': rgb,
                'hex': '#{:02x}{:02x}{:02x}'.format(*rgb),
                'count': count
            })

        return dominant_colors

    def _calculate_brightness(self, image: Image.Image) -> float:
        """
        Calculate average brightness of image

        Args:
            image: PIL Image object

        Returns:
            Brightness value (0-255)
        """
        # Convert to grayscale
        grayscale = image.convert('L')

        # Calculate average pixel value
        pixels = list(grayscale.getdata())
        brightness = sum(pixels) / len(pixels)

        return round(brightness, 2)

    def _get_color_histogram(self, image: Image.Image) -> Dict[str, List[int]]:
        """
        Get color histogram

        Args:
            image: PIL Image object

        Returns:
            Histogram data
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Get histogram
        histogram = image.histogram()

        # Split into R, G, B channels
        return {
            'red': histogram[0:256],
            'green': histogram[256:512],
            'blue': histogram[512:768]
        }

    def extract_qr_codes(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Extract QR codes from image

        Args:
            image: PIL Image object

        Returns:
            List of QR code data
        """
        try:
            import cv2
            import numpy as np

            # Convert PIL to OpenCV
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                img_cv = img_array

            # Detect QR codes
            detector = cv2.QRCodeDetector()
            data, points, _ = detector.detectAndDecode(img_cv)

            results = []
            if data:
                results.append({
                    'data': data,
                    'points': points.tolist() if points is not None else None
                })

            return results

        except ImportError:
            return [{'error': 'opencv-python not installed'}]
        except Exception as e:
            return [{'error': str(e)}]

    def compare_images(self, image1: Image.Image, image2: Image.Image) -> Dict[str, Any]:
        """
        Compare two images for similarity

        Args:
            image1: First PIL Image
            image2: Second PIL Image

        Returns:
            Comparison results
        """
        # Simple comparison based on size and basic features
        meta1 = self.extract_metadata(image1)
        meta2 = self.extract_metadata(image2)

        return {
            'same_size': meta1['size'] == meta2['size'],
            'same_format': meta1['format'] == meta2['format'],
            'same_mode': meta1['mode'] == meta2['mode'],
            'size_difference': {
                'width': abs(meta1['width'] - meta2['width']),
                'height': abs(meta1['height'] - meta2['height'])
            }
        }
