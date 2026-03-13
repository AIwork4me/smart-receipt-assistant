"""Tests for LangChain Agent module."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.agents import create_receipt_agent, ReceiptAgentExecutor, RECEIPT_AGENT_PROMPT


class TestReceiptAgentExecutor:
    """Tests for ReceiptAgentExecutor."""

    def test_executor_initialization(self):
        """Test executor initializes correctly."""
        with patch("src.agents.receipt_agent.ChatOpenAI"):
            with patch("src.agents.receipt_agent.create_agent") as mock_create:
                mock_agent = MagicMock()
                mock_create.return_value = mock_agent

                executor = ReceiptAgentExecutor(
                    api_key="test_key",
                    verbose=True
                )

                assert executor.api_key == "test_key"
                assert executor.verbose is True
                assert len(executor.tools) == 3

    def test_executor_with_custom_llm(self):
        """Test executor with custom LLM."""
        with patch("src.agents.receipt_agent.create_agent") as mock_create:
            with patch("src.agents.receipt_agent.get_api_key") as mock_get_key:
                mock_get_key.return_value = "test_key"
                custom_llm = MagicMock()
                mock_create.return_value = MagicMock()

                executor = ReceiptAgentExecutor(llm=custom_llm)

                assert executor.llm == custom_llm

    def test_invoke(self):
        """Test invoking the agent."""
        with patch("src.agents.receipt_agent.ChatOpenAI"):
            with patch("src.agents.receipt_agent.create_agent") as mock_create:
                mock_agent = MagicMock()
                mock_agent.invoke.return_value = {"output": "test result"}
                mock_create.return_value = mock_agent

                executor = ReceiptAgentExecutor(api_key="test_key")
                result = executor.invoke("Process this receipt")

                mock_agent.invoke.assert_called_once_with(
                    {"input": "Process this receipt"}
                )

    def test_process(self):
        """Test process method."""
        with patch("src.agents.receipt_agent.ChatOpenAI"):
            with patch("src.agents.receipt_agent.create_agent") as mock_create:
                mock_agent = MagicMock()
                mock_agent.invoke.return_value = {"output": "processed"}
                mock_create.return_value = mock_agent

                executor = ReceiptAgentExecutor(api_key="test_key")
                result = executor.process("invoice.jpg")

                # Should call invoke with proper prompt
                call_args = mock_agent.invoke.call_args
                assert "invoice.jpg" in call_args[0][0]["input"]


class TestCreateReceiptAgent:
    """Tests for create_receipt_agent factory function."""

    def test_create_agent_default(self):
        """Test creating agent with default settings."""
        with patch("src.agents.receipt_agent.ChatOpenAI"):
            with patch("src.agents.receipt_agent.create_agent") as mock_create:
                with patch("src.agents.receipt_agent.get_api_key") as mock_get_key:
                    mock_get_key.return_value = "test_key"
                    mock_create.return_value = MagicMock()

                    agent = create_receipt_agent()

                    assert isinstance(agent, ReceiptAgentExecutor)

    def test_create_agent_with_options(self):
        """Test creating agent with custom options."""
        with patch("src.agents.receipt_agent.ChatOpenAI"):
            with patch("src.agents.receipt_agent.create_agent") as mock_create:
                mock_create.return_value = MagicMock()

                agent = create_receipt_agent(
                    api_key="custom_key",
                    paddleocr_api_key="ocr_key",
                    verbose=True
                )

                assert agent.api_key == "custom_key"
                assert agent.verbose is True


class TestAgentPrompt:
    """Tests for agent prompt configuration."""

    def test_prompt_content(self):
        """Test prompt contains required elements."""
        assert "receipt" in RECEIPT_AGENT_PROMPT.lower()
        assert "OCR" in RECEIPT_AGENT_PROMPT
        assert "extract" in RECEIPT_AGENT_PROMPT.lower()
        assert "classify" in RECEIPT_AGENT_PROMPT.lower()


class TestAgentTools:
    """Tests for agent tool integration."""

    def test_tools_registered(self):
        """Test all tools are registered with the agent."""
        with patch("src.agents.receipt_agent.ChatOpenAI"):
            with patch("src.agents.receipt_agent.create_agent") as mock_create:
                mock_create.return_value = MagicMock()

                executor = ReceiptAgentExecutor(api_key="test_key")

                # Check tool names
                tool_names = [t.name for t in executor.tools]
                assert "receipt_ocr" in tool_names
                assert "receipt_extraction" in tool_names
                assert "receipt_classification" in tool_names


class TestAgentIntegration:
    """Integration tests for agent functionality."""

    @patch("src.agents.receipt_agent.ChatOpenAI")
    @patch("src.agents.receipt_agent.create_agent")
    @patch("src.agents.receipt_agent.get_api_key")
    def test_full_agent_workflow(
        self,
        mock_get_key,
        mock_create,
        mock_llm_class
    ):
        """Test complete agent workflow."""
        # Setup mocks
        mock_get_key.return_value = "test_key"
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "output": "Receipt processed successfully. Type: VAT Invoice, Total: 1000.00"
        }
        mock_create.return_value = mock_agent

        # Create agent
        agent = create_receipt_agent(verbose=True)

        # Process receipt
        result = agent.process("test_invoice.jpg")

        # Verify
        assert "output" in result
        assert "VAT Invoice" in result["output"]

    def test_batch_processing(self):
        """Test batch processing with agent."""
        with patch("src.agents.receipt_agent.ChatOpenAI"):
            with patch("src.agents.receipt_agent.create_agent") as mock_create:
                mock_create.return_value = MagicMock()

                executor = ReceiptAgentExecutor(api_key="test_key")

                # Mock the process method
                executor.process = MagicMock(return_value={"output": "processed"})

                # Batch process
                results = executor.batch_process(["file1.jpg", "file2.jpg"])

                assert len(results) == 2
                assert executor.process.call_count == 2
