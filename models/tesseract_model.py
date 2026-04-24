"""Tesseract OCR — Baseline model."""

from models import register_model
from models.base import BaseOCRModel, OCRResult


@register_model
class TesseractOCR(BaseOCRModel):
    @property
    def name(self): return "tesseract"
    @property
    def display_name(self): return "Tesseract (Baseline)"

    def setup(self):
        import pytesseract
        self._tess = pytesseract
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            raise RuntimeError(
                "Tesseract not installed.\n"
                "  macOS:  brew install tesseract tesseract-lang\n"
                "  Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-hin tesseract-ocr-tel"
            )
        self._is_setup = True

    def _ocr_impl(self, image_path: str) -> OCRResult:
        from PIL import Image
        cfg = self.config.get("tesseract", {})
        lang = cfg.get("lang", "eng")
        custom = f"--psm {cfg.get('psm', 3)} --oem {cfg.get('oem', 3)}"

        # Handle PDFs by converting to images with pdf2image
        path_lower = image_path.lower()
        if path_lower.endswith('.pdf'):
            from pdf2image import convert_from_path
            pages = convert_from_path(image_path, dpi=200)
            all_text = []
            for page in pages:
                text = self._tess.image_to_string(page, lang=lang, config=custom)
                all_text.append(text)
            full_text = "\n\n".join(all_text)

            # Compute confidence from OCR data on all pages
            all_confs = []
            for page in pages:
                data = self._tess.image_to_data(page, lang=lang, config=custom,
                                                output_type=self._tess.Output.DICT)
                page_confs = [int(c) for c in data["conf"] if int(c) > 0]
                all_confs.extend(page_confs)

            avg = sum(all_confs) / len(all_confs) / 100 if all_confs else 0
            return OCRResult(raw_text=full_text, confidence=avg,
                             metadata={"lang": lang, "words": len(all_confs),
                                       "pdf_pages": len(pages)})

        img = Image.open(image_path)
        text = self._tess.image_to_string(img, lang=lang, config=custom)
        data = self._tess.image_to_data(img, lang=lang, config=custom,
                                         output_type=self._tess.Output.DICT)
        confs = [int(c) for c in data["conf"] if int(c) > 0]
        avg = sum(confs) / len(confs) / 100 if confs else 0
        return OCRResult(raw_text=text, confidence=avg,
                         metadata={"lang": lang, "words": len(confs)})
