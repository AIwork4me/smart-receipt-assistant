# AGENTS.md

> AI Agent Collaboration Guide for Smart Receipt Assistant

This document provides comprehensive guidance for AI agents (including Claude, GPT, etc.) working with this codebase.

---

## Project Overview

**Smart Receipt Assistant** is an intelligent receipt processing system that combines OCR, NLU, and structured data extraction.

### Tech Stack
- **OCR Engine**: PaddleOCR-VL-1.5 (via `langchain-paddleocr`)
- **LLM Framework**: LangChain
- **Language Model**: ERINE 4.5 (Baidu's LLM, OpenAI-compatible API)
- **Web UI**: Gradio
- **Package Manager**: uv

### Core Features
1. Receipt OCR with seal/stamp recognition
2. Structured information extraction
3. Receipt classification for reimbursement

### Documentation Structure
- `README.md` - English documentation (main)
- `README_cn.md` - Chinese documentation (中文文档)
- `AGENTS.md` - This file, AI agent collaboration guide

---

## Code Architecture

```
src/
├── main.py              # CLI entry point
├── config.py            # Environment configuration
├── langchain_compat.py  # ⚠️ CRITICAL: LangChain compatibility layer
│
├── tools/               # LangChain Tools (BaseTool implementations)
│   ├── ocr_tool.py      # ReceiptOCRTool
│   ├── extraction_tool.py   # ReceiptExtractionTool
│   └── classification_tool.py   # ReceiptClassificationTool
│
├── agents/              # LangChain Agents
│   └── receipt_agent.py # create_receipt_agent()
│
├── chains/              # Processing Chains
│   ├── ocr_chain.py     # OCRChain - uses PaddleOCRVLLoader
│   ├── extraction_chain.py  # ExtractionChain
│   └── classification_chain.py  # ClassificationChain
│
├── llm/                 # LLM Integration
│   └── ernie.py         # ERINE client, ReceiptExtractionChain
│
├── models/              # Data Models (Pydantic)
│   └── receipt.py       # ReceiptInfo, SealInfo, enums
│
├── utils/               # Utilities
│   └── seal_extractor.py    # Seal extraction from API response
│
└── web/                 # Gradio Web UI
    ├── app.py           # Main Gradio app
    └── components.py    # UI components
```

### Dependency Graph

```
                    ┌─────────────┐
                    │   main.py   │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    ┌─────────┐      ┌─────────┐      ┌─────────┐
    │  tools/ │      │ agents/ │      │  web/   │
    └────┬────┘      └────┬────┘      └────┬────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
                          ▼
                    ┌───────────┐
                    │  chains/  │
                    └─────┬─────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │   llm/  │     │  ocr/   │     │  utils/ │
    └─────────┘     └─────────┘     └─────────┘
```

---

## Development Guidelines

### Code Style
- Python 3.10+ required
- Use type hints for all function parameters and return values
- Follow PEP 8 conventions
- Use Pydantic models for data validation

### Import Order
```python
# 1. Standard library
from typing import Optional, List

# 2. Third-party (LangChain, etc.)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

# 3. Local imports
from ..chains.ocr_chain import OCRChain
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `ReceiptOCRTool`, `ExtractionChain`)
- **Functions/Methods**: snake_case (e.g., `process_receipt`, `extract_info`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `ERINE_BASE_URL`)

---

## Critical: LangChain Compatibility Layer

⚠️ **IMPORTANT**: The `langchain_compat.py` module MUST be imported before any `langchain_paddleocr` imports.

```python
# CORRECT
from ..langchain_compat import setup_langchain_compat
setup_langchain_compat()
from langchain_paddleocr import PaddleOCRVLLoader

# WRONG - Will cause import errors
from langchain_paddleocr import PaddleOCRVLLoader  # Error!
```

This is required because `langchain-paddleocr` depends on legacy LangChain 0.x import paths.

---

## Environment Configuration

### Token Acquisition

⚠️ **KEY POINT**: **PaddleOCR Token and ERINE Token are the SAME - only one token needed!**

Get your token from **PaddleOCR Official Website**: https://www.paddleocr.com

1. Visit https://www.paddleocr.com
2. Complete registration
3. Click **"API"** button on model service page
4. Get TOKEN and API_URL for PaddleOCR-VL-1.5 / PP-OCRv5

> 💡 PaddleOCR supports free parsing of tens of thousands of document pages per day!

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PADDLEOCR_ACCESS_TOKEN` | Yes | PaddleOCR API token (also used for ERINE) |
| `PADDLEOCR_API_URL` | Yes | PaddleOCR API URL from website |
| `ERINE_BASE_URL` | No | ERINE API URL (default: https://aistudio.baidu.com/llm/lmapi/v3) |

### .env Configuration

```bash
# PaddleOCR Token - get from www.paddleocr.com
# This token works for BOTH PaddleOCR AND ERINE!
PADDLEOCR_ACCESS_TOKEN=your_token_here
PADDLEOCR_API_URL=your_api_url_here

# ERINE uses the same token - no extra config needed
# ERINE_BASE_URL=https://aistudio.baidu.com/llm/lmapi/v3
```

---

## API Quick Reference

### Tools (LangChain Standard)

```python
from src.tools import ReceiptOCRTool, ReceiptExtractionTool, ReceiptClassificationTool

# Single token for all tools!
TOKEN = "your_paddleocr_token"

# OCR Tool
ocr = ReceiptOCRTool(api_key=TOKEN)
result = ocr.invoke({"file_path": "invoice.jpg", "enable_seal": True})
# Returns: {"text": "...", "seals": [...], "documents": [...]}

# Extraction Tool (uses same token)
extract = ReceiptExtractionTool(api_key=TOKEN)
info = extract.invoke({"ocr_text": result["text"], "seals": result["seals"]})
# Returns: {"receipt_type": "增值税专用发票", "invoice_code": "...", ...}

# Classification Tool (uses same token)
classify = ReceiptClassificationTool(api_key=TOKEN)
category = classify.invoke({"ocr_text": result["text"]})
# Returns: {"receipt_type": "...", "reimbursement_category": "办公费用"}
```

### Agent

```python
from src.agents import create_receipt_agent

# Single token for everything!
TOKEN = "your_paddleocr_token"

agent = create_receipt_agent(
    api_key=TOKEN,           # Same token for ERINE
    paddleocr_api_key=TOKEN, # Same token for PaddleOCR
    verbose=True
)
result = agent.process("invoice.jpg")
```

### Chains (Legacy)

```python
from src.chains import OCRChain, ExtractionChain, ClassificationChain

TOKEN = "your_paddleocr_token"

# OCR
ocr = OCRChain(api_key=TOKEN)
result = ocr.process("invoice.jpg", enable_seal=True)

# Extraction (same token)
extract = ExtractionChain(api_key=TOKEN)
info = extract.extract_with_seals(result["text"], result["seals"])

# Classification (same token)
classify = ClassificationChain(api_key=TOKEN)
category = classify.classify(result["text"])
```

### Data Models

```python
from src.models import ReceiptInfo, SealInfo, ReceiptType, ReimbursementCategory

# Create receipt info
receipt = ReceiptInfo(
    receipt_type="增值税专用发票",
    invoice_code="1100...",
    invoice_number="12345678",
    total="1000.00",
    seals=[SealInfo(name="发票专用章", url="...", seal_type="发票专用章")]
)

# Convert to dict
data = receipt.to_dict()

# Convert to Excel row
row = receipt.to_excel_row()
```

---

## Common Tasks

### Add New Receipt Type

1. Update `ReceiptType` enum in `src/models/receipt.py`
2. Update `REIMBURSEMENT_CATEGORIES` in `src/chains/classification_chain.py`
3. Update extraction prompt in `src/llm/ernie.py` if needed

### Add New LLM Backend

1. Create new file in `src/llm/` (e.g., `openai.py`)
2. Implement similar to `ernie.py` with LangChain ChatOpenAI
3. Update `config.py` to support new API key

### Add New Tool

1. Create file in `src/tools/` (e.g., `validation_tool.py`)
2. Inherit from `BaseTool` and implement `_run` method
3. Export in `src/tools/__init__.py`

### Modify Extraction Fields

1. Update `ReceiptInfo` model in `src/models/receipt.py`
2. Update `EXTRACTION_PROMPT` in `src/llm/ernie.py`
3. Update `to_excel_row()` method if needed

---

## Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test
uv run pytest tests/test_extraction.py -v
```

---

## Troubleshooting

### Import Error: langchain_paddleocr

**Problem**: `ModuleNotFoundError` or import errors when using `langchain_paddleocr`

**Solution**: Ensure `langchain_compat.py` is imported first:
```python
from src.langchain_compat import setup_langchain_compat
setup_langchain_compat()
```

### API Authentication Errors

**Problem**: 401 or 403 errors from PaddleOCR/ERINE APIs

**Solution**: Check `.env` file contains correct token:
```bash
# Get token from https://www.paddleocr.com
PADDLEOCR_ACCESS_TOKEN=your_valid_token
PADDLEOCR_API_URL=your_api_url
```

**Remember**: PaddleOCR and ERINE use the SAME token!

### OCR Returns Empty Results

**Problem**: OCR process returns empty text

**Solution**: Verify:
1. File format is supported (PDF/JPG/PNG)
2. File is not corrupted
3. API URL is correct (from PaddleOCR website)

---

## Key Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `src/tools/ocr_tool.py` | LangChain OCR tool | ~120 |
| `src/agents/receipt_agent.py` | LangChain Agent | ~180 |
| `src/chains/ocr_chain.py` | OCR processing chain | ~100 |
| `src/llm/ernie.py` | ERINE LLM integration | ~240 |
| `src/models/receipt.py` | Data models | ~80 |
| `src/config.py` | Configuration (single token) | ~60 |
| `src/langchain_compat.py` | Compatibility layer | ~40 |

---

## Agent Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                    Receipt Processing Flow                    │
└──────────────────────────────────────────────────────────────┘

User Input ──────► Agent/Chain Selection
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │   OCR   │───►│Extract  │───►│ Classify│
    │  Tool   │    │  Tool   │    │  Tool   │
    └────┬────┘    └────┬────┘    └────┬────┘
         │              │              │
         ▼              ▼              ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │PaddleOCR│    │ ERINE   │    │ ERINE   │
    │   VL    │    │   LLM   │    │   LLM   │
    └────┬────┘    └────┬────┘    └────┬────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
              Same Token (PADDLEOCR_ACCESS_TOKEN)
                        │
                        ▼
              ┌─────────────────┐
              │ Structured JSON │
              │     Output      │
              └─────────────────┘
```

---

## For AI Agents: How to Help

When modifying this codebase:

1. **Always check `langchain_compat.py` imports** - Any file using OCR must import it first
2. **Use existing chains/tools** - Don't duplicate OCR logic
3. **Follow Pydantic patterns** - Use `ReceiptInfo` model for structured data
4. **Maintain type hints** - All new code should have type annotations
5. **Test with sample invoices** - Use files in `examples/sample_invoices/`
6. **Remember: Single Token** - PaddleOCR and ERINE use the same token from www.paddleocr.com

---

*Last updated: 2026-03-13*
