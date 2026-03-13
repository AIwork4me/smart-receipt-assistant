"""Receipt Classification Tool - LangChain Tool Implementation

This tool wraps the ClassificationChain functionality to provide a LangChain-compatible
interface for classifying receipts and determining reimbursement categories.
"""

from typing import Optional, Type, Dict, Any, List

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from ..chains.classification_chain import ClassificationChain


class ReceiptClassificationInput(BaseModel):
    """Input schema for Receipt Classification Tool.

    Attributes:
        ocr_text: OCR recognized text from the receipt.
    """
    ocr_text: str = Field(
        ...,
        description="OCR recognized text content from the receipt document."
    )


class ReceiptClassificationTool(BaseTool):
    """LangChain Tool for Receipt Classification.

    This tool classifies receipts and determines the appropriate reimbursement
    category based on the receipt type. It uses ERINE for intelligent classification.

    Classification mapping:
    - VAT Special Invoice -> Office Expenses
    - VAT Normal Invoice -> Office Expenses
    - Train Ticket -> Transportation
    - Taxi Receipt -> Transportation
    - Hotel Invoice -> Accommodation
    - Others -> Others

    The tool wraps ClassificationChain which uses LangChain's LCEL for processing.

    Attributes:
        name: Tool name for LangChain agent integration.
        description: Tool description for agent decision making.
        args_schema: Pydantic model for input validation.

    Example:
        >>> tool = ReceiptClassificationTool()
        >>> result = tool.invoke({
        ...     "ocr_text": "火车票 G1234 北京南-上海虹桥..."
        ... })
        >>> print(result["receipt_type"])  # "火车票"
        >>> print(result["reimbursement_category"])  # "交通费"
    """

    name: str = "receipt_classification"
    description: str = """Classify receipt type and determine reimbursement category.

    Input: OCR text from receipt
    Output: Receipt type and reimbursement category

    Use this tool to determine what type of receipt this is and how it should be
    categorized for reimbursement purposes.

    Categories include: Office Expenses, Transportation, Accommodation, Dining, Others.

    Powered by ERINE (Baidu's LLM) via LangChain.
    """
    args_schema: Type[BaseModel] = ReceiptClassificationInput

    # Tool configuration
    api_key: Optional[str] = None
    _chain: Optional[ClassificationChain] = None

    def __init__(
        self,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Initialize the Receipt Classification Tool.

        Args:
            api_key: AIStudio API key for ERINE. If not provided, reads from environment.
            **kwargs: Additional arguments passed to BaseTool.
        """
        super().__init__(**kwargs)
        self.api_key = api_key

    @property
    def chain(self) -> ClassificationChain:
        """Lazy initialization of classification chain."""
        if self._chain is None:
            self._chain = ClassificationChain(api_key=self.api_key)
        return self._chain

    def _run(
        self,
        ocr_text: str,
        run_manager: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Classify the receipt and determine reimbursement category.

        Args:
            ocr_text: OCR recognized text from the receipt.
            run_manager: Optional run manager for callbacks (unused).

        Returns:
            Dictionary containing:
            - receipt_type: Type of the receipt (e.g., "增值税专用发票", "火车票")
            - reimbursement_category: Category for reimbursement (e.g., "交通费", "办公费用")

        Raises:
            ValueError: If OCR text is empty or invalid.
            Exception: If classification fails.
        """
        return self.chain.classify(ocr_text)

    async def _arun(
        self,
        ocr_text: str,
        run_manager: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Async execution (falls back to sync for now).

        Args:
            ocr_text: OCR recognized text from the receipt.
            run_manager: Optional run manager for callbacks.

        Returns:
            Same as _run method.
        """
        return self._run(ocr_text, run_manager)

    def classify_batch(
        self,
        ocr_texts: List[str]
    ) -> List[Dict[str, Any]]:
        """Classify multiple receipts in batch.

        Args:
            ocr_texts: List of OCR text strings.

        Returns:
            List of classification results.
        """
        return self.chain.classify_batch(ocr_texts)

    def get_category_summary(
        self,
        classification_results: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Get summary statistics of classification results.

        Args:
            classification_results: List of classification results.

        Returns:
            Dictionary mapping category names to counts.
        """
        return self.chain.get_category_summary(classification_results)
