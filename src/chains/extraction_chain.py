"""信息提取链"""
from typing import Optional
from ..llm import ReceiptExtractionChain
from ..config import get_api_key


class ExtractionChain:
    """信息提取链

    负责从 OCR 文本中提取结构化信息
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: AIStudio API Key，默认从环境变量读取
        """
        self.chain = ReceiptExtractionChain(api_key or get_api_key())

    def extract(self, ocr_text: str) -> dict:
        """提取票据信息

        Args:
            ocr_text: OCR 识别的文本

        Returns:
            结构化的票据信息
        """
        return self.chain.extract(ocr_text)

    def extract_with_seals(self, ocr_text: str, seals: list) -> dict:
        """提取票据信息（包含印章信息）

        Args:
            ocr_text: OCR 识别的文本
            seals: 印章信息列表

        Returns:
            结构化的票据信息（含印章分析）
        """
        result = self.chain.extract(ocr_text)

        # 添加印章信息
        if seals:
            seal_info = self._analyze_seals(seals)
            result["seal_analysis"] = seal_info
            result["seals"] = seals  # 同时保存印章列表

        return result

    def _analyze_seals(self, seals: list) -> dict:
        """分析印章信息

        Args:
            seals: 印章列表

        Returns:
            印章分析结果
        """
        seal_types = [s["type"] for s in seals]

        return {
            "count": len(seals),
            "types": seal_types,
            "has_official_seal": "公章" in seal_types,
            "has_finance_seal": "财务专用章" in seal_types,
            "has_invoice_seal": "发票专用章" in seal_types,
            "has_supervision_seal": "发票监制章" in seal_types,
            "authenticity_hint": self._get_authenticity_hint(seal_types)
        }

    def _get_authenticity_hint(self, seal_types: list) -> str:
        """根据印章类型给出真伪提示

        Args:
            seal_types: 印章类型列表

        Returns:
            真伪提示信息
        """
        if "发票专用章" in seal_types:
            return "发票专用章齐全，建议通过税务局官网验证真伪"
        elif "财务专用章" in seal_types:
            return "有财务专用章，请确认是否有发票专用章"
        elif "公章" in seal_types:
            return "有公章，建议确认是否有发票专用章"
        elif "发票监制章" in seal_types:
            return "检测到发票监制章（预印），建议核实是否有发票专用章"
        else:
            return "未检测到标准印章，请人工核实"
