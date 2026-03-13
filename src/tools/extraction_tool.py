"""Receipt Extraction Tool - LangChain Tool Implementation

This tool wraps the ExtractionChain functionality to provide a LangChain-compatible
interface for extracting structured information from OCR text.
"""

from typing import Optional, Type, Dict, Any, List

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from ..chains.extraction_chain import ExtractionChain


class ReceiptExtractionInput(BaseModel):
    """Input schema for Receipt Extraction Tool.

    Attributes:
        ocr_text: OCR recognized text from the receipt.
        seals: Optional list of detected seals for analysis.
    """
    ocr_text: str = Field(
        ...,
        description="OCR recognized text content from the receipt document."
    )
    seals: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional list of detected seals. If provided, seal analysis will be included."
    )


class ReceiptExtractionTool(BaseTool):
    """LangChain Tool for Receipt Information Extraction.

    This tool extracts structured information from OCR text using ERINE
    (Baidu's large language model). It can identify:
    - Receipt type (VAT invoice, train ticket, taxi receipt, etc.)
    - Invoice code and number
    - Date, amount, tax, total
    - Buyer and seller information
    - Seal analysis (if seals are provided)

    The tool wraps ExtractionChain which uses LangChain's LCEL for processing.

    Attributes:
        name: Tool name for LangChain agent integration.
        description: Tool description for agent decision making.
        args_schema: Pydantic model for input validation.

    Example:
        >>> tool = ReceiptExtractionTool()
        >>> result = tool.invoke({
        ...     "ocr_text": "增值税专用发票 发票代码: 1100...",
        ...     "seals": [{"type": "发票专用章"}]
        ... })
        >>> print(result["receipt_type"])  # "增值税专用发票"
    """

    name: str = "receipt_extraction"
    description: str = """Extract structured information from receipt OCR text.

    Input: OCR text from receipt, optional seal information
    Output: Structured receipt data including type, amounts, parties, etc.

    Use this tool after receipt_ocr to extract structured data from the recognized text.
    Returns information like receipt type, invoice code/number, date, amounts,
    buyer/seller info, and seal analysis.

    Powered by ERINE (Baidu's LLM) via LangChain.
    """
    args_schema: Type[BaseModel] = ReceiptExtractionInput

    # Tool configuration
    api_key: Optional[str] = None
    _chain: Optional[ExtractionChain] = None

    def __init__(
        self,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Initialize the Receipt Extraction Tool.

        Args:
            api_key: AIStudio API key for ERINE. If not provided, reads from environment.
            **kwargs: Additional arguments passed to BaseTool.
        """
        super().__init__(**kwargs)
        self.api_key = api_key

    @property
    def chain(self) -> ExtractionChain:
        """Lazy initialization of extraction chain."""
        if self._chain is None:
            self._chain = ExtractionChain(api_key=self.api_key)
        return self._chain

    def _run(
        self,
        ocr_text: str,
        seals: Optional[List[Dict[str, Any]]] = None,
        run_manager: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Extract structured information from OCR text.

        Args:
            ocr_text: OCR recognized text from the receipt.
            seals: Optional list of detected seals for analysis.
            run_manager: Optional run manager for callbacks (unused).

        Returns:
            Dictionary containing:
            - receipt_type: Type of the receipt
            - invoice_code: Invoice code (if applicable)
            - invoice_number: Invoice number
            - date: Issue date
            - amount: Amount without tax
            - tax: Tax amount
            - total: Total amount with tax
            - buyer_name: Buyer company name
            - seller_name: Seller company name
            - seal_analysis: Seal authenticity analysis (if seals provided)

        Raises:
            ValueError: If OCR text is empty or invalid.
            Exception: If extraction fails.
        """
        if seals:
            return self.chain.extract_with_seals(ocr_text, seals)
        return self.chain.extract(ocr_text)

    async def _arun(
        self,
        ocr_text: str,
        seals: Optional[List[Dict[str, Any]]] = None,
        run_manager: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Async execution (falls back to sync for now).

        Args:
            ocr_text: OCR recognized text from the receipt.
            seals: Optional list of detected seals.
            run_manager: Optional run manager for callbacks.

        Returns:
            Same as _run method.
        """
        return self._run(ocr_text, seals, run_manager)
