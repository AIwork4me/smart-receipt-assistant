# Contributing to Smart Receipt Assistant

Thank you for your interest in contributing to Smart Receipt Assistant! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting a Pull Request](#submitting-a-pull-request)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## Development Setup

### Prerequisites

- Python 3.10 or higher (3.10 - 3.12)
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git

### Setup Steps

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/smart-receipt-assistant.git
cd smart-receipt-assistant

# Install dependencies with uv
uv sync

# Or with pip
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Set up pre-commit hooks (optional but recommended)
uv run pre-commit install

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### API Keys

You'll need the following API keys for development:

1. **PaddleOCR Access Token**: Get from [PaddleOCR API](https://www.paddleocr.com)
2. **AIStudio API Key** (optional): Get from [Baidu AIStudio](https://aistudio.baidu.com) for ERINE features

---

## Code Style

### Python Style Guide

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions
- Use **type hints** for all function parameters and return values
- Use **docstrings** for all public functions and classes
- Maximum line length: 100 characters

### Type Hints

```python
# Good
def process_receipt(file_path: str, enable_seal: bool = True) -> dict[str, Any]:
    """Process a receipt file and return structured data."""
    ...

# Bad
def process_receipt(file_path, enable_seal=True):
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def extract_info(ocr_text: str, seals: list | None = None) -> dict:
    """Extract structured information from OCR text.

    Args:
        ocr_text: The OCR recognized text from a receipt.
        seals: Optional list of detected seals for analysis.

    Returns:
        A dictionary containing extracted receipt information.

    Raises:
        ValueError: If ocr_text is empty.
    """
    ...
```

### Import Order

```python
# 1. Standard library
from typing import Optional, List, Any

# 2. Third-party packages
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

# 3. Local imports
from ..chains.ocr_chain import OCRChain
from ..config import get_api_key
```

### Formatting Tools

We use the following tools for code formatting:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking

Run them with pre-commit or manually:

```bash
# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Type check
uv run mypy src/
```

---

## Project Structure

```
smart-receipt-assistant/
├── src/
│   ├── tools/           # LangChain Tools
│   ├── agents/          # LangChain Agents
│   ├── chains/          # Processing Chains
│   ├── llm/             # LLM Integration
│   ├── models/          # Pydantic Data Models
│   ├── utils/           # Utility Functions
│   └── web/             # Gradio Web UI
├── tests/               # Test Files
├── examples/            # Sample Invoices
├── docs/                # Documentation
└── prompts/             # Prompt Templates
```

---

## Making Changes

### Branch Naming

Use descriptive branch names:

- `feat/add-vat-invoice-support`
- `fix/ocr-timeout-error`
- `docs/update-readme`
- `refactor/extract-tool`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add support for hotel invoices
fix: handle OCR timeout gracefully
docs: update API documentation
refactor: simplify extraction chain logic
test: add unit tests for classification tool
```

### Code Guidelines

1. **Use existing patterns**: Look at existing code for reference
2. **Keep it simple**: Avoid over-engineering
3. **Add tests**: New features should include tests
4. **Update docs**: Update README.md and AGENTS.md if needed
5. **Check compatibility**: Ensure `langchain_compat.py` is imported before `langchain_paddleocr`

---

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_extraction.py -v

# Run specific test
uv run pytest tests/test_extraction.py::TestExtractionChain::test_extract_vat_invoice -v
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch

from src.chains.extraction_chain import ExtractionChain


class TestExtractionChain:
    """Tests for ExtractionChain."""

    @pytest.fixture
    def chain(self) -> ExtractionChain:
        """Create a chain instance for testing."""
        return ExtractionChain(api_key="test-key")

    def test_extract_with_valid_text(self, chain: ExtractionChain):
        """Test extraction with valid OCR text."""
        ocr_text = "增值税专用发票 发票代码: 1100..."
        # ... test implementation
```

---

## Submitting a Pull Request

### Before Submitting

1. **Run tests**: Ensure all tests pass
2. **Format code**: Run black and isort
3. **Type check**: Run mypy
4. **Update docs**: Update documentation if needed
5. **Add tests**: Add tests for new features

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] All tests pass
- [ ] New features have corresponding tests
- [ ] Documentation is updated
- [ ] Commit messages follow conventional commits

### PR Process

1. Create a feature branch from `main`
2. Make your changes
3. Push to your fork
4. Open a Pull Request against `main`
5. Wait for review and address feedback

---

## Getting Help

- Open an [Issue](https://github.com/AIwork4me/smart-receipt-assistant/issues) for bugs or feature requests
- Check existing issues before creating new ones
- Provide detailed information when reporting bugs

---

Thank you for contributing! 🎉
