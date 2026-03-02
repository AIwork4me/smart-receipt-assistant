"""PaddleOCR-VL-1.5 云端 API 封装"""
import base64
import requests
from typing import Optional, Tuple
from pathlib import Path


class PaddleOCRVL:
    """PaddleOCR-VL-1.5 云端 API 封装 (AIStudio)

    特色功能：
    - 票据文字识别
    - 印章识别（独有功能）
    - 版面分析
    - 支持 PDF 和图片格式（自动检测）
    """

    API_URL = "https://q6mbb0r0t8m9q4pf.aistudio-app.com/layout-parsing"

    # 文件类型映射（根据 API 文档）
    FILE_TYPE_PDF = 0     # PDF 文档
    FILE_TYPE_IMAGE = 1   # 图片文件

    # 支持的文件扩展名
    SUPPORTED_PDF_EXTENSIONS = {".pdf"}
    SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
    SUPPORTED_EXTENSIONS = SUPPORTED_PDF_EXTENSIONS | SUPPORTED_IMAGE_EXTENSIONS

    def __init__(self, api_key: str):
        """
        Args:
            api_key: AIStudio Access Token
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"token {api_key}",
            "Content-Type": "application/json"
        }

    def _get_file_type(self, file_path: str) -> Tuple[int, str]:
        """根据文件扩展名自动判断文件类型

        Args:
            file_path: 文件路径

        Returns:
            (文件类型代码, 文件类型描述)
            文件类型代码: 0=PDF, 1=图片

        Raises:
            ValueError: 不支持的文件格式
        """
        ext = Path(file_path).suffix.lower()

        if ext in self.SUPPORTED_PDF_EXTENSIONS:
            return self.FILE_TYPE_PDF, "PDF文档"
        elif ext in self.SUPPORTED_IMAGE_EXTENSIONS:
            return self.FILE_TYPE_IMAGE, "图片"
        else:
            raise ValueError(
                f"不支持的文件格式: {ext}\n"
                f"支持的格式: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

    def _validate_file(self, file_path: str) -> Path:
        """验证文件是否存在且可读

        Args:
            file_path: 文件路径

        Returns:
            Path 对象

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件不可读
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        if not path.is_file():
            raise ValueError(f"不是有效文件: {file_path}")
        if path.stat().st_size == 0:
            raise ValueError(f"文件为空: {file_path}")
        return path

    def recognize(
        self,
        file_path: str,
        use_seal_recognition: bool = True,
        use_layout_detection: bool = True
    ) -> dict:
        """
        识别票据图片或 PDF（自动检测文件类型）

        Args:
            file_path: 图片/PDF 路径
            use_seal_recognition: 是否启用印章识别（特色功能）
            use_layout_detection: 是否启用版面检测

        Returns:
            识别结果字典，包含 markdown 文本和印章信息

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的文件格式
        """
        # 验证文件
        path = self._validate_file(file_path)

        # 自动检测文件类型
        file_type, type_desc = self._get_file_type(file_path)

        # 读取并编码文件
        with open(path, "rb") as file:
            file_data = base64.b64encode(file.read()).decode("ascii")

        payload = {
            "file": file_data,
            "fileType": file_type,  # 自动检测: 0=PDF, 1=图片
            "useSealRecognition": use_seal_recognition,
            "useLayoutDetection": use_layout_detection,
            "useDocOrientationClassify": False,
            "useDocUnwarping": False,
            "useChartRecognition": False,
            "useOcrForImageBlock": False,
            "mergeTables": True,
            "layoutNms": True,
            "promptLabel": "ocr",
            "temperature": 0,
        }

        response = requests.post(
            self.API_URL,
            json=payload,
            headers=self.headers,
            timeout=120  # PDF 可能需要更长时间
        )
        response.raise_for_status()

        return response.json().get("result", {})

    def extract_text(self, result: dict) -> str:
        """从识别结果中提取纯文本

        Args:
            result: recognize() 返回的结果

        Returns:
            合并后的文本内容
        """
        texts = []
        layout_results = result.get("layoutParsingResults", [])

        for res in layout_results:
            markdown = res.get("markdown", {})
            text = markdown.get("text", "")
            if text:
                texts.append(text)

        return "\n\n".join(texts)

    def extract_seals(self, result: dict) -> list:
        """从识别结果中提取印章信息

        Args:
            result: recognize() 返回的结果

        Returns:
            印章信息列表，包含印章名称、图片URL、页码等
        """
        seals = []
        layout_results = result.get("layoutParsingResults", [])

        for i, res in enumerate(layout_results):
            # 获取 markdown 文本用于分析印章类型
            markdown = res.get("markdown", {})
            full_text = markdown.get("text", "")

            # 方法1: 从 outputImages 中提取
            output_images = res.get("outputImages", {})
            for img_name, img_url in output_images.items():
                if "seal" in img_name.lower():
                    seals.append({
                        "name": img_name,
                        "url": img_url,
                        "page": i,
                        "type": self._classify_seal(img_name, full_text)
                    })

            # 方法2: 从 markdown.images 中提取印章图片
            images = markdown.get("images", {})
            for img_name, img_url in images.items():
                if "seal" in img_name.lower():
                    seals.append({
                        "name": img_name,
                        "url": img_url,
                        "page": i,
                        "type": self._classify_seal(img_name, full_text)
                    })

        return seals

    def _classify_seal(self, name: str, surrounding_text: str = "") -> str:
        """根据名称和周围文本判断印章类型

        Args:
            name: 印章图片名称
            surrounding_text: 印章周围的 OCR 文本

        Returns:
            印章类型
        """
        name_lower = name.lower()
        combined = f"{name} {surrounding_text}".lower()

        # 发票专用章
        if "invoice" in name_lower or "发票专用章" in surrounding_text or "发票章" in surrounding_text:
            return "发票专用章"

        # 财务专用章
        if "finance" in name_lower or "财务专用章" in surrounding_text or "财务章" in surrounding_text:
            return "财务专用章"

        # 公章
        if "official" in name_lower or "公章" in surrounding_text:
            return "公章"

        # 发票监制章（预印在发票上）
        if "监制章" in surrounding_text or "监督章" in surrounding_text:
            return "发票监制章"

        # 合同章
        if "合同章" in surrounding_text:
            return "合同章"

        return "其他印章"

    def get_full_result(self, file_path: str) -> dict:
        """获取完整识别结果（包含文本和印章）

        Args:
            file_path: 图片路径

        Returns:
            包含 text、seals、raw_result 的字典
        """
        result = self.recognize(file_path)

        return {
            "text": self.extract_text(result),
            "seals": self.extract_seals(result),
            "raw_result": result
        }
