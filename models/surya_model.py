"""Surya OCR wrapper."""

from models import register_model
from models.base import BaseOCRModel, OCRResult


@register_model
class SuryaModel(BaseOCRModel):
    @property
    def name(self): return "surya"
    @property
    def display_name(self): return "Surya OCR"

    def setup(self):
        from surya.common.surya.schema import TaskNames
        from surya.detection import DetectionPredictor
        from surya.foundation import FoundationPredictor
        from surya.recognition import RecognitionPredictor

        self._task_name = TaskNames.ocr_with_boxes
        self._foundation_predictor = FoundationPredictor()
        self._det_predictor = DetectionPredictor()
        self._rec_predictor = RecognitionPredictor(self._foundation_predictor)
        self._langs = self.config.get("surya", {}).get("langs", ["en"])
        self._is_setup = True

    def _ocr_impl(self, image_path: str) -> OCRResult:
        from PIL import Image

        img = Image.open(image_path).convert("RGB")
        results = self._rec_predictor(
            [img],
            task_names=[self._task_name],
            det_predictor=self._det_predictor,
            highres_images=[img],
            math_mode=True,
        )

        lines = []
        confidences = []
        if results:
            for line in results[0].text_lines:
                lines.append(line.text)
                confidences.append(line.confidence or 0)

        raw_text = "\n".join(lines)
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        return OCRResult(raw_text=raw_text, confidence=avg_conf,
                         metadata={"lines": len(lines), "langs": self._langs})
