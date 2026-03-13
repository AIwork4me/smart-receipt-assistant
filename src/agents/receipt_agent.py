"""Receipt Processing Agent - LangChain Agent Implementation

This module provides a LangChain Agent that can intelligently process receipts
by orchestrating OCR, extraction, and classification tools.

Note: Uses LangChain 1.2+ API with create_agent.
"""

from typing import Optional, List, Dict, Any

# IMPORTANT: Import langchain agents BEFORE any compat layer is triggered
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI

from ..tools import ReceiptOCRTool, ReceiptExtractionTool, ReceiptClassificationTool
from ..config import get_api_key

# AIStudio ERINE Configuration
ERINE_BASE_URL = "https://aistudio.baidu.com/llm/lmapi/v3"
ERINE_MODEL = "ernie-4.5-turbo-128k-preview"

# Default agent prompt template
RECEIPT_AGENT_PROMPT = """You are an intelligent receipt processing assistant.

Your capabilities include:
1. **OCR Recognition**: Extract text and detect seals from receipt images/PDFs
2. **Information Extraction**: Parse structured data from OCR text
3. **Classification**: Categorize receipts and determine reimbursement types

When processing receipts:
- Always start with OCR to get the text content
- Then extract structured information
- Finally classify the receipt for reimbursement

If the user provides a file path, use the receipt_ocr tool first.
If the user provides OCR text directly, use receipt_extraction tool.

Use the tools to help the user process receipts. Always explain what you're doing.

Remember: You must use the tools to process receipts, do not make up information.
"""

# LangChain prompt template for agent
AGENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", RECEIPT_AGENT_PROMPT),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


class ReceiptAgentExecutor:
    """High-level wrapper for Receipt Processing Agent.

    This class provides a convenient interface for using the receipt agent
    without needing to understand LangChain agent internals.

    Attributes:
        tools: List of available tools.
        llm: The language model used.
        agent: The underlying LangChain agent.

    Example:
        >>> from src.agents import ReceiptAgentExecutor
        >>> agent = ReceiptAgentExecutor(api_key="your-api-key")
        >>> result = agent.process("invoice.jpg")
        >>> print(result["receipt_type"])
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        paddleocr_api_key: Optional[str] = None,
        paddleocr_api_url: Optional[str] = None,
        llm: Optional[BaseLanguageModel] = None,
        verbose: bool = False,
        max_iterations: int = 10,
    ):
        """Initialize the Receipt Agent.

        Args:
            api_key: AIStudio API key for ERINE LLM. Reads from env if not provided.
            paddleocr_api_key: PaddleOCR API token. Reads from env if not provided.
            paddleocr_api_url: PaddleOCR API URL.
            llm: Custom LLM instance. If provided, api_key is ignored.
            verbose: Whether to print agent reasoning steps.
            max_iterations: Maximum number of tool calls per request.
        """
        self.api_key = api_key or get_api_key()
        self.verbose = verbose
        self.max_iterations = max_iterations

        # Initialize tools
        self.tools: List[Any] = [
            ReceiptOCRTool(api_key=paddleocr_api_key, api_url=paddleocr_api_url),
            ReceiptExtractionTool(api_key=self.api_key),
            ReceiptClassificationTool(api_key=self.api_key),
        ]

        # Initialize LLM
        if llm is None:
            self.llm = ChatOpenAI(
                model=ERINE_MODEL,
                api_key=self.api_key,
                base_url=ERINE_BASE_URL,
                temperature=0.1,
            )
        else:
            self.llm = llm

        # Create agent using LangChain 1.2+ API
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            prompt=RECEIPT_AGENT_PROMPT,
        )

    def invoke(self, input_text: str) -> Dict[str, Any]:
        """Process a request using the agent.

        Args:
            input_text: Natural language request or file path.

        Returns:
            Agent response with output and intermediate steps.
        """
        result = self.agent.invoke({"input": input_text})
        return result

    def process(self, file_path: str) -> Dict[str, Any]:
        """Process a receipt file (convenience method).

        This method provides a simpler interface for processing receipt files.
        It directly invokes the agent with appropriate context.

        Args:
            file_path: Path to the receipt file.

        Returns:
            Processed receipt information.
        """
        prompt = f"Please process this receipt file: {file_path}"
        return self.invoke(prompt)

    def batch_process(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Process multiple receipt files.

        Args:
            file_paths: List of file paths.

        Returns:
            List of processing results.
        """
        return [self.process(fp) for fp in file_paths]


def create_receipt_agent(
    api_key: Optional[str] = None,
    paddleocr_api_key: Optional[str] = None,
    paddleocr_api_url: Optional[str] = None,
    llm: Optional[BaseLanguageModel] = None,
    verbose: bool = False,
) -> ReceiptAgentExecutor:
    """Factory function to create a Receipt Processing Agent.

    This is the recommended way to create a receipt agent instance.

    Args:
        api_key: AIStudio API key for ERINE LLM.
        paddleocr_api_key: PaddleOCR API token.
        paddleocr_api_url: PaddleOCR API URL.
        llm: Custom LLM instance (overrides api_key).
        verbose: Whether to print agent reasoning.

    Returns:
        Configured ReceiptAgentExecutor instance.

    Example:
        >>> agent = create_receipt_agent(verbose=True)
        >>> result = agent.process("invoice.jpg")
        >>> print(result)

    Example with custom LLM:
        >>> from langchain_openai import ChatOpenAI
        >>> llm = ChatOpenAI(model="gpt-4")
        >>> agent = create_receipt_agent(llm=llm)
    """
    return ReceiptAgentExecutor(
        api_key=api_key,
        paddleocr_api_key=paddleocr_api_key,
        paddleocr_api_url=paddleocr_api_url,
        llm=llm,
        verbose=verbose,
    )
