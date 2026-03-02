"""分类链"""
from typing import Optional
from ..llm import ReceiptExtractionChain
from ..config import get_api_key


# 报销类别映射
REIMBURSEMENT_CATEGORIES = {
    "增值税专用发票": "办公费用",
    "增值税普通发票": "办公费用",
    "火车票": "交通费",
    "出租车票": "交通费",
    "住宿发票": "住宿费",
    "餐饮发票": "餐饮费",
    "其他": "其他"
}


class ClassificationChain:
    """分类链

    负责对票据进行智能分类
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: AIStudio API Key，默认从环境变量读取
        """
        self.chain = ReceiptExtractionChain(api_key or get_api_key())

    def classify(self, ocr_text: str) -> dict:
        """分类票据

        Args:
            ocr_text: OCR 识别的文本

        Returns:
            分类结果，包含票据类型和报销类别
        """
        receipt_type = self.chain.classify(ocr_text)
        category = REIMBURSEMENT_CATEGORIES.get(receipt_type, "其他")

        return {
            "receipt_type": receipt_type,
            "reimbursement_category": category
        }

    def classify_batch(self, ocr_texts: list) -> list:
        """批量分类票据

        Args:
            ocr_texts: OCR 文本列表

        Returns:
            分类结果列表
        """
        return [self.classify(text) for text in ocr_texts]

    def get_category_summary(self, classification_results: list) -> dict:
        """获取分类统计

        Args:
            classification_results: 分类结果列表

        Returns:
            各类别数量统计
        """
        summary = {}
        for result in classification_results:
            category = result.get("reimbursement_category", "其他")
            summary[category] = summary.get(category, 0) + 1

        return summary
