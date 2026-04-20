"""PaddleOCR wrapper."""
import inspect

from models import register_model
from models.base import BaseOCRModel, OCRResult


@register_model
class PaddleOCRModel(BaseOCRModel):
    @property
    def name(self): return "paddleocr"
    @property
    def display_name(self): return "PaddleOCR"

    def setup(self):
        from paddleocr import PaddleOCR

        cfg = self.config.get("paddleocr", {})
        sig = inspect.signature(PaddleOCR.__init__)
        params = sig.parameters

        init_kwargs = {
            "lang": cfg.get("lang", "en"),
        }

        use_angle_cls = cfg.get("use_angle_cls", True)
        if "use_textline_orientation" in params:
            init_kwargs["use_textline_orientation"] = use_angle_cls
        elif "use_angle_cls" in params:
            init_kwargs["use_angle_cls"] = use_angle_cls

        if "use_gpu" in params:
            init_kwargs["use_gpu"] = cfg.get("use_gpu", True)
        if "show_log" in params:
            init_kwargs["show_log"] = False

        self._ocr = PaddleOCR(**init_kwargs)
        self._is_setup = True

    def _ocr_impl(self, image_path: str) -> OCRResult:
        lines, confidences = [], []

        if hasattr(self._ocr, "predict"):
            result = self._ocr.predict(image_path)
            if result:
                page = result[0]
                lines = page.get("rec_texts", []) or []
                confidences = page.get("rec_scores", []) or []
        else:
            result = self._ocr.ocr(image_path, cls=True)
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    conf = line[1][1]
                    lines.append(text)
                    confidences.append(conf)

        raw_text = "\n".join(lines)
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        return OCRResult(raw_text=raw_text, confidence=avg_conf,
                         metadata={"lines": len(lines)})
