"""Receipt OCR Tool - LangChain Tool Implementation

This tool wraps the OCRChain functionality to provide a LangChain-compatible
interface for receipt OCR processing using langchain-paddleocr.
"""

from typing import Optional, Type, Dict, Any, List

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from ..chains.ocr_chain import OCRChain


class ReceiptOCRInput(BaseModel):
    """Input schema for Receipt OCR Tool.

    Attributes:
        file_path: Path to the receipt image or PDF file.
        enable_seal: Whether to enable seal/stamp recognition.
    """
    file_path: str = Field(
        ...,
        description="Path to the receipt image or PDF file. Supports JPG, PNG, and PDF formats."
    )
    enable_seal: bool = Field(
        default=True,
        description="Whether to enable seal/stamp recognition. Set to False for faster processing."
    )


class ReceiptOCRTool(BaseTool):
    """LangChain Tool for Receipt OCR Processing.

    This tool uses PaddleOCR-VL-1.5 (via langchain-paddleocr) to perform OCR
    on receipt images and PDFs, with optional seal/stamp recognition for
    authenticity verification.

    The tool wraps OCRChain which internally uses PaddleOCRVLLoader from
    the official langchain-paddleocr package.

    Attributes:
        name: Tool name for LangChain agent integration.
        description: Tool description for agent decision making.
        args_schema: Pydantic model for input validation.

    Example:
        >>> tool = ReceiptOCRTool()
        >>> result = tool.invoke({
        ...     "file_path": "invoice.jpg",
        ...     "enable_seal": True
        ... })
        >>> print(result["text"])  # OCR text
        >>> print(result["seals"])  # Detected seals
    """

    name: str = "receipt_ocr"
    description: str = """Recognize text and seals from receipt images or PDFs.

    Input: file path to the receipt image/PDF
    Output: OCR text, detected seals, and raw API response

    Use this tool when you need to extract text content from a receipt document.
    Supports JPG, PNG, and PDF formats. Can optionally detect official seals/stamps
    for authenticity verification.

    Powered by PaddleOCR-VL-1.5 via langchain-paddleocr.
    """
    args_schema: Type[BaseModel] = ReceiptOCRInput

    # Tool configuration
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    _chain: Optional[OCRChain] = None

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        **kwargs
    ):
        """Initialize the Receipt OCR Tool.

        Args:
            api_key: PaddleOCR API access token. If not provided, reads from environment.
            api_url: PaddleOCR API URL. If not provided, uses default from config.
            **kwargs: Additional arguments passed to BaseTool.
        """
        super().__init__(**kwargs)
        self.api_key = api_key
        self.api_url = api_url

    @property
    def chain(self) -> OCRChain:
        """Lazy initialization of OCR chain (uses langchain-paddleocr)."""
        if self._chain is None:
            self._chain = OCRChain(api_key=self.api_key, api_url=self.api_url)
        return self._chain

    def _run(
        self,
        file_path: str,
        enable_seal: bool = True,
        run_manager: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Execute OCR on the receipt file.

        Args:
            file_path: Path to the receipt image or PDF.
            enable_seal: Whether to enable seal recognition.
            run_manager: Optional run manager for callbacks (unused).

        Returns:
            Dictionary containing:
            - text: OCR recognized text
            - seals: List of detected seals with type and position
            - raw_result: Raw API response
            - documents: LangChain Document objects

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is not supported.
            Exception: If OCR processing fails.
        """
        return self.chain.process(file_path, enable_seal=enable_seal)

    async def _arun(
        self,
        file_path: str,
        enable_seal: bool = True,
        run_manager: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Async execution (falls back to sync for now).

        Args:
            file_path: Path to the receipt image or PDF.
            enable_seal: Whether to enable seal recognition.
            run_manager: Optional run manager for callbacks.

        Returns:
            Same as _run method.
        """
        # TODO: Implement true async processing
        return self._run(file_path, enable_seal, run_manager)

    def batch_process(
        self,
        file_paths: List[str],
        enable_seal: bool = True
    ) -> List[Dict[str, Any]]:
        """Process multiple receipt files in batch.

        Args:
            file_paths: List of file paths to process.
            enable_seal: Whether to enable seal recognition.

        Returns:
            List of processing results, one per file.
        """
        return self.chain.batch_process(file_paths, enable_seal=enable_seal)
