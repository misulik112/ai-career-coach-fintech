"""
Image OCR Parser with Multi-Language Support
Week 3 Day 18+ - Extract text from images in multiple languages
"""

from typing import Dict, Optional, List
from pathlib import Path
import os
import subprocess

try:
    import pytesseract
    from PIL import Image

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️  OCR libraries not installed. Run: pip install pytesseract pillow")


class ImageOCR:
    """Extract text from images using OCR with multi-language support"""

    # Language code mappings (ISO 639-3 to Tesseract codes)
    LANGUAGE_CODES = {
        "english": "eng",
        "french": "fra",
        "german": "deu",
        "spanish": "spa",
        "italian": "ita",
        "portuguese": "por",
        "russian": "rus",
        "arabic": "ara",
        "chinese_simplified": "chi_sim",
        "chinese_traditional": "chi_tra",
        "japanese": "jpn",
        "korean": "kor",
        "greek": "ell",
        "dutch": "nld",
        "polish": "pol",
        "turkish": "tur",
        "vietnamese": "vie",
        "thai": "tha",
        "hindi": "hin",
        "swedish": "swe",
        "norwegian": "nor",
        "danish": "dan",
        "finnish": "fin",
        "romanian": "ron",
    }

    def __init__(self, tesseract_cmd: Optional[str] = None, default_lang="ron"):
        """
        Initialize OCR engine with multi-language support

        Args:
            tesseract_cmd: Path to tesseract executable (auto-detect if None)
            default_lang: Default language code (e.g., 'eng', 'fra', 'deu')
        """
        self.default_lang = default_lang
        self.available_languages = []

        self.stats = {
            "images_processed": 0,
            "text_extracted": 0,
            "failed": 0,
            "languages_used": {},
        }

        # Set tesseract command path if provided
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        # AUTO-FIX: Set TESSDATA_PREFIX if not set
        self._auto_configure_tessdata()

        print(f"📸 Multi-Language OCR initialized")
        print(f"   Available: {OCR_AVAILABLE}")

        if OCR_AVAILABLE:
            self._initialize_tesseract()

    def _auto_configure_tessdata(self):
        """Auto-detect and configure TESSDATA_PREFIX"""
        if "TESSDATA_PREFIX" not in os.environ:
            # Try common locations
            possible_paths = [
                "/opt/homebrew/share/tessdata/",  # M1/M2 Mac
                "/usr/local/share/tessdata/",  # Intel Mac
                "/usr/share/tessdata/",  # Linux
                "C:\\Program Files\\Tesseract-OCR\\tessdata\\",  # Windows
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    os.environ["TESSDATA_PREFIX"] = path
                    print(f"   ℹ️  Auto-set TESSDATA_PREFIX: {path}")
                    break
            else:
                # Try to find via brew
                try:
                    result = subprocess.run(
                        ["brew", "--prefix", "tesseract"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        brew_prefix = result.stdout.strip()
                        tessdata_path = os.path.join(brew_prefix, "share", "tessdata")
                        if os.path.exists(tessdata_path):
                            os.environ["TESSDATA_PREFIX"] = tessdata_path
                            print(
                                f"   ℹ️  Auto-detected TESSDATA_PREFIX: {tessdata_path}"
                            )
                except:
                    pass

    def _initialize_tesseract(self):
        """Initialize and verify Tesseract configuration"""
        try:
            # Test tesseract
            version = pytesseract.get_tesseract_version()
            print(f"   Tesseract version: {version}")

            # List available languages
            try:
                self.available_languages = pytesseract.get_languages()
                print(
                    f"   Available languages ({len(self.available_languages)}): {', '.join(self.available_languages)}"
                )

                # Check if default language is available
                if self.default_lang not in self.available_languages:
                    print(
                        f"   ⚠️  Default language '{self.default_lang}' not installed!"
                    )
                    if "eng" in self.available_languages:
                        self.default_lang = "eng"
                        print(f"   ℹ️  Falling back to English (eng)")

            except Exception as e:
                print(f"   ⚠️  Could not list languages: {e}")
                self.available_languages = ["eng"]

        except Exception as e:
            print(f"   ⚠️  Tesseract configuration issue: {e}")
            print(f"\n   💡 Quick fix:")
            print(f"      brew reinstall tesseract")
            print(f"      brew install tesseract-lang  # For all languages")

    def extract_text_from_image(
        self, filepath: str, lang: Optional[str] = None, auto_detect: bool = False
    ) -> Optional[Dict]:
        """
        Extract text from a single image file

        Args:
            filepath: Path to image file
            lang: Language code (e.g., 'eng', 'fra', 'eng+fra' for multiple)
                  If None, uses default_lang
            auto_detect: Try to auto-detect language (experimental)
        """
        if not OCR_AVAILABLE:
            print("❌ OCR libraries not available")
            return None

        filepath = Path(filepath)

        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            return None

        # Check if it's an image file
        valid_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}
        if filepath.suffix.lower() not in valid_extensions:
            print(f"❌ Not a supported image file: {filepath}")
            return None

        # Determine language to use
        ocr_lang = lang or self.default_lang

        # Auto-detect language if requested
        if auto_detect:
            detected_lang = self._detect_language(filepath)
            if detected_lang:
                ocr_lang = detected_lang
                print(f"   🌍 Auto-detected language: {ocr_lang}")

        print(f"\n📸 Processing image: {filepath.name} (lang: {ocr_lang})")

        try:
            # Open image
            image = Image.open(filepath)

            # Get image info
            width, height = image.size
            mode = image.mode

            # Extract text with Tesseract
            text = pytesseract.image_to_string(image, lang=ocr_lang)

            # Clean text
            text = text.strip()

            # Get confidence data
            try:
                data = pytesseract.image_to_data(
                    image, lang=ocr_lang, output_type=pytesseract.Output.DICT
                )
                confidences = [int(conf) for conf in data["conf"] if conf != "-1"]
                avg_confidence = (
                    sum(confidences) / len(confidences) if confidences else 0
                )
            except:
                avg_confidence = 0

            word_count = len(text.split())

            # Track language usage
            if ocr_lang not in self.stats["languages_used"]:
                self.stats["languages_used"][ocr_lang] = 0
            self.stats["languages_used"][ocr_lang] += 1

            result = {
                "filename": filepath.name,
                "filepath": str(filepath),
                "content": text,
                "metadata": {
                    "source": "image_ocr",
                    "filename": filepath.name,
                    "image_width": str(width),
                    "image_height": str(height),
                    "image_mode": mode,
                    "ocr_language": ocr_lang,
                    "ocr_confidence": str(round(avg_confidence, 2)),
                },
                "word_count": word_count,
                "file_type": "image",
            }

            print(
                f"   ✓ Extracted: {word_count} words (confidence: {avg_confidence:.1f}%)"
            )

            self.stats["images_processed"] += 1
            if word_count > 0:
                self.stats["text_extracted"] += 1

            return result

        except Exception as e:
            print(f"   ❌ Failed to process {filepath.name}: {e}")
            self.stats["failed"] += 1
            return None

    def _detect_language(self, filepath: str) -> Optional[str]:
        """
        Auto-detect language in image (using OSD - Orientation and Script Detection)
        Returns language code or None
        """
        try:
            image = Image.open(filepath)
            # Use OSD to detect script
            osd = pytesseract.image_to_osd(image)

            # Parse OSD output (basic implementation)
            # This is experimental and may not always work
            if "Script: Latin" in osd:
                return "eng"  # Default to English for Latin script
            elif "Script: Arabic" in osd:
                return "ara"
            elif "Script: Han" in osd:
                return "chi_sim"
            elif "Script: Japanese" in osd:
                return "jpn"
            elif "Script: Hangul" in osd:
                return "kor"
            elif "Script: Greek" in osd:
                return "ell"

        except Exception as e:
            print(f"   ℹ️  Auto-detection failed: {e}")

        return None

    def process_folder(
        self, folder_path: str, lang: Optional[str] = None, auto_detect: bool = False
    ) -> List[Dict]:
        """
        Process all images in a folder

        Args:
            folder_path: Path to folder
            lang: Language code (None = use default)
            auto_detect: Auto-detect language for each image
        """
        folder = Path(folder_path)

        if not folder.exists():
            print(f"❌ Folder not found: {folder_path}")
            return []

        # Find all image files
        image_extensions = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.tiff"]
        image_files = []

        for ext in image_extensions:
            image_files.extend(folder.glob(f"**/{ext}"))

        if not image_files:
            print(f"⚠️  No image files found in {folder_path}")
            return []

        print(f"\n📂 Found {len(image_files)} image file(s)")

        results = []
        for image_file in image_files:
            result = self.extract_text_from_image(
                image_file, lang=lang, auto_detect=auto_detect
            )
            if result and result["word_count"] > 0:
                results.append(result)

        return results

    def extract_multilingual(self, filepath: str, languages: List[str]) -> Dict:
        """
        Extract text trying multiple languages and return best result

        Args:
            filepath: Path to image
            languages: List of language codes to try (e.g., ['eng', 'fra', 'deu'])
        """
        best_result = None
        best_confidence = 0

        print(f"\n🌍 Multi-language extraction for: {Path(filepath).name}")
        print(f"   Trying languages: {', '.join(languages)}")

        for lang in languages:
            if lang not in self.available_languages:
                print(f"   ⏭️  Skipping {lang} (not installed)")
                continue

            result = self.extract_text_from_image(filepath, lang=lang)

            if result:
                confidence = float(result["metadata"]["ocr_confidence"])

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_result = result

        if best_result:
            print(
                f"   🏆 Best result: {best_result['metadata']['ocr_language']} "
                f"(confidence: {best_confidence:.1f}%)"
            )

        return best_result

    def get_language_name(self, code: str) -> str:
        """Get human-readable language name from code"""
        reverse_map = {v: k for k, v in self.LANGUAGE_CODES.items()}
        return reverse_map.get(code, code).replace("_", " ").title()

    def list_available_languages(self):
        """Print all available languages"""
        print("\n🌍 Available OCR Languages:")
        print("=" * 60)

        for lang in sorted(self.available_languages):
            lang_name = self.get_language_name(lang)
            print(f"   {lang:<15} - {lang_name}")

        print("=" * 60)
        print(f"\nTotal: {len(self.available_languages)} languages")

        if len(self.available_languages) < 5:
            print("\n💡 Install more languages:")
            print("   macOS: brew install tesseract-lang")
            print("   Linux: sudo apt-get install tesseract-ocr-[lang]")

    def get_stats(self) -> Dict:
        """Get OCR statistics"""
        success_rate = (
            (self.stats["text_extracted"] / self.stats["images_processed"] * 100)
            if self.stats["images_processed"] > 0
            else 0
        )

        return {**self.stats, "success_rate": round(success_rate, 1)}

    def print_stats(self):
        """Print OCR statistics"""
        stats = self.get_stats()

        print(f"\n📊 OCR Statistics:")
        print(f"   Images processed: {stats['images_processed']}")
        print(f"   Text extracted: {stats['text_extracted']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Success rate: {stats['success_rate']}%")

        if stats["languages_used"]:
            print(f"\n🌍 Languages used:")
            for lang, count in sorted(
                stats["languages_used"].items(), key=lambda x: x[1], reverse=True
            ):
                lang_name = self.get_language_name(lang)
                print(f"   {lang} ({lang_name}): {count} image(s)")


# Quick test
if __name__ == "__main__":
    print("=" * 70)
    print("🌍 MULTI-LANGUAGE OCR TEST")
    print("=" * 70)

    ocr = ImageOCR(default_lang="eng")

    if not OCR_AVAILABLE:
        print("\n❌ Install OCR libraries first:")
        print("   pip install pytesseract pillow")
        print("   brew install tesseract tesseract-lang")
    else:
        # List available languages
        ocr.list_available_languages()

        # Test with sample images if available
        test_folder = "data/images"

        if not os.path.exists(test_folder):
            os.makedirs(test_folder, exist_ok=True)
            print(f"\n📁 Created folder: {test_folder}")
            print(f"   Add image files to test OCR!")
        else:
            # Process with auto-detect
            print("\n" + "=" * 70)
            print("Testing Auto-Language Detection")
            print("=" * 70)

            results = ocr.process_folder(test_folder, auto_detect=False)

            if results:
                print(f"\n✅ Processed {len(results)} image(s)")

                # Show sample
                if results:
                    sample = results[0]
                    print(f"\n--- Sample: {sample['filename']} ---")
                    print(f"Language: {sample['metadata']['ocr_language']}")
                    print(f"Confidence: {sample['metadata']['ocr_confidence']}%")
                    print(f"Words: {sample['word_count']}")
                    print(f"\nText preview:")
                    print(sample["content"][:200] + "...")

            ocr.print_stats()

    print("\n" + "=" * 70)
    print("✅ MULTI-LANGUAGE OCR READY!")
    print("=" * 70)
