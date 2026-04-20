"""Sarvam Vision OCR wrapper — India-focused multilingual OCR."""

import json
import tempfile
import zipfile
from models import register_model
from models.base import BaseOCRModel, OCRResult


@register_model
class SarvamOCR(BaseOCRModel):
    @property
    def name(self): return "sarvam_ocr"
    @property
    def display_name(self): return "Sarvam Vision OCR"
    @property
    def model_type(self): return "cloud_api"

    def setup(self):
        from sarvamai import SarvamAI

        cfg = self.config.get("sarvam") or {}
        if not cfg.get("api_key"):
            raise ValueError("Sarvam api_key required in config.")

        self._api_key = cfg["api_key"]
        self._language = cfg.get("language", "en-IN")
        self._output_format = cfg.get("output_format", "md")
        self._client = SarvamAI(api_subscription_key=self._api_key)
        self._is_setup = True

    def _extract_text_from_zip(self, zip_path: str) -> tuple[str, dict]:
        metadata = {"zip_path": zip_path}
        text = ""

        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
            metadata["archive_files"] = names

            text_files = [n for n in names if n.lower().endswith((".md", ".txt", ".html", ".json"))]
            for name in text_files:
                data = z.read(name)
                if name.lower().endswith('.json') and 'metadata/' in name.lower():
                    continue
                content = data.decode("utf-8", "ignore")
                if name.lower().endswith('.json'):
                    try:
                        parsed = json.loads(content)
                        if isinstance(parsed, dict):
                            candidate = parsed.get("text") or parsed.get("content") or ""
                            if candidate:
                                text = candidate
                                metadata["text_file"] = name
                                break
                    except Exception:
                        pass
                else:
                    text = content
                    metadata["text_file"] = name
                    break

            if not text and text_files:
                name = text_files[0]
                text = z.read(name).decode("utf-8", "ignore")
                metadata["text_file"] = name

        return text, metadata

    def _ocr_impl(self, image_path: str) -> OCRResult:
        job = self._client.document_intelligence.create_job(
            language=self._language,
            output_format=self._output_format,
        )
        job.upload_file(image_path)
        job.start()
        status = job.wait_until_complete(timeout=300)

        if status.job_state not in {"Completed", "PartiallyCompleted"}:
            return OCRResult(error=f"Sarvam job failed with state: {status.job_state}")

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        tmp.close()
        out_path = job.download_output(tmp.name)
        raw_text, meta = self._extract_text_from_zip(out_path)
        meta["job_id"] = job.job_id
        meta["job_state"] = status.job_state
        page_metrics = job.get_page_metrics()
        if page_metrics:
            meta["page_metrics"] = page_metrics

        return OCRResult(
            raw_text=raw_text,
            metadata=meta,
        )
