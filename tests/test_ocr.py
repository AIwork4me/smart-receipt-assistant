"""OCR 模块测试"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import base64


class TestPaddleOCRVL:
    """PaddleOCR VL 测试"""

    def test_init(self):
        """测试初始化"""
        from src.ocr.paddle_ocr import PaddleOCRVL

        ocr = PaddleOCRVL("test_api_key")
        assert ocr.api_key == "test_api_key"
        assert "token" in ocr.headers["Authorization"]

    @patch("src.ocr.paddle_ocr.requests.post")
    def test_recognize_success(self, mock_post):
        """测试识别成功"""
        from src.ocr.paddle_ocr import PaddleOCRVL

        # 模拟响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "result": {
                "layoutParsingResults": [
                    {
                        "markdown": {
                            "text": "发票代码：1234567890\n发票号码：12345678"
                        },
                        "outputImages": {
                            "seal_1": "https://example.com/seal1.png"
                        }
                    }
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # 创建临时图片文件
        import tempfile
        import os
        from PIL import Image

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = Image.new("RGB", (100, 100), color="white")
            img.save(f.name)
            temp_path = f.name

        try:
            ocr = PaddleOCRVL("test_api_key")
            result = ocr.recognize(temp_path)

            assert "layoutParsingResults" in result
            mock_post.assert_called_once()

        finally:
            os.unlink(temp_path)

    def test_extract_text(self):
        """测试文本提取"""
        from src.ocr.paddle_ocr import PaddleOCRVL

        ocr = PaddleOCRVL("test_api_key")
        result = {
            "layoutParsingResults": [
                {"markdown": {"text": "第一段文本"}},
                {"markdown": {"text": "第二段文本"}}
            ]
        }

        text = ocr.extract_text(result)
        assert "第一段文本" in text
        assert "第二段文本" in text

    def test_extract_seals(self):
        """测试印章提取"""
        from src.ocr.paddle_ocr import PaddleOCRVL

        ocr = PaddleOCRVL("test_api_key")
        result = {
            "layoutParsingResults": [
                {
                    "outputImages": {
                        "seal_finance": "https://example.com/finance_seal.png",
                        "seal_official": "https://example.com/official_seal.png",
                        "other_image": "https://example.com/other.png"
                    }
                }
            ]
        }

        seals = ocr.extract_seals(result)
        assert len(seals) == 2
        assert seals[0]["type"] in ["财务专用章", "公章", "其他印章"]

    def test_classify_seal(self):
        """测试印章分类"""
        from src.ocr.paddle_ocr import PaddleOCRVL

        ocr = PaddleOCRVL("test_api_key")

        assert ocr._classify_seal("seal_finance") == "财务专用章"
        assert ocr._classify_seal("seal_invoice") == "发票专用章"
        assert ocr._classify_seal("seal_official") == "公章"
        assert ocr._classify_seal("unknown_seal") == "其他印章"


class TestOCRChain:
    """OCR Chain 测试"""

    @patch("src.chains.ocr_chain.PaddleOCRVLLoader")
    def test_process(self, mock_loader_class):
        """测试处理流程 - 使用 langchain-paddleocr"""
        from src.chains.ocr_chain import OCRChain

        # 创建模拟的 Document 对象
        mock_doc = MagicMock()
        mock_doc.page_content = "发票代码：1234567890\n发票号码：12345678"
        mock_doc.metadata = {
            "paddleocr_vl_raw_response": {
                "result": {
                    "layoutParsingResults": [
                        {
                            "markdown": {"text": "发票代码：1234567890"},
                            "outputImages": {}
                        }
                    ]
                }
            }
        }

        # 设置 mock loader
        mock_loader = MagicMock()
        mock_loader.load.return_value = [mock_doc]
        mock_loader_class.return_value = mock_loader

        chain = OCRChain(api_key="test_key")
        result = chain.process("test.jpg")

        assert "发票代码" in result["text"]
        assert "seals" in result
        assert "documents" in result
