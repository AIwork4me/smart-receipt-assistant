# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- LangChain Tools module (`src/tools/`)
  - `ReceiptOCRTool` - LangChain-compatible OCR tool
  - `ReceiptExtractionTool` - Information extraction tool
  - `ReceiptClassificationTool` - Receipt classification tool
- LangChain Agent module (`src/agents/`)
  - `create_receipt_agent()` - Factory function for receipt processing agent
  - `ReceiptAgentExecutor` - High-level agent wrapper
- AGENTS.md - AI-Native repository guide
- README_EN.md - English version of README
- CONTRIBUTING.md - Contribution guidelines
- CODE_OF_CONDUCT.md - Community code of conduct
- SECURITY.md - Security policy
- `.pre-commit-config.yaml` - Pre-commit hooks configuration

### Changed
- Added language switcher links in README.md

## [0.2.0] - 2026-03-11

### Added
- Official `langchain-paddleocr` package integration
- `uv` package manager support
- LangChain compatibility layer (`langchain_compat.py`)
- New environment variable `PADDLEOCR_ACCESS_TOKEN`
- Seal extraction utility module (`utils/seal_extractor.py`)

### Changed
- Migrated from custom OCR implementation to `PaddleOCRVLLoader`
- Improved dependency management with `pyproject.toml`
- Updated documentation for new API configuration

### Fixed
- Import compatibility issues with `langchain-paddleocr`

## [0.1.0] - 2024-01-01

### Added
- Initial release
- PaddleOCR-VL-1.5 OCR recognition
- ERINE (Baidu LLM) integration for information extraction
- Seal/stamp recognition feature
- Support for multiple receipt types:
  - VAT Special Invoice (增值税专用发票)
  - VAT Normal Invoice (增值税普通发票)
  - Train Tickets (火车票)
  - Taxi Receipts (出租车票)
- Gradio Web UI
- CLI interface
- Sample invoices for testing

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 0.2.0 | 2026-03-11 | Official langchain-paddleocr integration, uv support |
| 0.1.0 | 2024-01-01 | Initial release with OCR, ERINE, seal recognition |

---

[Unreleased]: https://github.com/AIwork4me/smart-receipt-assistant/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/AIwork4me/smart-receipt-assistant/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/AIwork4me/smart-receipt-assistant/releases/tag/v0.1.0
