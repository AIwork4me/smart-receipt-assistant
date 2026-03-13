#!/usr/bin/env python
"""
Basic Usage Example for Smart Receipt Assistant

This script demonstrates the basic usage of the receipt processing tools
and chains.

Usage:
    uv run python examples/basic_usage.py
"""

import os
import json
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chains.ocr_chain import OCRChain
from src.chains.extraction_chain import ExtractionChain
from src.chains.classification_chain import ClassificationChain
from src.tools import ReceiptOCRTool, ReceiptExtractionTool, ReceiptClassificationTool


def example_using_chains():
    """Example using the traditional Chain classes."""
    print("=" * 60)
    print("Example 1: Using Chain Classes")
    print("=" * 60)

    # Initialize chains
    ocr_chain = OCRChain()
    extraction_chain = ExtractionChain()
    classification_chain = ClassificationChain()

    # Find a sample invoice
    sample_dir = Path(__file__).parent.parent / "examples" / "sample_invoices"
    sample_files = list(sample_dir.glob("*.pdf")) + list(sample_dir.glob("*.jpg"))

    if not sample_files:
        print("No sample files found. Please add sample invoices to examples/sample_invoices/")
        return

    sample_file = str(sample_files[0])
    print(f"\nProcessing: {sample_file}")

    # Step 1: OCR
    print("\n[Step 1] Running OCR...")
    try:
        ocr_result = ocr_chain.process(sample_file, enable_seal=True)
        print(f"  OCR text length: {len(ocr_result['text'])} characters")
        print(f"  Seals detected: {len(ocr_result['seals'])}")
    except Exception as e:
        print(f"  OCR Error: {e}")
        return

    # Step 2: Classification
    print("\n[Step 2] Classifying receipt...")
    try:
        classify_result = classification_chain.classify(ocr_result["text"])
        print(f"  Receipt type: {classify_result['receipt_type']}")
        print(f"  Reimbursement category: {classify_result['reimbursement_category']}")
    except Exception as e:
        print(f"  Classification Error: {e}")

    # Step 3: Extraction
    print("\n[Step 3] Extracting information...")
    try:
        extract_result = extraction_chain.extract_with_seals(
            ocr_result["text"],
            ocr_result["seals"]
        )
        print(f"  Receipt type: {extract_result.get('receipt_type', 'N/A')}")
        print(f"  Invoice number: {extract_result.get('invoice_number', 'N/A')}")
        print(f"  Total amount: {extract_result.get('total', 'N/A')}")

        if "seal_analysis" in extract_result:
            print(f"  Seal analysis: {extract_result['seal_analysis'].get('authenticity_hint', 'N/A')}")
    except Exception as e:
        print(f"  Extraction Error: {e}")


def example_using_tools():
    """Example using LangChain Tools."""
    print("\n" + "=" * 60)
    print("Example 2: Using LangChain Tools")
    print("=" * 60)

    # Initialize tools
    ocr_tool = ReceiptOCRTool()
    extraction_tool = ReceiptExtractionTool()
    classification_tool = ReceiptClassificationTool()

    # Find a sample invoice
    sample_dir = Path(__file__).parent.parent / "examples" / "sample_invoices"
    sample_files = list(sample_dir.glob("*.pdf")) + list(sample_dir.glob("*.jpg"))

    if not sample_files:
        print("No sample files found.")
        return

    sample_file = str(sample_files[0])
    print(f"\nProcessing: {sample_file}")

    # Step 1: OCR
    print("\n[Step 1] Running OCR with ReceiptOCRTool...")
    try:
        ocr_result = ocr_tool.invoke({
            "file_path": sample_file,
            "enable_seal": True
        })
        print(f"  OCR text preview: {ocr_result['text'][:100]}...")
    except Exception as e:
        print(f"  OCR Error: {e}")
        return

    # Step 2: Classification
    print("\n[Step 2] Running classification...")
    try:
        classify_result = classification_tool.invoke({
            "ocr_text": ocr_result["text"]
        })
        print(f"  Result: {json.dumps(classify_result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"  Classification Error: {e}")

    # Step 3: Extraction
    print("\n[Step 3] Running extraction...")
    try:
        extract_result = extraction_tool.invoke({
            "ocr_text": ocr_result["text"],
            "seals": ocr_result["seals"]
        })
        print(f"  Result: {json.dumps(extract_result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"  Extraction Error: {e}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Smart Receipt Assistant - Basic Usage Examples")
    print("=" * 60)

    # Check for API keys
    if not os.getenv("PADDLEOCR_ACCESS_TOKEN"):
        print("\nWarning: PADDLEOCR_ACCESS_TOKEN not set. OCR will fail.")
        print("Please set environment variables in .env file.")

    # Run examples
    example_using_chains()
    example_using_tools()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
