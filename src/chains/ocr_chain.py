"""OCR 处理链"""
from typing import Optional
from ..ocr import PaddleOCRVL
from ..config import get_api_key


class OCRChain:
    """OCR 处理链

    负责调用 PaddleOCR-VL-1.5 进行票据识别
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: AIStudio API Key，默认从环境变量读取
        """
        self.ocr = PaddleOCRVL(api_key or get_api_key())

    def process(self, file_path: str, enable_seal: bool = True) -> dict:
        """处理票据图片

        Args:
            file_path: 图片路径
            enable_seal: 是否启用印章识别

        Returns:
            处理结果，包含 text、seals、raw_result
        """
        result = self.ocr.recognize(
            file_path,
            use_seal_recognition=enable_seal
        )

        return {
            "text": self.ocr.extract_text(result),
            "seals": self.ocr.extract_seals(result),
            "raw_result": result
        }

    def batch_process(self, file_paths: list, enable_seal: bool = True) -> list:
        """批量处理票据图片

        Args:
            file_paths: 图片路径列表
            enable_seal: 是否启用印章识别

        Returns:
            处理结果列表
        """
        results = []
        for path in file_paths:
            try:
                result = self.process(path, enable_seal)
                result["file_path"] = path
                result["status"] = "success"
            except Exception as e:
                result = {
                    "file_path": path,
                    "status": "error",
                    "error": str(e)
                }
            results.append(result)
        return results
