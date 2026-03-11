"""OCR 模块

注意: PaddleOCRVL 类已废弃，请使用 langchain_paddleocr.PaddleOCRVLLoader
印章提取功能已移至 src.utils.seal_extractor
"""
from .paddle_ocr import PaddleOCRVL

__all__ = ["PaddleOCRVL"]
