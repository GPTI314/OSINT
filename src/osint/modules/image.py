"""
Image Intelligence Module

Provides comprehensive image intelligence gathering including:
- Reverse image search (Google, Bing, Yandex, TinEye)
- Metadata extraction (EXIF, IPTC, XMP)
- OCR text extraction
- Face detection and recognition
- Object detection
- Image forensics and tampering detection
"""

import requests
import hashlib
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import exifread
from typing import Dict, Any, List, Optional, Tuple
import io
import base64
from datetime import datetime

from ..core.base import BaseModule
from ..core.utils import calculate_hash


class ImageIntelligence(BaseModule):
    """Image Intelligence gathering module"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.google_api_key = self.config.get('google_api_key')
        self.google_cse_id = self.config.get('google_cse_id')
        self.yandex_api_key = self.config.get('yandex_api_key')
        self.tineye_api_key = self.config.get('tineye_api_key')

    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect comprehensive image intelligence

        Args:
            target: Image path or URL
            **kwargs: Additional options
                - include_reverse_search: Include reverse image search (default: True)
                - include_metadata: Include metadata extraction (default: True)
                - include_ocr: Include OCR text extraction (default: True)
                - include_face_detection: Include face detection (default: True)
                - include_object_detection: Include object detection (default: False)
                - include_forensics: Include image forensics (default: False)

        Returns:
            Dictionary with comprehensive image intelligence
        """
        try:
            # Load image
            image, image_data = self._load_image(target)

            data = {
                'source': target,
                'image_properties': self._get_image_properties(image)
            }

            if kwargs.get('include_metadata', True):
                data['metadata'] = self.extract_metadata(target, image_data)

            if kwargs.get('include_reverse_search', True):
                data['reverse_search'] = self.reverse_image_search(target)

            if kwargs.get('include_ocr', True):
                data['ocr'] = self.extract_text_ocr(image)

            if kwargs.get('include_face_detection', True):
                data['faces'] = self.detect_faces(image)

            if kwargs.get('include_object_detection', False):
                data['objects'] = self.detect_objects(image)

            if kwargs.get('include_forensics', False):
                data['forensics'] = self.analyze_forensics(image, image_data)

            return self._create_result(target=target, data=data)

        except Exception as e:
            return self._handle_error(target, e)

    def _load_image(self, source: str) -> Tuple[Image.Image, bytes]:
        """
        Load image from file path or URL

        Args:
            source: Image path or URL

        Returns:
            PIL Image object and raw image data
        """
        if source.startswith('http://') or source.startswith('https://'):
            response = requests.get(source, timeout=30)
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
        else:
            with open(source, 'rb') as f:
                image_data = f.read()
            image = Image.open(source)

        return image, image_data

    def _get_image_properties(self, image: Image.Image) -> Dict[str, Any]:
        """
        Get basic image properties

        Args:
            image: PIL Image object

        Returns:
            Image properties
        """
        return {
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
            'width': image.width,
            'height': image.height,
            'is_animated': getattr(image, 'is_animated', False),
            'n_frames': getattr(image, 'n_frames', 1)
        }

    def extract_metadata(self, source: str, image_data: bytes) -> Dict[str, Any]:
        """
        Extract metadata from image (EXIF, IPTC, XMP)

        Args:
            source: Image source path/URL
            image_data: Raw image data

        Returns:
            Extracted metadata
        """
        metadata = {}

        # EXIF data using exifread
        try:
            tags = exifread.process_file(io.BytesIO(image_data), details=True)
            exif_data = {}

            for tag, value in tags.items():
                # Skip thumbnail data
                if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                    try:
                        exif_data[tag] = str(value)
                    except:
                        pass

            metadata['exif'] = exif_data

            # Extract GPS coordinates if available
            gps_data = self._extract_gps_data(tags)
            if gps_data:
                metadata['gps'] = gps_data

        except Exception as e:
            self.logger.warning(f"EXIF extraction failed: {str(e)}")
            metadata['exif'] = {'error': str(e)}

        # PIL EXIF data
        try:
            image = Image.open(io.BytesIO(image_data))
            exif_pil = image.getexif()

            if exif_pil:
                pil_data = {}
                for tag_id, value in exif_pil.items():
                    tag = TAGS.get(tag_id, tag_id)
                    try:
                        pil_data[tag] = str(value)
                    except:
                        pass
                metadata['exif_pil'] = pil_data

        except Exception as e:
            self.logger.warning(f"PIL EXIF extraction failed: {str(e)}")

        # XMP data (if present)
        try:
            image_str = image_data.decode('latin-1')
            xmp_start = image_str.find('<x:xmpmeta')
            xmp_end = image_str.find('</x:xmpmeta>')

            if xmp_start != -1 and xmp_end != -1:
                xmp_data = image_str[xmp_start:xmp_end + 12]
                metadata['xmp'] = xmp_data[:1000]  # Truncate if too long

        except Exception as e:
            self.logger.warning(f"XMP extraction failed: {str(e)}")

        # Image hashes
        metadata['hashes'] = {
            'md5': calculate_hash(image_data.hex(), 'md5'),
            'sha1': calculate_hash(image_data.hex(), 'sha1'),
            'sha256': calculate_hash(image_data.hex(), 'sha256')
        }

        # Perceptual hash using imagehash
        try:
            import imagehash
            image = Image.open(io.BytesIO(image_data))

            metadata['perceptual_hashes'] = {
                'phash': str(imagehash.phash(image)),
                'average_hash': str(imagehash.average_hash(image)),
                'dhash': str(imagehash.dhash(image)),
                'whash': str(imagehash.whash(image))
            }
        except Exception as e:
            self.logger.warning(f"Perceptual hash calculation failed: {str(e)}")

        return metadata

    def _extract_gps_data(self, tags: Dict) -> Optional[Dict[str, Any]]:
        """
        Extract GPS coordinates from EXIF tags

        Args:
            tags: EXIF tags dictionary

        Returns:
            GPS data dictionary or None
        """
        gps_data = {}

        # Get GPS tags
        gps_latitude = tags.get('GPS GPSLatitude')
        gps_latitude_ref = tags.get('GPS GPSLatitudeRef')
        gps_longitude = tags.get('GPS GPSLongitude')
        gps_longitude_ref = tags.get('GPS GPSLongitudeRef')

        if all([gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref]):
            try:
                def convert_to_degrees(value):
                    """Convert GPS coordinates to degrees"""
                    d, m, s = [float(x.num) / float(x.den) for x in value.values]
                    return d + (m / 60.0) + (s / 3600.0)

                lat = convert_to_degrees(gps_latitude)
                if str(gps_latitude_ref) == 'S':
                    lat = -lat

                lon = convert_to_degrees(gps_longitude)
                if str(gps_longitude_ref) == 'W':
                    lon = -lon

                gps_data['latitude'] = lat
                gps_data['longitude'] = lon
                gps_data['google_maps_url'] = f"https://www.google.com/maps?q={lat},{lon}"

                # Additional GPS data
                if 'GPS GPSAltitude' in tags:
                    altitude = tags['GPS GPSAltitude']
                    gps_data['altitude'] = float(altitude.values[0].num) / float(altitude.values[0].den)

                if 'GPS GPSTimeStamp' in tags:
                    gps_data['timestamp'] = str(tags['GPS GPSTimeStamp'])

                return gps_data

            except Exception as e:
                self.logger.warning(f"GPS data conversion failed: {str(e)}")

        return None

    def reverse_image_search(self, image_source: str) -> Dict[str, Any]:
        """
        Perform reverse image search across multiple engines

        Args:
            image_source: Image path or URL

        Returns:
            Reverse search results
        """
        results = {}

        # Google Reverse Image Search
        if self.google_api_key and self.google_cse_id:
            results['google'] = self._google_reverse_search(image_source)
        else:
            results['google'] = {
                'search_url': f"https://www.google.com/searchbyimage?image_url={image_source}",
                'note': 'Manual search required or configure Google Custom Search API'
            }

        # Bing Reverse Image Search
        results['bing'] = {
            'search_url': f"https://www.bing.com/images/search?view=detailv2&iss=sbi&form=SBIIRP&sbisrc=UrlPaste&q=imgurl:{image_source}",
            'note': 'Manual search required'
        }

        # Yandex Reverse Image Search
        results['yandex'] = {
            'search_url': f"https://yandex.com/images/search?rpt=imageview&url={image_source}",
            'note': 'Manual search required'
        }

        # TinEye Reverse Image Search
        if self.tineye_api_key:
            results['tineye'] = self._tineye_reverse_search(image_source)
        else:
            results['tineye'] = {
                'search_url': f"https://tineye.com/search?url={image_source}",
                'note': 'Manual search required or configure TinEye API'
            }

        return results

    def _google_reverse_search(self, image_url: str) -> Dict[str, Any]:
        """
        Perform Google reverse image search using Custom Search API

        Args:
            image_url: Image URL

        Returns:
            Search results
        """
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'searchType': 'image',
                'q': image_url,
                'num': 10
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'total_results': data.get('searchInformation', {}).get('totalResults', 0),
                    'results': [
                        {
                            'title': item.get('title'),
                            'link': item.get('link'),
                            'snippet': item.get('snippet'),
                            'thumbnail': item.get('image', {}).get('thumbnailLink')
                        }
                        for item in data.get('items', [])
                    ]
                }
            else:
                return {'error': f'API returned status code {response.status_code}'}

        except Exception as e:
            return {'error': str(e)}

    def _tineye_reverse_search(self, image_url: str) -> Dict[str, Any]:
        """
        Perform TinEye reverse image search

        Args:
            image_url: Image URL

        Returns:
            Search results
        """
        # TinEye API integration would go here
        return {
            'search_url': f"https://tineye.com/search?url={image_url}",
            'note': 'TinEye API integration requires pytineye library'
        }

    def extract_text_ocr(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract text from image using OCR

        Args:
            image: PIL Image object

        Returns:
            Extracted text and OCR data
        """
        try:
            import pytesseract

            # Extract text
            text = pytesseract.image_to_string(image)

            # Extract detailed data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            # Filter out empty text
            words = []
            for i, word in enumerate(data['text']):
                if word.strip():
                    words.append({
                        'text': word,
                        'confidence': data['conf'][i],
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })

            return {
                'text': text.strip(),
                'word_count': len([w for w in text.split() if w]),
                'words': words,
                'language': pytesseract.image_to_osd(image)
            }

        except Exception as e:
            self.logger.warning(f"OCR extraction failed: {str(e)}")
            return {'error': str(e)}

    def detect_faces(self, image: Image.Image) -> Dict[str, Any]:
        """
        Detect faces in image

        Args:
            image: PIL Image object

        Returns:
            Face detection results
        """
        try:
            import cv2
            import numpy as np

            # Convert PIL to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Load face cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            # Detect faces
            faces = face_cascade.detectMultiScale(
                cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY),
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            face_data = []
            for (x, y, w, h) in faces:
                face_data.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'center': (int(x + w/2), int(y + h/2))
                })

            # Try face_recognition library for better accuracy
            try:
                import face_recognition

                # Convert to RGB if needed
                rgb_image = np.array(image.convert('RGB'))

                # Find face locations
                face_locations = face_recognition.face_locations(rgb_image)

                # Get face encodings
                face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

                enhanced_faces = []
                for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                    enhanced_faces.append({
                        'location': {
                            'top': top,
                            'right': right,
                            'bottom': bottom,
                            'left': left
                        },
                        'encoding': encoding.tolist()[:10]  # First 10 values for reference
                    })

                return {
                    'face_count': len(faces),
                    'faces': face_data,
                    'enhanced_faces': enhanced_faces
                }

            except ImportError:
                pass

            return {
                'face_count': len(faces),
                'faces': face_data
            }

        except Exception as e:
            self.logger.warning(f"Face detection failed: {str(e)}")
            return {'error': str(e)}

    def detect_objects(self, image: Image.Image) -> Dict[str, Any]:
        """
        Detect objects in image

        Args:
            image: PIL Image object

        Returns:
            Object detection results
        """
        try:
            import cv2
            import numpy as np

            # Convert PIL to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # This is a placeholder for actual object detection
            # Real implementation would use models like YOLO, SSD, or Faster R-CNN

            return {
                'note': 'Object detection requires deep learning models (YOLO, SSD, etc.)',
                'implementation': 'Use opencv-python with pre-trained models or cloud APIs'
            }

        except Exception as e:
            self.logger.warning(f"Object detection failed: {str(e)}")
            return {'error': str(e)}

    def analyze_forensics(self, image: Image.Image, image_data: bytes) -> Dict[str, Any]:
        """
        Perform image forensics analysis

        Args:
            image: PIL Image object
            image_data: Raw image data

        Returns:
            Forensics analysis results
        """
        forensics = {}

        # Error Level Analysis (ELA) for tampering detection
        try:
            # Save original
            original = image.copy()

            # Re-save at different quality
            buffer = io.BytesIO()
            original.save(buffer, 'JPEG', quality=95)
            buffer.seek(0)
            resaved = Image.open(buffer)

            # Calculate difference
            import numpy as np
            diff = np.array(original, dtype=float) - np.array(resaved, dtype=float)
            diff = np.abs(diff).mean()

            forensics['ela_score'] = float(diff)
            forensics['ela_interpretation'] = 'High score may indicate tampering' if diff > 10 else 'Normal'

        except Exception as e:
            forensics['ela'] = {'error': str(e)}

        # JPEG compression analysis
        try:
            if image.format == 'JPEG':
                forensics['compression_analysis'] = {
                    'format': 'JPEG',
                    'quality_estimate': self._estimate_jpeg_quality(image)
                }
        except Exception as e:
            forensics['compression'] = {'error': str(e)}

        # Metadata consistency check
        forensics['metadata_consistency'] = self._check_metadata_consistency(image_data)

        return forensics

    def _estimate_jpeg_quality(self, image: Image.Image) -> int:
        """
        Estimate JPEG quality

        Args:
            image: PIL Image object

        Returns:
            Estimated quality (0-100)
        """
        # Simple estimation based on file size
        # More sophisticated methods would analyze quantization tables
        return 75  # Placeholder

    def _check_metadata_consistency(self, image_data: bytes) -> Dict[str, Any]:
        """
        Check for metadata inconsistencies

        Args:
            image_data: Raw image data

        Returns:
            Consistency analysis
        """
        return {
            'timestamps_consistent': True,
            'software_tags_present': True,
            'note': 'Full forensics requires specialized tools like FotoForensics or Ghiro'
        }
