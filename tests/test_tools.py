"""Tests for LangChain Tools module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.tools import (
    ReceiptOCRTool,
    ReceiptExtractionTool,
    ReceiptClassificationTool,
)
from src.tools.ocr_tool import ReceiptOCRInput
from src.tools.extraction_tool import ReceiptExtractionInput
from src.tools.classification_tool import ReceiptClassificationInput


class TestReceiptOCRTool:
    """Tests for ReceiptOCRTool."""

    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = ReceiptOCRTool()
        assert tool.name == "receipt_ocr"
        assert "Recognize text" in tool.description
        assert tool.args_schema == ReceiptOCRInput

    def test_tool_with_custom_config(self):
        """Test tool with custom API configuration."""
        tool = ReceiptOCRTool(
            api_key="custom_key",
            api_url="https://custom.api.url"
        )
        assert tool.api_key == "custom_key"
        assert tool.api_url == "https://custom.api.url"

    def test_input_schema_validation(self):
        """Test input schema validates correctly."""
        # Valid input
        input_data = ReceiptOCRInput(file_path="test.jpg", enable_seal=True)
        assert input_data.file_path == "test.jpg"
        assert input_data.enable_seal is True

        # Default enable_seal
        input_data = ReceiptOCRInput(file_path="test.jpg")
        assert input_data.enable_seal is True

    @patch("src.tools.ocr_tool.OCRChain")
    def test_run_success(self, mock_chain_class):
        """Test successful OCR execution."""
        # Setup mock
        mock_chain = MagicMock()
        mock_chain.process.return_value = {
            "text": "Sample OCR text",
            "seals": [{"type": "发票专用章"}],
            "raw_result": {},
            "documents": []
        }
        mock_chain_class.return_value = mock_chain

        # Execute
        tool = ReceiptOCRTool()
        result = tool._run(file_path="test.jpg", enable_seal=True)

        # Verify
        assert result["text"] == "Sample OCR text"
        assert len(result["seals"]) == 1
        mock_chain.process.assert_called_once_with("test.jpg", enable_seal=True)


class TestReceiptExtractionTool:
    """Tests for ReceiptExtractionTool."""

    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = ReceiptExtractionTool()
        assert tool.name == "receipt_extraction"
        assert "Extract structured" in tool.description
        assert tool.args_schema == ReceiptExtractionInput

    def test_input_schema_validation(self):
        """Test input schema validates correctly."""
        # Valid input
        input_data = ReceiptExtractionInput(
            ocr_text="Sample OCR text",
            seals=[{"type": "发票专用章"}]
        )
        assert input_data.ocr_text == "Sample OCR text"
        assert len(input_data.seals) == 1

        # Optional seals
        input_data = ReceiptExtractionInput(ocr_text="Sample OCR text")
        assert input_data.seals is None

    @patch("src.tools.extraction_tool.ExtractionChain")
    def test_run_without_seals(self, mock_chain_class):
        """Test extraction without seals."""
        # Setup mock
        mock_chain = MagicMock()
        mock_chain.extract.return_value = {
            "receipt_type": "增值税专用发票",
            "invoice_number": "12345678"
        }
        mock_chain_class.return_value = mock_chain

        # Execute
        tool = ReceiptExtractionTool()
        result = tool._run(ocr_text="Sample text", seals=None)

        # Verify
        assert result["receipt_type"] == "增值税专用发票"
        mock_chain.extract.assert_called_once_with("Sample text")

    @patch("src.tools.extraction_tool.ExtractionChain")
    def test_run_with_seals(self, mock_chain_class):
        """Test extraction with seals."""
        # Setup mock
        mock_chain = MagicMock()
        mock_chain.extract_with_seals.return_value = {
            "receipt_type": "增值税专用发票",
            "seal_analysis": {"count": 1}
        }
        mock_chain_class.return_value = mock_chain

        # Execute
        tool = ReceiptExtractionTool()
        seals = [{"type": "发票专用章"}]
        result = tool._run(ocr_text="Sample text", seals=seals)

        # Verify
        assert "seal_analysis" in result
        mock_chain.extract_with_seals.assert_called_once_with("Sample text", seals)


class TestReceiptClassificationTool:
    """Tests for ReceiptClassificationTool."""

    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = ReceiptClassificationTool()
        assert tool.name == "receipt_classification"
        assert "Classify receipt" in tool.description
        assert tool.args_schema == ReceiptClassificationInput

    def test_input_schema_validation(self):
        """Test input schema validates correctly."""
        input_data = ReceiptClassificationInput(ocr_text="Sample text")
        assert input_data.ocr_text == "Sample text"

    @patch("src.tools.classification_tool.ClassificationChain")
    def test_run_success(self, mock_chain_class):
        """Test successful classification."""
        # Setup mock
        mock_chain = MagicMock()
        mock_chain.classify.return_value = {
            "receipt_type": "火车票",
            "reimbursement_category": "交通费"
        }
        mock_chain_class.return_value = mock_chain

        # Execute
        tool = ReceiptClassificationTool()
        result = tool._run(ocr_text="火车票 G1234...")

        # Verify
        assert result["receipt_type"] == "火车票"
        assert result["reimbursement_category"] == "交通费"

    @patch("src.tools.classification_tool.ClassificationChain")
    def test_classify_batch(self, mock_chain_class):
        """Test batch classification."""
        # Setup mock
        mock_chain = MagicMock()
        mock_chain.classify_batch.return_value = [
            {"receipt_type": "火车票", "reimbursement_category": "交通费"},
            {"receipt_type": "增值税专用发票", "reimbursement_category": "办公费用"}
        ]
        mock_chain_class.return_value = mock_chain

        # Execute
        tool = ReceiptClassificationTool()
        results = tool.classify_batch(["text1", "text2"])

        # Verify
        assert len(results) == 2
        assert results[0]["receipt_type"] == "火车票"


class TestToolsIntegration:
    """Integration tests for tools working together."""

    @patch("src.tools.ocr_tool.OCRChain")
    @patch("src.tools.extraction_tool.ExtractionChain")
    @patch("src.tools.classification_tool.ClassificationChain")
    def test_full_pipeline(
        self,
        mock_classify_chain,
        mock_extract_chain,
        mock_ocr_chain
    ):
        """Test full processing pipeline with all tools."""
        # Setup mocks
        mock_ocr = MagicMock()
        mock_ocr.process.return_value = {
            "text": "发票内容",
            "seals": [{"type": "发票专用章"}],
            "raw_result": {},
            "documents": []
        }
        mock_ocr_chain.return_value = mock_ocr

        mock_extract = MagicMock()
        mock_extract.extract_with_seals.return_value = {
            "receipt_type": "增值税专用发票",
            "total": "1000.00"
        }
        mock_extract_chain.return_value = mock_extract

        mock_classify = MagicMock()
        mock_classify.classify.return_value = {
            "receipt_type": "增值税专用发票",
            "reimbursement_category": "办公费用"
        }
        mock_classify_chain.return_value = mock_classify

        # Execute pipeline
        ocr_tool = ReceiptOCRTool()
        extract_tool = ReceiptExtractionTool()
        classify_tool = ReceiptClassificationTool()

        # Step 1: OCR
        ocr_result = ocr_tool._run(file_path="invoice.jpg", enable_seal=True)

        # Step 2: Classification
        classify_result = classify_tool._run(ocr_text=ocr_result["text"])

        # Step 3: Extraction
        extract_result = extract_tool._run(
            ocr_text=ocr_result["text"],
            seals=ocr_result["seals"]
        )

        # Verify pipeline results
        assert ocr_result["text"] == "发票内容"
        assert classify_result["reimbursement_category"] == "办公费用"
        assert extract_result["total"] == "1000.00"
