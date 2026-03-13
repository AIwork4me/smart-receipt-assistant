<div align="center">

# 🧾 Smart Receipt Assistant

**Enterprise-Grade Receipt OCR & Extraction Powered by PaddleOCR-VL + LangChain**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1.0%2B-1C3C3C?logo=langchain&logoColor=white)](https://python.langchain.com/)
[![langchain-paddleocr](https://img.shields.io/badge/langchain--paddleocr-0.1%2B-orange)](https://github.com/PaddlePaddle/PaddleOCR/tree/main/langchain-paddleocr)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/AIwork4me/smart-receipt-assistant?style=social)](https://github.com/AIwork4me/smart-receipt-assistant)

**English** | [中文](README_cn.md)

---

### 🎯 One Token. Full Stack OCR + LLM Pipeline.

Powered by **[langchain-paddleocr](https://github.com/PaddlePaddle/PaddleOCR/tree/main/langchain-paddleocr)** - The Official LangChain Integration for PaddleOCR

[![ModelScope Demo](https://img.shields.io/badge/🚀_Live_Demo-ModelScope-9f44d3?style=for-the-badge)](https://modelscope.cn/studios/Devkit/reciept-agent)
[![GitHub Repo](https://img.shields.io/badge/📦_Source_Code-GitHub-24292f?style=for-the-badge&logo=github)](https://github.com/AIwork4me/smart-receipt-assistant)

</div>

---

## ✨ Why Smart Receipt Assistant?

<table>
<tr>
<td width="33%" align="center">

### 🔍 Seal Recognition

**PaddleOCR-VL-1.5 Exclusive**

Auto-detect seal types for authenticity verification

</td>
<td width="33%" align="center">

### 🤖 Intelligent Extraction

**ERINE 4.5 Powered**

Structured JSON output with smart categorization

</td>
<td width="33%" align="center">

### 🔗 LangChain Native

**Production Ready**

Tool-based architecture with Agent support

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Application Layer                         │
│         Gradio Web UI  │  CLI  │  LangChain Agent API            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LangChain Orchestration                     │
│                                                                  │
│   ┌──────────┐    ┌──────────────┐    ┌──────────────────┐      │
│   │ OCRTool  │───▶│ ExtractTool  │───▶│ ClassificationTool│     │
│   └──────────┘    └──────────────┘    └──────────────────┘      │
│         │                                                      │
│         ▼                                                      │
│   ┌──────────────────────────────────────────────────────┐     │
│   │          langchain-paddleocr (Official)               │     │
│   │              PaddleOCRVLLoader                        │     │
│   └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AI Capability Layer                       │
│     PaddleOCR-VL-1.5 (OCR + Seal)    │    ERINE 4.5 (LLM)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### 1. Get Your API Token

Visit [PaddleOCR Official Website](https://www.paddleocr.com) and register:

1. Click **"API"** button on the model service page
2. Get and copy your **PaddleOCR-VL-1.5** and **PP-OCRv5** credentials:
   - **TOKEN** (Access Token) - for API authentication
   - **API_URL** - Service endpoint address

> 💡 **Tip**: PaddleOCR supports free parsing of tens of thousands of document pages per day!

### 2. Token Note

> ⚠️ **Important**: **ERINE LLM Token is the same as PaddleOCR Token - no extra setup needed!**

With a single PaddleOCR Token, you can use both:
- ✅ PaddleOCR-VL-1.5 (OCR Recognition + Seal Detection)
- ✅ ERINE 4.5 (Intelligent Information Extraction)

### 3. Installation

```bash
# Install uv (if not installed)
pip install uv

# Clone the repository
git clone https://github.com/AIwork4me/smart-receipt-assistant.git
cd smart-receipt-assistant

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env and fill in your PaddleOCR TOKEN and API_URL

# Launch Web UI
uv run python app.py
```

### 4. Configuration

Edit `.env`:

```bash
# PaddleOCR Token (from www.paddleocr.com)
PADDLEOCR_ACCESS_TOKEN=your_token_here
PADDLEOCR_API_URL=your_api_url_here

# ERINE uses the same token as PaddleOCR - no extra config needed!
```

---

## 📖 Usage

### Web UI (Recommended)

```bash
uv run python app.py
```

Open http://localhost:7860 in your browser.

### CLI

```bash
# Recognize single receipt
uv run python -m src.main recognize invoice.jpg

# Save results to JSON
uv run python -m src.main recognize invoice.jpg --output result.json

# Batch processing
uv run python -m src.main batch ./invoices/ --output ./results/
```

### LangChain Agent API

```python
from src.agents import create_receipt_agent

# Create agent with your API key
agent = create_receipt_agent(api_key="your_token")

# Process receipt
result = agent.process("invoice.jpg")
print(result["output"])
```

### LangChain Tools

```python
from src.tools import ReceiptOCRTool, ReceiptExtractionTool

# Use as LangChain tools
ocr_tool = ReceiptOCRTool(api_key="your_token")
result = ocr_tool.invoke({"file_path": "invoice.jpg"})
print(result["text"])
```

---

## 🔖 Supported Receipt Types

| Type | OCR | Extraction | Seal Detection |
|------|:---:|:----------:|:--------------:|
| VAT Special Invoice (增值税专用发票) | ✅ | ✅ | ✅ |
| VAT General Invoice (增值税普通发票) | ✅ | ✅ | ✅ |
| Train Ticket (火车票) | ✅ | ✅ | - |
| Taxi Receipt (出租车票) | ✅ | ✅ | - |
| Fixed Amount Invoice (定额发票) | ✅ | ✅ | ✅ |
| Other Receipts | ✅ | ✅ | ✅ |

---

## 🔍 Seal Recognition Guide

| Seal Type | Description | Verification Value |
|-----------|-------------|-------------------|
| 发票专用章 (Invoice Seal) | Official invoice seal | ⭐⭐⭐ High - Strong authenticity indicator |
| 财务专用章 (Finance Seal) | Finance department seal | ⭐⭐ Medium - Supporting evidence |
| 公章 (Company Seal) | Official company seal | ⭐⭐ Medium - Supporting evidence |
| 发票监制章 (Tax Authority Seal) | Pre-printed tax seal | ⭐ Low - Present on all invoices |

> ⚠️ **Note**: Seal recognition is an auxiliary verification method. For official verification, use the [National Tax Verification Platform](https://inv-veri.chinatax.gov.cn).

---

## 📦 Project Structure

```
smart-receipt-assistant/
├── app.py                      # Gradio entry point
├── pyproject.toml              # Project config (uv)
├── src/
│   ├── main.py                 # CLI entry
│   ├── config.py               # Configuration
│   ├── langchain_compat.py     # LangChain compatibility layer
│   ├── chains/                 # LangChain Chains
│   │   ├── ocr_chain.py        # OCR chain (langchain-paddleocr)
│   │   ├── extraction_chain.py # Information extraction
│   │   └── classification_chain.py
│   ├── tools/                  # LangChain Tools
│   │   ├── ocr_tool.py         # ReceiptOCRTool
│   │   ├── extraction_tool.py  # ReceiptExtractionTool
│   │   └── classification_tool.py
│   ├── agents/                 # LangChain Agents
│   │   └── receipt_agent.py    # ReceiptAgentExecutor
│   ├── models/                 # Pydantic models
│   └── utils/                  # Utilities
├── examples/                   # Example code & samples
├── tests/                      # Test suite
└── docs/                       # Documentation
```

---

## 🧪 Development

### Run Tests

```bash
uv run pytest tests/ -v
```

### Code Style

This project uses:
- Type hints (Python 3.10+)
- Pydantic v2 for data validation
- LangChain 1.0+ API

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

[MIT License](LICENSE)

---

## 🙏 Acknowledgements

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - PaddlePaddle OCR Framework
- [langchain-paddleocr](https://github.com/PaddlePaddle/PaddleOCR/tree/main/langchain-paddleocr) - Official LangChain Integration
- [LangChain](https://python.langchain.com/) - LLM Application Framework
- [Baidu AIStudio](https://aistudio.baidu.com/) - AI Development Platform

---

## 📞 Contact

<div align="center">

Scan to follow for more AI productivity tips!

![WeChat](assets/aiwork4me.jpg)

</div>

---

<div align="center">

**[⬆ Back to Top](#-smart-receipt-assistant)**

Made with ❤️ by [AIwork4me](https://github.com/AIwork4me)

</div>
