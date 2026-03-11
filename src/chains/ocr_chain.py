"""OCR 处理链 - 使用官方 langchain-paddleocr"""
from typing import Optional, List

# 必须在导入 langchain_paddleocr 之前设置兼容层
from ..langchain_compat import setup_langchain_compat
setup_langchain_compat()

from langchain_paddleocr import PaddleOCRVLLoader
from pydantic import SecretStr

from ..config import get_paddleocr_token, PADDLEOCR_API_URL
from ..utils.seal_extractor import extract_seals_from_response


class OCRChain:
    """OCR 处理链 - 基于官方 PaddleOCRVLLoader

    负责调用 PaddleOCR-VL-1.5 进行票据识别，支持印章识别。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None
    ):
        """
        Args:
            api_key: Access Token，默认从环境变量读取
            api_url: API URL，默认从配置读取
        """
        if api_key:
            self.access_token = SecretStr(api_key)
        else:
            self.access_token = get_paddleocr_token()
        self.api_url = api_url or PADDLEOCR_API_URL

    def process(self, file_path: str, enable_seal: bool = True) -> dict:
        """处理票据图片

        Args:
            file_path: 图片/PDF 路径
            enable_seal: 是否启用印章识别

        Returns:
            处理结果，包含:
            - text: OCR 识别的文本
            - seals: 印章信息列表
            - raw_result: 原始 API 响应
            - documents: LangChain Document 对象列表
        """
        # 使用官方 PaddleOCRVLLoader
        loader = PaddleOCRVLLoader(
            file_path=file_path,
            api_url=self.api_url,
            access_token=self.access_token,
            use_seal_recognition=enable_seal,
            use_layout_detection=True,
        )

        # 加载文档
        docs = loader.load()

        # 合并所有页面文本
        text = "\n\n".join(doc.page_content for doc in docs)

        # 从原始响应提取印章信息
        raw_response = docs[0].metadata.get("paddleocr_vl_raw_response", {}) if docs else {}
        seals = extract_seals_from_response(raw_response)

        return {
            "text": text,
            "seals": seals,
            "raw_result": raw_response,
            "documents": docs  # LangChain Document 对象
        }

    def batch_process(self, file_paths: List[str], enable_seal: bool = True) -> List[dict]:
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
