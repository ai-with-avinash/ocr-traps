"""olmOCR wrapper — Allen AI VLM-based OCR (Qwen2-VL architecture)."""

from models import register_model
from models.base import BaseOCRModel, OCRResult
from utils.helpers import get_device


@register_model
class OlmOCR(BaseOCRModel):
    @property
    def name(self): return "olmocr"
    @property
    def display_name(self): return "olmOCR"

    def setup(self):
        from transformers import AutoProcessor, AutoModelForImageTextToText
        import torch

        cfg = self.config.get("olmocr", {})
        model_name = cfg.get("model_name", "allenai/olmOCR-7B-0225-preview")
        self._device = get_device(self.config)

        print(f"  Loading olmOCR on {self._device}...")
        dtype = torch.float16 if self._device != "cpu" else torch.float32
        self._processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        self._model = AutoModelForImageTextToText.from_pretrained(
            model_name, trust_remote_code=True, dtype=dtype,
        ).to(self._device).eval()
        self._is_setup = True

    def _ocr_impl(self, image_path: str) -> OCRResult:
        from PIL import Image
        import torch
        import gc

        img = Image.open(image_path).convert("RGB")
        max_side = 1280
        if max(img.size) > max_side:
            ratio = max_side / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        messages = [{"role": "user", "content": [
            {"type": "image", "image": img},
            {"type": "text", "text": "Extract all text from this document image. Return the text preserving the original layout and reading order."},
        ]}]

        text_input = self._processor.apply_chat_template(messages, tokenize=False,
                                                          add_generation_prompt=True)
        inputs = self._processor(text=[text_input], images=[img], return_tensors="pt",
                                  padding=True).to(self._device)

        try:
            with torch.no_grad():
                output_ids = self._model.generate(**inputs, max_new_tokens=4096)

            output_ids = output_ids[:, inputs.input_ids.shape[1]:]
            text = self._processor.batch_decode(output_ids, skip_special_tokens=True)[0]
        finally:
            del inputs
            if 'output_ids' in locals():
                del output_ids
            gc.collect()
            if self._device == "mps":
                torch.mps.empty_cache()
            elif self._device == "cuda":
                torch.cuda.empty_cache()

        return OCRResult(raw_text=text, metadata={"device": str(self._device)})
