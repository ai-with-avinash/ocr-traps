"""GOT-OCR 2.0 wrapper — General OCR Transformer (HuggingFace version)."""

from models import register_model
from models.base import BaseOCRModel, OCRResult
from utils.helpers import get_device


@register_model
class GOTOCR(BaseOCRModel):
    @property
    def name(self): return "got_ocr"
    @property
    def display_name(self): return "GOT-OCR 2.0"

    def setup(self):
        from transformers import AutoProcessor, AutoModelForImageTextToText
        import torch

        cfg = self.config.get("got_ocr", {})
        model_name = cfg.get("model_name", "stepfun-ai/GOT-OCR-2.0-hf")
        self._device = get_device(self.config)

        print(f"  Loading GOT-OCR 2.0 on {self._device}...")
        dtype = torch.float16 if self._device != "cpu" else torch.float32
        self._processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        self._model = AutoModelForImageTextToText.from_pretrained(
            model_name, trust_remote_code=True, dtype=dtype,
        ).to(self._device).eval()
        self._is_setup = True

    def _ocr_impl(self, image_path: str) -> OCRResult:
        from PIL import Image
        import torch

        img = Image.open(image_path).convert("RGB")

        # Build prompt with 256 image pad tokens as required by GOT-OCR 2.0
        p = self._processor
        img_tokens = p.img_start_token + p.img_pad_token * 256 + p.img_end_token
        prompt = (
            f"<|im_start|>system\n{p.system_query}<|im_end|>\n"
            f"<|im_start|>user\n{img_tokens}\nOCR with format<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        inputs = p(images=img, text=prompt, return_tensors="pt").to(self._device)

        with torch.no_grad():
            output_ids = self._model.generate(**inputs, max_new_tokens=4096, do_sample=False)

        gen_ids = output_ids[:, inputs["input_ids"].shape[1]:]
        text = p.batch_decode(gen_ids, skip_special_tokens=True)[0]

        return OCRResult(raw_text=text, metadata={"device": str(self._device)})
