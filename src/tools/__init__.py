"""LangChain Tools for Receipt Processing

This module provides LangChain-compatible tools for receipt OCR,
information extraction, and classification.

All tools wrap the existing chains that use langchain-paddleocr.

Example:
    >>> from src.tools import ReceiptOCRTool, ReceiptExtractionTool
    >>> ocr_tool = ReceiptOCRTool()
    >>> result = ocr_tool.invoke({"file_path": "invoice.jpg"})
"""

from .ocr_tool import ReceiptOCRTool
from .extraction_tool import ReceiptExtractionTool
from .classification_tool import ReceiptClassificationTool

__all__ = [
    "ReceiptOCRTool",
    "ReceiptExtractionTool",
    "ReceiptClassificationTool",
]
