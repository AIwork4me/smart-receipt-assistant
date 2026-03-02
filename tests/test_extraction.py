"""信息提取测试"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestReceiptExtractionChain:
    """Receipt Extraction Chain 测试"""

    @patch("src.llm.ernie.ChatOpenAI")
    @patch("src.llm.ernie.PromptTemplate")
    def test_extract_success(self, mock_prompt, mock_chat):
        """测试提取成功"""
        from src.llm.ernie import ReceiptExtractionChain

        # 模拟 LLM 响应
        mock_response = Mock()
        mock_response.content = json.dumps({
            "receipt_type": "增值税发票",
            "invoice_code": "1234567890",
            "invoice_number": "12345678",
            "date": "2024-01-15",
            "buyer_name": "测试公司",
            "seller_name": "测试商家",
            "amount": "1000.00",
            "tax": "60.00",
            "total": "1060.00"
        })

        # 模拟链式调用
        mock_chain = Mock()
        mock_chain.invoke.return_value = mock_response

        # 模拟 PromptTemplate 的 __or__ 操作符
        mock_prompt_instance = Mock()
        mock_prompt_instance.__or__ = Mock(return_value=mock_chain)
        mock_prompt.return_value = mock_prompt_instance

        chain = ReceiptExtractionChain("test_key")
        result = chain.extract("测试OCR文本")

        assert result["receipt_type"] == "增值税发票"
        assert result["invoice_code"] == "1234567890"

    @patch("src.llm.ernie.ChatOpenAI")
    @patch("src.llm.ernie.PromptTemplate")
    def test_extract_with_json_block(self, mock_prompt, mock_chat):
        """测试带 JSON 代码块的响应"""
        from src.llm.ernie import ReceiptExtractionChain

        mock_response = Mock()
        mock_response.content = """```json
{
    "receipt_type": "火车票",
    "date": "2024-01-15",
    "total": "553.00"
}
```"""

        mock_chain = Mock()
        mock_chain.invoke.return_value = mock_response

        mock_prompt_instance = Mock()
        mock_prompt_instance.__or__ = Mock(return_value=mock_chain)
        mock_prompt.return_value = mock_prompt_instance

        chain = ReceiptExtractionChain("test_key")
        result = chain.extract("测试OCR文本")

        assert result["receipt_type"] == "火车票"
        assert result["total"] == "553.00"

    @patch("src.llm.ernie.ChatOpenAI")
    @patch("src.llm.ernie.PromptTemplate")
    def test_classify(self, mock_prompt, mock_chat):
        """测试分类"""
        from src.llm.ernie import ReceiptExtractionChain

        mock_response = Mock()
        mock_response.content = "增值税专用发票"

        mock_chain = Mock()
        mock_chain.invoke.return_value = mock_response

        mock_prompt_instance = Mock()
        mock_prompt_instance.__or__ = Mock(return_value=mock_chain)
        mock_prompt.return_value = mock_prompt_instance

        chain = ReceiptExtractionChain("test_key")
        result = chain.classify("测试OCR文本")

        assert "增值税" in result


class TestExtractionChain:
    """Extraction Chain 测试"""

    @patch("src.chains.extraction_chain.get_api_key")
    @patch("src.chains.extraction_chain.ReceiptExtractionChain")
    def test_extract_with_seals(self, mock_chain_class, mock_get_api_key):
        """测试带印章的提取"""
        from src.chains.extraction_chain import ExtractionChain

        mock_get_api_key.return_value = "test_key"
        mock_chain = Mock()
        mock_chain.extract.return_value = {
            "receipt_type": "增值税发票",
            "total": "1060.00"
        }
        mock_chain_class.return_value = mock_chain

        chain = ExtractionChain("test_key")
        seals = [{"type": "发票专用章", "url": "https://example.com/seal.png"}]
        result = chain.extract_with_seals("测试文本", seals)

        assert "seal_analysis" in result
        assert result["seal_analysis"]["has_invoice_seal"] is True

    def test_analyze_seals(self):
        """测试印章分析"""
        from src.chains.extraction_chain import ExtractionChain

        chain = ExtractionChain.__new__(ExtractionChain)

        seals = [
            {"type": "发票专用章"},
            {"type": "财务专用章"}
        ]
        analysis = chain._analyze_seals(seals)

        assert analysis["count"] == 2
        assert analysis["has_invoice_seal"] is True
        assert analysis["has_finance_seal"] is True


class TestValidators:
    """验证器测试"""

    def test_validate_amount_success(self):
        """测试金额验证成功"""
        from src.utils.validators import validate_amount

        result = validate_amount("1000.00", "60.00", "1060.00")
        assert result["is_valid"] is True

    def test_validate_amount_failure(self):
        """测试金额验证失败"""
        from src.utils.validators import validate_amount

        result = validate_amount("1000.00", "60.00", "2000.00")
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0

    def test_validate_date_future(self):
        """测试未来日期"""
        from src.utils.validators import validate_date

        result = validate_date("2099-01-01")
        assert "未来日期" in " ".join(result["issues"])

    def test_validate_date_format(self):
        """测试日期格式"""
        from src.utils.validators import validate_date

        result = validate_date("2024年01月15日")
        assert result["is_valid"] is True
        assert result["parsed_date"] == "2024-01-15"

    def test_validate_receipt(self):
        """测试票据验证"""
        from src.utils.validators import validate_receipt

        receipt = {
            "receipt_type": "增值税发票",
            "date": "2024-01-15",
            "invoice_code": "1234567890",
            "invoice_number": "12345678",
            "amount": "1000.00",
            "tax": "60.00",
            "total": "1060.00",
            "seals": [{"type": "发票专用章"}]
        }

        result = validate_receipt(receipt)
        assert result["is_valid"] is True
