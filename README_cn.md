<div align="center">

# 🧾 智能票据报销助手

**基于 PaddleOCR-VL + LangChain 的企业级票据 OCR 与信息提取系统**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1.0%2B-1C3C3C?logo=langchain&logoColor=white)](https://python.langchain.com/)
[![langchain-paddleocr](https://img.shields.io/badge/langchain--paddleocr-0.1%2B-orange)](https://github.com/PaddlePaddle/PaddleOCR/tree/main/langchain-paddleocr)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/AIwork4me/smart-receipt-assistant?style=social)](https://github.com/AIwork4me/smart-receipt-assistant)

[English](README.md) | **中文**

---

### 🎯 一个 Token，搞定 OCR + LLM 全流程

基于 **[langchain-paddleocr](https://github.com/PaddlePaddle/PaddleOCR/tree/main/langchain-paddleocr)** - LangChain 官方 PaddleOCR 集成

[![ModelScope Demo](https://img.shields.io/badge/🚀_在线体验-ModelScope-9f44d3?style=for-the-badge)](https://modelscope.cn/studios/Devkit/reciept-agent)
[![GitHub Repo](https://img.shields.io/badge/📦_源代码-GitHub-24292f?style=for-the-badge&logo=github)](https://github.com/AIwork4me/smart-receipt-assistant)

</div>

---

## ✨ 核心亮点

<table>
<tr>
<td width="33%" align="center">

### 🔍 印章识别

**PaddleOCR-VL-1.5 独有**

自动检测印章类型，辅助验证发票真伪

</td>
<td width="33%" align="center">

### 🤖 智能提取

**ERINE 4.5 驱动**

结构化 JSON 输出，智能报销分类

</td>
<td width="33%" align="center">

### 🔗 LangChain 原生

**生产级就绪**

工具化架构，支持 Agent 编排

</td>
</tr>
</table>

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                          应用层                                  │
│         Gradio Web 界面  │  CLI 命令行  │  LangChain Agent API    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LangChain 编排层                            │
│                                                                  │
│   ┌──────────┐    ┌──────────────┐    ┌──────────────────┐      │
│   │ OCRTool  │───▶│ ExtractTool  │───▶│ ClassificationTool│     │
│   └──────────┘    └──────────────┘    └──────────────────┘      │
│         │                                                      │
│         ▼                                                      │
│   ┌──────────────────────────────────────────────────────┐     │
│   │          langchain-paddleocr (官方集成)               │     │
│   │              PaddleOCRVLLoader                        │     │
│   └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                          AI 能力层                               │
│     PaddleOCR-VL-1.5 (OCR + 印章)    │    ERINE 4.5 (LLM)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10 或更高版本
- [uv](https://docs.astral.sh/uv/)（推荐）或 pip

### 1. 获取 API Token

访问 [PaddleOCR 官方网站](https://www.paddleocr.com)，完成注册后：

1. 在模型服务页面点击 **"API"** 按钮
2. 获得并复制 **PaddleOCR-VL-1.5** 和 **PP-OCRv5** 的：
   - **TOKEN**（访问令牌）- 用于接口鉴权
   - **API_URL** - 服务接口地址

> 💡 **提示**：PaddleOCR 支持每天免费解析数万文档页数！

### 2. Token 说明

> ⚠️ **重要**：**ERINE 大模型的 Token 与 PaddleOCR 完全一致，无需额外获取！**

只需一个 PaddleOCR Token，即可同时使用：
- ✅ PaddleOCR-VL-1.5（OCR 识别 + 印章检测）
- ✅ ERINE 4.5（智能信息提取）

### 3. 安装部署

```bash
# 安装 uv（如果未安装）
pip install uv

# 克隆项目
git clone https://github.com/AIwork4me/smart-receipt-assistant.git
cd smart-receipt-assistant

# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 PaddleOCR TOKEN 和 API_URL

# 启动 Web 服务
uv run python app.py
```

### 4. 环境配置

编辑 `.env` 文件：

```bash
# PaddleOCR Token（从 www.paddleocr.com 获取）
PADDLEOCR_ACCESS_TOKEN=your_token_here
PADDLEOCR_API_URL=your_api_url_here

# ERINE 使用与 PaddleOCR 相同的 Token，无需额外配置！
```

---

## 📖 使用方式

### Web 界面（推荐）

```bash
uv run python app.py
```

浏览器打开 http://localhost:7860

### 命令行 CLI

```bash
# 识别单张票据
uv run python -m src.main recognize invoice.jpg

# 保存结果到 JSON
uv run python -m src.main recognize invoice.jpg --output result.json

# 批量处理
uv run python -m src.main batch ./invoices/ --output ./results/
```

### LangChain Agent API

```python
from src.agents import create_receipt_agent

# 创建 Agent
agent = create_receipt_agent(api_key="your_token")

# 处理票据
result = agent.process("invoice.jpg")
print(result["output"])
```

### LangChain Tools

```python
from src.tools import ReceiptOCRTool, ReceiptExtractionTool

# 作为 LangChain 工具使用
ocr_tool = ReceiptOCRTool(api_key="your_token")
result = ocr_tool.invoke({"file_path": "invoice.jpg"})
print(result["text"])
```

---

## 🔖 支持的票据类型

| 类型 | OCR | 信息提取 | 印章检测 |
|------|:---:|:--------:|:--------:|
| 增值税专用发票 | ✅ | ✅ | ✅ |
| 增值税普通发票 | ✅ | ✅ | ✅ |
| 火车票 | ✅ | ✅ | - |
| 出租车票 | ✅ | ✅ | - |
| 定额发票 | ✅ | ✅ | ✅ |
| 其他票据 | ✅ | ✅ | ✅ |

---

## 🔍 印章识别说明

| 印章类型 | 说明 | 验真价值 |
|---------|------|---------|
| 发票专用章 | 发票上的专用印章 | ⭐⭐⭐ 高 - 真实性强 |
| 财务专用章 | 财务部门印章 | ⭐⭐ 中 - 辅助判断 |
| 公章 | 企业公章 | ⭐⭐ 中 - 辅助判断 |
| 发票监制章 | 发票上预印的官方章 | ⭐ 低 - 所有发票都有 |

> ⚠️ **注意**：印章识别仅作为辅助验真手段，正式报销建议通过 [国家税务总局查验平台](https://inv-veri.chinatax.gov.cn) 核实。

---

## 📦 项目结构

```
smart-receipt-assistant/
├── app.py                      # Gradio 入口
├── pyproject.toml              # 项目配置 (uv)
├── src/
│   ├── main.py                 # CLI 入口
│   ├── config.py               # 配置管理
│   ├── langchain_compat.py     # LangChain 兼容层
│   ├── chains/                 # LangChain Chains
│   │   ├── ocr_chain.py        # OCR 链 (langchain-paddleocr)
│   │   ├── extraction_chain.py # 信息提取链
│   │   └── classification_chain.py
│   ├── tools/                  # LangChain Tools
│   │   ├── ocr_tool.py         # ReceiptOCRTool
│   │   ├── extraction_tool.py  # ReceiptExtractionTool
│   │   └── classification_tool.py
│   ├── agents/                 # LangChain Agents
│   │   └── receipt_agent.py    # ReceiptAgentExecutor
│   ├── models/                 # Pydantic 数据模型
│   └── utils/                  # 工具函数
├── examples/                   # 示例代码与样例
├── tests/                      # 测试套件
└── docs/                       # 文档
```

---

## 🧪 开发

### 运行测试

```bash
uv run pytest tests/ -v
```

### 代码规范

- 类型注解 (Python 3.10+)
- Pydantic v2 数据验证
- LangChain 1.0+ API

---

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

---

## 📄 许可证

[MIT License](LICENSE)

---

## 🙏 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 飞桨 OCR 框架
- [langchain-paddleocr](https://github.com/PaddlePaddle/PaddleOCR/tree/main/langchain-paddleocr) - LangChain 官方集成
- [LangChain](https://python.langchain.com/) - LLM 应用开发框架
- [百度 AIStudio](https://aistudio.baidu.com/) - AI 开发平台

---

## 📞 联系我们

<div align="center">

扫码关注，获取更多 AI 效率技巧！

![WeChat](assets/aiwork4me.jpg)

</div>

---

<div align="center">

**[⬆ 返回顶部](#-智能票据报销助手)**

Made with ❤️ by [AIwork4me](https://github.com/AIwork4me)

</div>
