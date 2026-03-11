# 智能票据报销助手 - 项目开发提示词

> 使用此提示词指导 Claude Code 从零开始完成「智能票据报销助手」项目
>
> 技术栈：langchain-paddleocr + LangChain + ERINE + Gradio + uv

---

## 项目背景

中国企业员工平均每月花费 2-3 小时处理报销，发票种类繁多（增值税专票/普票、电子发票、火车票、出租车票等），手动录入易出错，财务审核工作量大。

**目标**：打造一个智能票据报销助手，实现：
- 自动识别票据类型（增值税发票/火车票等）
- 提取关键字段（发票代码、金额、日期等）
- **识别印章并辅助验证真伪**（亮点功能）
- 自动分类报销类别

---

## 技术栈

| 组件 | 选择 | 说明 |
|------|------|------|
| OCR | PaddleOCR-VL-1.5 + langchain-paddleocr | 官方 LangChain 集成包，支持印章识别 |
| LLM | ERINE（文心一言） | 中文理解强，OpenAI 兼容 API |
| 编排 | LangChain | 链式工作流，模型无关性 |
| 环境 | uv | 现代化 Python 包管理器，快速可靠 |
| Web | Gradio | 快速搭建界面 |
| 部署 | ModelScope 创空间 | 百度生态集成 |

**关键优势**：
- 使用官方 `langchain-paddleocr` 包，与 LangChain 无缝集成
- 一个 API Key 同时用于 OCR 和 LLM
- 云端 API，无需本地安装 PaddlePaddle
- 支持 PDF 和图片格式自动检测

---

## 项目结构

```
smart-receipt-assistant/
├── app.py                  # ModelScope 创空间入口
├── pyproject.toml          # uv 依赖管理
├── uv.lock                 # uv 锁定文件（自动生成）
├── requirements.txt        # pip 兼容（可选）
├── .env.example            # 环境变量模板
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py             # CLI 入口
│   ├── config.py           # 配置管理
│   ├── langchain_compat.py # LangChain 兼容层（关键！）
│   ├── chains/
│   │   ├── __init__.py
│   │   ├── ocr_chain.py    # OCR 链（使用官方包）
│   │   ├── extraction_chain.py  # 信息提取链
│   │   └── classification_chain.py  # 分类链
│   ├── llm/
│   │   ├── __init__.py
│   │   └── ernie.py        # ERINE + LangChain 封装
│   ├── ocr/
│   │   ├── __init__.py
│   │   └── paddle_ocr.py   # 保留用于向后兼容
│   ├── web/
│   │   ├── __init__.py
│   │   ├── app.py          # Gradio 应用
│   │   └── components.py   # UI 组件
│   └── utils/
│       ├── __init__.py
│       ├── seal_extractor.py  # 印章提取（独立模块）
│       └── validators.py      # 验证函数
├── tests/
│   ├── __init__.py
│   ├── test_ocr.py
│   └── test_extraction.py
├── examples/
│   └── sample_invoices/    # 样本发票
│       ├── README.md
│       ├── dinner.pdf
│       ├── didi.pdf
│       ├── train.pdf
│       ├── invoice1.png
│       └── invoice2.png
└── prompts/
    └── receipt-agent-prompt.md  # 本文件
```

---

## 核心实现代码

### 1. 依赖配置 (pyproject.toml)

**必须使用 uv 作为包管理器**

```toml
[project]
name = "smart-receipt-assistant"
version = "0.2.0"
description = "智能票据报销助手 - PaddleOCR-VL + LangChain + ERINE"
readme = "README.md"
requires-python = ">=3.10,<3.13"
dependencies = [
    # LangChain 生态
    "langchain>=0.1.0",
    "langchain-community>=0.0.1",
    "langchain-openai>=0.1.0",
    "langchain-paddleocr>=0.1.0",
    "langchain-core>=0.1.0",
    "langchain-text-splitters>=0.0.1",
    # OpenAI 兼容
    "openai>=1.0.0",
    # HTTP 和数据处理
    "requests>=2.31.0",
    "pydantic>=2.0.0",
    # 环境变量
    "python-dotenv>=1.0.0",
    # CLI 美化
    "rich>=13.0.0",
    # 图像处理
    "pillow>=10.0.0",
    # Web UI
    "gradio>=4.0.0",
    # Excel 导出
    "openpyxl>=3.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "jupyter>=1.0.0",
]

[project.scripts]
receipt-assistant = "src.main:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

**uv 常用命令**：
```bash
# 安装依赖
uv sync

# 运行 CLI
uv run python -m src.main recognize invoice.pdf

# 启动 Web
uv run python app.py

# 运行测试
uv run pytest
```

### 2. LangChain 兼容层 (src/langchain_compat.py)

**这是最关键的文件！必须在导入 langchain_paddleocr 之前被导入。**

paddlex 包使用了旧版 LangChain 的导入路径，这些路径在新版中已被移除。此兼容层解决该问题。

```python
"""LangChain 兼容层

解决 paddlex 包与新版 LangChain 的兼容性问题。
paddlex 使用了旧版 LangChain 的导入路径，这些路径在新版中已被移除。

此模块必须在导入 langchain_paddleocr 之前被导入。
"""
import sys
from types import ModuleType


def setup_langchain_compat():
    """设置 LangChain 兼容层

    为旧版 LangChain 导入路径创建兼容模块：
    - langchain.docstore.document -> langchain_core.documents
    - langchain.text_splitter -> langchain_text_splitters
    """
    # 导入新版模块
    import langchain_core.documents
    import langchain_text_splitters

    # 创建 langchain.docstore 兼容模块
    if 'langchain.docstore' not in sys.modules:
        docstore_module = ModuleType('langchain.docstore')
        sys.modules['langchain.docstore'] = docstore_module

    # 创建 langchain.docstore.document 兼容模块
    if 'langchain.docstore.document' not in sys.modules:
        document_module = ModuleType('langchain.docstore.document')
        document_module.Document = langchain_core.documents.Document
        sys.modules['langchain.docstore.document'] = document_module

    # 创建 langchain.text_splitter 兼容模块
    if 'langchain.text_splitter' not in sys.modules:
        text_splitter_module = ModuleType('langchain.text_splitter')
        # 复制所有公共属性
        for attr in dir(langchain_text_splitters):
            if not attr.startswith('_'):
                setattr(text_splitter_module, attr, getattr(langchain_text_splitters, attr))
        sys.modules['langchain.text_splitter'] = text_splitter_module

    # 确保 langchain 模块存在
    if 'langchain' not in sys.modules:
        langchain_module = ModuleType('langchain')
        sys.modules['langchain'] = langchain_module


# 自动设置兼容层
setup_langchain_compat()
```

### 3. 配置管理 (src/config.py)

```python
"""配置管理模块"""
import os
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()


def get_paddleocr_token() -> SecretStr:
    """获取 PaddleOCR Access Token

    优先使用 PADDLEOCR_ACCESS_TOKEN，回退到 AISTUDIO_API_KEY

    Returns:
        SecretStr: Access Token

    Raises:
        ValueError: 未设置任何有效的环境变量
    """
    token = os.getenv("PADDLEOCR_ACCESS_TOKEN") or os.getenv("AISTUDIO_API_KEY")
    if not token:
        raise ValueError(
            "请设置 PADDLEOCR_ACCESS_TOKEN 或 AISTUDIO_API_KEY 环境变量\n"
            "1. 访问 https://www.paddleocr.com\n"
            "2. 点击【API】选择【PaddleOCR-VL-1.5】\n"
            "3. 复制 TOKEN 和 API_URL"
        )
    return SecretStr(token)


# PaddleOCR API URL（可通过环境变量覆盖）
PADDLEOCR_API_URL = os.getenv(
    "PADDLEOCR_API_URL",
    "https://q6mbb0r0t8m9q4pf.aistudio-app.com/layout-parsing"
)

# ERINE 配置
ERINE_BASE_URL = "https://aistudio.baidu.com/llm/lmapi/v3"
ERINE_MODEL = "ernie-4.5-turbo-128k-preview"

# 保留向后兼容
AISTUDIO_API_KEY = os.getenv("AISTUDIO_API_KEY")


def get_api_key() -> str:
    """获取 API Key（向后兼容）

    Returns:
        str: API Key 字符串
    """
    token = get_paddleocr_token()
    return token.get_secret_value()
```

### 4. OCR 处理链 (src/chains/ocr_chain.py)

**使用官方 langchain-paddleocr 包**

```python
"""OCR 处理链 - 使用官方 langchain-paddleocr"""
from typing import Optional, List

# 必须在导入 langchain_paddleocr 之前设置兼容层
from ..langchain_compat import setup_langchain_compat
setup_langchain_compat()

from langchain_paddleocr import PaddleOCRVLLoader
from pydantic import SecretStr

from ..config import get_paddleocr_token, PADDLEOCR_API_URL
from ..utils.seal_extractor import extract_seals_from_response


class OCRChain:
    """OCR 处理链 - 基于官方 PaddleOCRVLLoader

    负责调用 PaddleOCR-VL-1.5 进行票据识别，支持印章识别。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None
    ):
        """
        Args:
            api_key: Access Token，默认从环境变量读取
            api_url: API URL，默认从配置读取
        """
        if api_key:
            self.access_token = SecretStr(api_key)
        else:
            self.access_token = get_paddleocr_token()
        self.api_url = api_url or PADDLEOCR_API_URL

    def process(self, file_path: str, enable_seal: bool = True) -> dict:
        """处理票据图片

        Args:
            file_path: 图片/PDF 路径
            enable_seal: 是否启用印章识别

        Returns:
            处理结果，包含:
            - text: OCR 识别的文本
            - seals: 印章信息列表
            - raw_result: 原始 API 响应
            - documents: LangChain Document 对象列表
        """
        # 使用官方 PaddleOCRVLLoader
        loader = PaddleOCRVLLoader(
            file_path=file_path,
            api_url=self.api_url,
            access_token=self.access_token,
            use_seal_recognition=enable_seal,
            use_layout_detection=True,
        )

        # 加载文档
        docs = loader.load()

        # 合并所有页面文本
        text = "\n\n".join(doc.page_content for doc in docs)

        # 从原始响应提取印章信息
        raw_response = docs[0].metadata.get("paddleocr_vl_raw_response", {}) if docs else {}
        seals = extract_seals_from_response(raw_response)

        return {
            "text": text,
            "seals": seals,
            "raw_result": raw_response,
            "documents": docs  # LangChain Document 对象
        }

    def batch_process(self, file_paths: List[str], enable_seal: bool = True) -> List[dict]:
        """批量处理票据图片

        Args:
            file_paths: 图片路径列表
            enable_seal: 是否启用印章识别

        Returns:
            处理结果列表
        """
        results = []
        for path in file_paths:
            try:
                result = self.process(path, enable_seal)
                result["file_path"] = path
                result["status"] = "success"
            except Exception as e:
                result = {
                    "file_path": path,
                    "status": "error",
                    "error": str(e)
                }
            results.append(result)
        return results
```

### 5. 印章提取工具 (src/utils/seal_extractor.py)

**独立模块，从原始响应提取印章信息**

```python
"""印章提取工具

从 PaddleOCR-VL API 原始响应中提取印章信息。
"""
from typing import List, Dict, Any


def extract_seals_from_response(raw_response: dict) -> List[Dict[str, Any]]:
    """从 PaddleOCR API 原始响应中提取印章信息

    Args:
        raw_response: PaddleOCRVLLoader 返回的 paddleocr_vl_raw_response

    Returns:
        印章信息列表，每个元素包含:
        - name: 印章图片名称
        - url: 印章图片 URL
        - page: 所在页码
        - type: 印章类型（发票专用章、财务专用章等）
    """
    seals = []

    # 处理可能的响应结构
    result = raw_response.get("result", raw_response)
    layout_results = result.get("layoutParsingResults", [])

    for i, res in enumerate(layout_results):
        # 获取 markdown 文本用于分析印章类型
        markdown = res.get("markdown", {})
        full_text = markdown.get("text", "")

        # 方法1: 从 outputImages 中提取
        output_images = res.get("outputImages", {})
        for img_name, img_url in output_images.items():
            if "seal" in img_name.lower():
                seals.append({
                    "name": img_name,
                    "url": img_url,
                    "page": i,
                    "type": classify_seal(img_name, full_text)
                })

        # 方法2: 从 markdown.images 中提取
        images = markdown.get("images", {})
        for img_name, img_url in images.items():
            if "seal" in img_name.lower():
                seals.append({
                    "name": img_name,
                    "url": img_url,
                    "page": i,
                    "type": classify_seal(img_name, full_text)
                })

    return seals


def classify_seal(name: str, surrounding_text: str = "") -> str:
    """根据名称和周围文本判断印章类型

    Args:
        name: 印章图片名称
        surrounding_text: 印章周围的 OCR 文本

    Returns:
        印章类型字符串
    """
    name_lower = name.lower()

    # 发票专用章
    if "invoice" in name_lower or "发票专用章" in surrounding_text or "发票章" in surrounding_text:
        return "发票专用章"

    # 财务专用章
    if "finance" in name_lower or "财务专用章" in surrounding_text or "财务章" in surrounding_text:
        return "财务专用章"

    # 公章
    if "official" in name_lower or "公章" in surrounding_text:
        return "公章"

    # 发票监制章（预印在发票上）
    if "监制章" in surrounding_text or "监督章" in surrounding_text:
        return "发票监制章"

    # 合同章
    if "合同" in surrounding_text and "章" in surrounding_text:
        return "合同章"

    return "其他印章"
```

### 6. 信息提取链 (src/chains/extraction_chain.py)

```python
"""信息提取链"""
from typing import Optional
from ..llm import ReceiptExtractionChain
from ..config import get_api_key


class ExtractionChain:
    """信息提取链

    负责从 OCR 文本中提取结构化信息
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: AIStudio API Key，默认从环境变量读取
        """
        self.chain = ReceiptExtractionChain(api_key or get_api_key())

    def extract(self, ocr_text: str) -> dict:
        """提取票据信息

        Args:
            ocr_text: OCR 识别的文本

        Returns:
            结构化的票据信息
        """
        return self.chain.extract(ocr_text)

    def extract_with_seals(self, ocr_text: str, seals: list) -> dict:
        """提取票据信息（包含印章信息）

        Args:
            ocr_text: OCR 识别的文本
            seals: 印章信息列表

        Returns:
            结构化的票据信息（含印章分析）
        """
        result = self.chain.extract(ocr_text)

        # 添加印章信息
        if seals:
            seal_info = self._analyze_seals(seals)
            result["seal_analysis"] = seal_info
            result["seals"] = seals  # 同时保存印章列表

        return result

    def _analyze_seals(self, seals: list) -> dict:
        """分析印章信息

        Args:
            seals: 印章列表

        Returns:
            印章分析结果
        """
        seal_types = [s["type"] for s in seals]

        return {
            "count": len(seals),
            "types": seal_types,
            "has_official_seal": "公章" in seal_types,
            "has_finance_seal": "财务专用章" in seal_types,
            "has_invoice_seal": "发票专用章" in seal_types,
            "has_supervision_seal": "发票监制章" in seal_types,
            "authenticity_hint": self._get_authenticity_hint(seal_types)
        }

    def _get_authenticity_hint(self, seal_types: list) -> str:
        """根据印章类型给出真伪提示

        Args:
            seal_types: 印章类型列表

        Returns:
            真伪提示信息
        """
        if "发票专用章" in seal_types:
            return "发票专用章齐全，建议通过税务局官网验证真伪"
        elif "财务专用章" in seal_types:
            return "有财务专用章，请确认是否有发票专用章"
        elif "公章" in seal_types:
            return "有公章，建议确认是否有发票专用章"
        elif "发票监制章" in seal_types:
            return "检测到发票监制章（预印），建议核实是否有发票专用章"
        else:
            return "未检测到标准印章，请人工核实"
```

### 7. 分类链 (src/chains/classification_chain.py)

```python
"""分类链"""
from typing import Optional
from ..llm import ReceiptExtractionChain
from ..config import get_api_key


# 报销类别映射
REIMBURSEMENT_CATEGORIES = {
    "增值税专用发票": "办公费用",
    "增值税普通发票": "办公费用",
    "火车票": "交通费",
    "出租车票": "交通费",
    "住宿发票": "住宿费",
    "餐饮发票": "餐饮费",
    "其他": "其他"
}


class ClassificationChain:
    """分类链

    负责对票据进行智能分类
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: AIStudio API Key，默认从环境变量读取
        """
        self.chain = ReceiptExtractionChain(api_key or get_api_key())

    def classify(self, ocr_text: str) -> dict:
        """分类票据

        Args:
            ocr_text: OCR 识别的文本

        Returns:
            分类结果，包含票据类型和报销类别
        """
        receipt_type = self.chain.classify(ocr_text)
        category = REIMBURSEMENT_CATEGORIES.get(receipt_type, "其他")

        return {
            "receipt_type": receipt_type,
            "reimbursement_category": category
        }

    def classify_batch(self, ocr_texts: list) -> list:
        """批量分类票据

        Args:
            ocr_texts: OCR 文本列表

        Returns:
            分类结果列表
        """
        return [self.classify(text) for text in ocr_texts]

    def get_category_summary(self, classification_results: list) -> dict:
        """获取分类统计

        Args:
            classification_results: 分类结果列表

        Returns:
            各类别数量统计
        """
        summary = {}
        for result in classification_results:
            category = result.get("reimbursement_category", "其他")
            summary[category] = summary.get(category, 0) + 1

        return summary
```

### 8. ERINE + LangChain 封装 (src/llm/ernie.py)

```python
"""ERINE API 封装"""
import json
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from typing import Optional

# AIStudio ERINE 配置
ERINE_BASE_URL = "https://aistudio.baidu.com/llm/lmapi/v3"
ERINE_MODEL = "ernie-4.5-turbo-128k-preview"


class ERINEClient:
    """ERINE API 客户端 (AIStudio OpenAI 兼容)"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: AIStudio Access Token
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=ERINE_BASE_URL,
        )

    def chat(self, messages: list, stream: bool = False) -> str:
        """发送聊天请求

        Args:
            messages: 消息列表
            stream: 是否流式输出

        Returns:
            模型回复内容
        """
        response = self.client.chat.completions.create(
            model=ERINE_MODEL,
            messages=messages,
            stream=stream,
            temperature=0.8,
            top_p=0.8,
            max_completion_tokens=12000,
        )

        if stream:
            result = []
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    if hasattr(chunk.choices[0].delta, "content"):
                        result.append(chunk.choices[0].delta.content or "")
            return "".join(result)
        else:
            return response.choices[0].message.content


class ReceiptExtractionChain:
    """票据信息提取链

    使用 LangChain + ERINE 从 OCR 文本中提取结构化信息
    """

    EXTRACTION_PROMPT = """你是一个专业的票据信息提取助手。请从以下 OCR 识别文本中提取关键信息。

OCR 文本：
{ocr_text}

请提取以下字段（如果存在）：
- 票据类型：[增值税发票/火车票/出租车票/其他]
- 发票代码：
- 发票号码：
- 开票日期：
- 购买方名称：
- 购买方税号：
- 销售方名称：
- 销售方税号：
- 金额（不含税）：
- 税额：
- 价税合计：
- 印章信息：

要求：
1. 请以 JSON 格式返回结果，确保字段名使用英文
2. 日期格式统一为 YYYY-MM-DD
3. 金额保留两位小数
4. 如果某字段不存在，值设为 null
5. 只返回 JSON，不要其他说明文字

返回格式示例：
{{
    "receipt_type": "增值税发票",
    "invoice_code": "1234567890",
    "invoice_number": "12345678",
    "date": "2024-01-15",
    "buyer_name": "某某公司",
    "buyer_tax_id": "91110000XXXXXXXXXX",
    "seller_name": "某某商家",
    "seller_tax_id": "91110000YYYYYYYYYY",
    "amount": "1000.00",
    "tax": "60.00",
    "total": "1060.00",
    "seal_info": "发票专用章"
}}"""

    CLASSIFICATION_PROMPT = """请判断以下票据文本属于哪种类型。

OCR 文本：
{ocr_text}

请从以下类型中选择一个：
- 增值税专用发票
- 增值税普通发票
- 火车票
- 出租车票
- 住宿发票
- 其他

只返回类型名称，不要其他说明。"""

    VALIDATION_PROMPT = """请验证以下票据信息是否合理。

票据信息：
{receipt_info}

请检查：
1. 日期是否合理（不是未来日期，且在合理范围内）
2. 金额计算是否正确（金额 + 税额 = 价税合计）
3. 必填字段是否完整

请返回 JSON 格式：
{{
    "is_valid": true/false,
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"]
}}"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: AIStudio Access Token
        """
        # 使用 LangChain 的 ChatOpenAI 封装
        self.llm = ChatOpenAI(
            model=ERINE_MODEL,
            api_key=api_key,
            base_url=ERINE_BASE_URL,
            temperature=0.1,  # 低温度保证提取准确性
        )

        # 提取链
        self.extraction_prompt = PromptTemplate(
            template=self.EXTRACTION_PROMPT,
            input_variables=["ocr_text"]
        )
        self.extraction_chain = self.extraction_prompt | self.llm

        # 分类链
        self.classification_prompt = PromptTemplate(
            template=self.CLASSIFICATION_PROMPT,
            input_variables=["ocr_text"]
        )
        self.classification_chain = self.classification_prompt | self.llm

        # 验证链
        self.validation_prompt = PromptTemplate(
            template=self.VALIDATION_PROMPT,
            input_variables=["receipt_info"]
        )
        self.validation_chain = self.validation_prompt | self.llm

    def extract(self, ocr_text: str) -> dict:
        """从 OCR 文本中提取结构化信息

        Args:
            ocr_text: OCR 识别的文本

        Returns:
            结构化的票据信息字典
        """
        response = self.extraction_chain.invoke({"ocr_text": ocr_text})
        content = response.content

        # 尝试解析 JSON
        try:
            # 尝试提取 JSON 块
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            return json.loads(json_str)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始内容
            return {
                "raw_response": content,
                "parse_error": "无法解析为 JSON"
            }

    def classify(self, ocr_text: str) -> str:
        """对票据进行分类

        Args:
            ocr_text: OCR 识别的文本

        Returns:
            票据类型
        """
        response = self.classification_chain.invoke({"ocr_text": ocr_text})
        return response.content.strip()

    def validate(self, receipt_info: dict) -> dict:
        """验证票据信息

        Args:
            receipt_info: 票据信息字典

        Returns:
            验证结果
        """
        response = self.validation_chain.invoke({
            "receipt_info": json.dumps(receipt_info, ensure_ascii=False, indent=2)
        })
        content = response.content

        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            return json.loads(json_str)
        except json.JSONDecodeError:
            return {
                "is_valid": True,
                "raw_response": content
            }
```

### 9. 验证器 (src/utils/validators.py)

```python
"""校验函数"""
from typing import Optional
from datetime import datetime
import re


def validate_amount(amount: Optional[str], tax: Optional[str], total: Optional[str]) -> dict:
    """验证金额计算是否正确

    Args:
        amount: 金额（不含税）
        tax: 税额
        total: 价税合计

    Returns:
        验证结果
    """
    issues = []

    if not all([amount, tax, total]):
        return {
            "is_valid": True,
            "issues": ["金额信息不完整，无法验证"]
        }

    try:
        amount_val = float(amount.replace(",", "").replace("￥", ""))
        tax_val = float(tax.replace(",", "").replace("￥", ""))
        total_val = float(total.replace(",", "").replace("￥", ""))

        calculated_total = amount_val + tax_val

        if abs(calculated_total - total_val) > 0.01:
            issues.append(
                f"金额计算有误：{amount_val} + {tax_val} = {calculated_total}，"
                f"但发票显示 {total_val}"
            )
    except (ValueError, AttributeError) as e:
        issues.append(f"金额格式错误：{str(e)}")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues
    }


def validate_date(date_str: Optional[str]) -> dict:
    """验证日期是否合理

    Args:
        date_str: 日期字符串

    Returns:
        验证结果
    """
    issues = []

    if not date_str:
        return {
            "is_valid": True,
            "issues": ["日期为空"]
        }

    # 尝试多种日期格式
    date_formats = [
        "%Y-%m-%d",
        "%Y年%m月%d日",
        "%Y/%m/%d",
        "%Y%m%d",
        "%d %b %Y",
    ]

    parsed_date = None
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue

    if not parsed_date:
        issues.append(f"无法解析日期格式：{date_str}")
        return {
            "is_valid": False,
            "issues": issues
        }

    # 检查是否为未来日期
    today = datetime.now()
    if parsed_date > today:
        issues.append("日期为未来日期，请核实")

    # 检查是否过于久远（超过5年）
    days_diff = (today - parsed_date).days
    if days_diff > 365 * 5:
        issues.append(f"日期距今已超过5年（{days_diff // 365}年），请确认是否有效")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "parsed_date": parsed_date.strftime("%Y-%m-%d")
    }


def validate_receipt(receipt_info: dict) -> dict:
    """验证票据信息完整性

    Args:
        receipt_info: 票据信息字典

    Returns:
        验证结果
    """
    issues = []
    warnings = []

    # 必填字段检查
    required_fields = {
        "receipt_type": "票据类型",
        "date": "开票日期",
    }

    for field, name in required_fields.items():
        if not receipt_info.get(field):
            issues.append(f"缺少必填字段：{name}")

    # 发票特有字段检查
    receipt_type = receipt_info.get("receipt_type", "")
    if "发票" in receipt_type:
        invoice_fields = {
            "invoice_code": "发票代码",
            "invoice_number": "发票号码",
            "buyer_name": "购买方名称",
            "seller_name": "销售方名称",
        }
        for field, name in invoice_fields.items():
            if not receipt_info.get(field):
                warnings.append(f"建议补充字段：{name}")

    # 金额验证
    amount_result = validate_amount(
        receipt_info.get("amount"),
        receipt_info.get("tax"),
        receipt_info.get("total")
    )
    issues.extend(amount_result.get("issues", []))

    # 日期验证
    date_result = validate_date(receipt_info.get("date"))
    issues.extend(date_result.get("issues", []))

    # 印章检查
    seals = receipt_info.get("seals", [])
    if not seals and "发票" in receipt_type:
        warnings.append("未检测到印章，建议人工核实发票真伪")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }


def validate_tax_id(tax_id: Optional[str]) -> dict:
    """验证纳税人识别号格式

    Args:
        tax_id: 纳税人识别号

    Returns:
        验证结果
    """
    if not tax_id:
        return {
            "is_valid": True,
            "issues": ["纳税人识别号为空"]
        }

    # 中国纳税人识别号通常是 15、17、18 或 20 位
    tax_id = tax_id.strip()

    if not re.match(r"^[0-9A-Z]+$", tax_id):
        return {
            "is_valid": False,
            "issues": ["纳税人识别号格式错误，只能包含数字和大写字母"]
        }

    if len(tax_id) not in [15, 17, 18, 20]:
        return {
            "is_valid": False,
            "issues": [f"纳税人识别号长度异常：{len(tax_id)}位（通常为15/17/18/20位）"]
        }

    return {
        "is_valid": True,
        "issues": []
    }
```

### 10. CLI 入口 (src/main.py)

```python
"""主入口模块 - CLI 和 Web 启动"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from .config import get_api_key
from .chains import OCRChain, ExtractionChain, ClassificationChain
from .utils import validate_receipt
from .web import launch_app


console = Console()


def recognize_single(
    file_path: str,
    output: Optional[str] = None,
    enable_seal: bool = True,
    verbose: bool = False
) -> dict:
    """识别单张票据

    Args:
        file_path: 图片路径
        output: 输出文件路径
        enable_seal: 是否启用印章识别
        verbose: 是否显示详细信息

    Returns:
        识别结果
    """
    with console.status("[bold green]正在识别票据...") as status:
        # OCR 识别
        status.update("[bold blue]正在进行 OCR 识别...")
        ocr_chain = OCRChain(get_api_key())
        ocr_result = ocr_chain.process(file_path, enable_seal)

        # 信息提取
        status.update("[bold blue]正在提取信息...")
        extraction_chain = ExtractionChain(get_api_key())
        extracted_info = extraction_chain.extract_with_seals(
            ocr_result["text"],
            ocr_result["seals"]
        )

        # 分类
        status.update("[bold blue]正在分类...")
        classification_chain = ClassificationChain(get_api_key())
        classification = classification_chain.classify(ocr_result["text"])
        extracted_info["reimbursement_category"] = classification["reimbursement_category"]

        # 验证
        validation = validate_receipt(extracted_info)
        extracted_info["validation_result"] = validation

    # 显示结果
    display_result(extracted_info, ocr_result["seals"], verbose)

    # 保存结果
    if output:
        save_result(extracted_info, output)

    return extracted_info


def display_result(info: dict, seals: list, verbose: bool = False):
    """显示识别结果"""
    # 基本信息
    table = Table(title="票据信息")
    table.add_column("字段", style="cyan")
    table.add_column("值", style="green")

    fields = [
        ("票据类型", info.get("receipt_type")),
        ("发票代码", info.get("invoice_code")),
        ("发票号码", info.get("invoice_number")),
        ("开票日期", info.get("date")),
        ("购买方", info.get("buyer_name")),
        ("销售方", info.get("seller_name")),
        ("金额", info.get("amount")),
        ("税额", info.get("tax")),
        ("价税合计", info.get("total")),
        ("报销类别", info.get("reimbursement_category")),
    ]

    for name, value in fields:
        if value:
            table.add_row(name, str(value))

    console.print(table)

    # 印章信息
    if seals:
        seal_table = Table(title="印章信息")
        seal_table.add_column("类型", style="cyan")
        seal_table.add_column("状态", style="green")

        for seal in seals:
            seal_table.add_row(seal.get("type", "未知"), "已识别")

        console.print(seal_table)

        if info.get("seal_analysis"):
            hint = info["seal_analysis"].get("authenticity_hint", "")
            console.print(f"\n[bold]真伪提示:[/bold] {hint}")

    # 验证结果
    validation = info.get("validation_result", {})
    if validation:
        if validation.get("is_valid"):
            console.print("\n[bold green]验证通过[/bold green]")
        else:
            console.print("\n[bold red]验证失败[/bold red]")
            for issue in validation.get("issues", []):
                console.print(f"  - {issue}")


def save_result(result: dict, output: str):
    """保存结果到文件"""
    output_path = Path(output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    console.print(f"[bold green]结果已保存到: {output_path}[/bold green]")


def cli():
    """CLI 入口"""
    parser = argparse.ArgumentParser(
        description="智能票据报销助手 - PaddleOCR + LangChain + ERINE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 识别单张票据
  uv run python -m src.main recognize invoice.jpg

  # 识别并保存结果
  uv run python -m src.main recognize invoice.jpg --output result.json

  # 批量识别
  uv run python -m src.main batch ./invoices/ --output ./results/

  # 启动 Web 界面
  uv run python -m src.main web
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # recognize 命令
    recognize_parser = subparsers.add_parser("recognize", help="识别单张票据")
    recognize_parser.add_argument("file", help="票据图片路径")
    recognize_parser.add_argument("--output", "-o", help="输出文件路径")
    recognize_parser.add_argument("--no-seal", action="store_true", help="禁用印章识别")
    recognize_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")

    # web 命令
    web_parser = subparsers.add_parser("web", help="启动 Web 界面")
    web_parser.add_argument("--share", action="store_true", help="创建公共链接")
    web_parser.add_argument("--port", type=int, default=7860, help="端口号")
    web_parser.add_argument("--host", default="0.0.0.0", help="主机地址")

    args = parser.parse_args()

    if args.command == "recognize":
        recognize_single(
            args.file,
            args.output,
            enable_seal=not args.no_seal,
            verbose=args.verbose
        )

    elif args.command == "web":
        console.print(Panel.fit(
            "[bold green]智能票据报销助手[/bold green]\n"
            "基于 PaddleOCR-VL-1.5 + LangChain + ERINE",
            border_style="green"
        ))
        launch_app(share=args.share, server_name=args.host, server_port=args.port)

    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
```

### 11. Gradio Web 应用 (src/web/app.py)

```python
"""Gradio Web 应用"""
import gradio as gr
import json
from typing import Optional, List
from datetime import datetime
from pathlib import Path

from ..config import get_api_key
from ..chains import OCRChain, ExtractionChain, ClassificationChain
from ..utils import validate_receipt
from .components import (
    create_upload_component,
    create_result_component,
    create_sample_component,
    format_seal_info,
    format_validation_result,
    get_sample_path,
    SAMPLE_INVOICES
)


def process_single_receipt(
    file_path: str,
    enable_seal: bool = True
) -> tuple:
    """处理单张票据"""
    if not file_path:
        return None, "", [], "请上传文件", ""

    try:
        api_key = get_api_key()
        # OCR 识别
        ocr_chain = OCRChain(api_key)
        ocr_result = ocr_chain.process(file_path, enable_seal)

        # 信息提取
        extraction_chain = ExtractionChain(api_key)
        extracted_info = extraction_chain.extract_with_seals(
            ocr_result["text"],
            ocr_result["seals"]
        )

        # 分类
        classification_chain = ClassificationChain(api_key)
        classification = classification_chain.classify(ocr_result["text"])
        extracted_info["reimbursement_category"] = classification["reimbursement_category"]

        # 验证
        validation = validate_receipt(extracted_info)
        extracted_info["validation_result"] = validation

        # 格式化印章信息
        seal_images, seal_info_text = format_seal_info(
            ocr_result["seals"],
            extracted_info.get("seal_analysis")
        )

        # 格式化验证结果
        validation_text = format_validation_result(validation)

        return (
            extracted_info,
            ocr_result["text"],
            seal_images,
            seal_info_text,
            validation_text
        )

    except Exception as e:
        return None, "", [], f"处理出错：{str(e)}", ""


def process_sample(sample_file: str, enable_seal: bool = True) -> tuple:
    """处理样本发票"""
    try:
        file_path = get_sample_path(sample_file)
        sample_info = next(
            (s for s in SAMPLE_INVOICES if s["file"] == sample_file),
            {"name": sample_file, "description": ""}
        )
        info_text = f"类型: {sample_info.get('type', '未知')} | {sample_info.get('description', '')}"
        result = process_single_receipt(file_path, enable_seal)
        return (file_path,) + result + (info_text,)

    except Exception as e:
        return None, None, "", [], f"处理出错：{str(e)}", "", ""


def create_app() -> gr.Blocks:
    """创建 Gradio 应用"""
    with gr.Blocks(title="智能票据报销助手") as app:
        gr.Markdown(
            """
            # 智能票据报销助手
            基于 PaddleOCR-VL-1.5 + LangChain + ERINE 的票据识别与信息提取系统

            **特色功能**：支持印章识别，辅助验证发票真伪
            """
        )

        with gr.Tabs():
            # 单张识别
            with gr.TabItem("单张识别"):
                with gr.Row():
                    # 左侧：上传区域 + 样本发票
                    with gr.Column(scale=1):
                        upload_col, file_input, enable_seal, submit_btn = create_upload_component()

                        gr.Markdown("---")

                        sample_col, sample_buttons, sample_info = create_sample_component()

                    # 右侧：结果展示
                    with gr.Column(scale=2):
                        right_col, result_json, result_text, seal_gallery, seal_info, validation_status = create_result_component()

                # 绑定上传识别按钮
                submit_btn.click(
                    fn=process_single_receipt,
                    inputs=[file_input, enable_seal],
                    outputs=[result_json, result_text, seal_gallery, seal_info, validation_status]
                )

                # 绑定样本按钮
                for btn, sample in sample_buttons:
                    btn.click(
                        fn=lambda s=sample["file"], e=enable_seal: process_sample(s, e),
                        inputs=[],
                        outputs=[file_input, result_json, result_text, seal_gallery, seal_info, validation_status, sample_info]
                    )

        gr.Markdown(
            """
            ---
            **使用说明**：
            1. 上传票据文件（支持 PDF 和图片格式：jpg, png, bmp, tiff, webp）
            2. 或点击左侧样本发票按钮，快速体验识别效果
            3. 查看识别结果和印章信息

            **支持的票据类型**：增值税发票、火车票、出租车票等
            """
        )

    return app


def launch_app(share: bool = False, server_name: str = "0.0.0.0", server_port: int = 7860):
    """启动 Gradio 应用"""
    app = create_app()
    app.launch(
        share=share,
        server_name=server_name,
        server_port=server_port
    )


if __name__ == "__main__":
    launch_app()
```

### 12. UI 组件 (src/web/components.py)

```python
"""UI 组件"""
import gradio as gr
from typing import Optional, Tuple
from PIL import Image
import io
import requests
from pathlib import Path


# 支持的文件格式
SUPPORTED_FILE_TYPES = [".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"]

# 样本发票路径
SAMPLES_DIR = Path(__file__).parent.parent.parent / "examples" / "sample_invoices"

# 样本发票信息
SAMPLE_INVOICES = [
    {
        "file": "dinner.pdf",
        "name": "餐饮发票",
        "type": "增值税发票",
        "description": "餐饮服务增值税发票"
    },
    {
        "file": "didi.pdf",
        "name": "滴滴出行",
        "type": "增值税发票",
        "description": "滴滴出行电子发票"
    },
    {
        "file": "train.pdf",
        "name": "火车票",
        "type": "火车票",
        "description": "铁路电子客票"
    },
    {
        "file": "invoice1.png",
        "name": "增值税发票",
        "type": "增值税发票",
        "description": "增值税普通发票（含印章）"
    },
    {
        "file": "invoice2.png",
        "name": "航空发票",
        "type": "其他",
        "description": "航空服务发票"
    }
]


def create_upload_component() -> Tuple:
    """创建上传组件"""
    with gr.Column() as col:
        gr.Markdown("### 上传票据文件")
        gr.Markdown("支持 PDF 和图片格式（增值税发票、火车票、出租车票等）")

        file_input = gr.File(
            label="票据文件",
            file_types=SUPPORTED_FILE_TYPES,
            type="filepath"
        )

        with gr.Row():
            enable_seal = gr.Checkbox(
                label="启用印章识别",
                value=True,
                info="识别发票上的公章、财务章等"
            )

        submit_btn = gr.Button(
            "识别票据",
            variant="primary",
            size="lg"
        )

    return col, file_input, enable_seal, submit_btn


def create_sample_component() -> Tuple:
    """创建样本发票组件"""
    with gr.Column() as col:
        gr.Markdown("### 样本发票")
        gr.Markdown("点击下方按钮，快速体验识别效果")

        sample_buttons = []

        # 第一行：3个按钮
        with gr.Row():
            for sample in SAMPLE_INVOICES[:3]:
                btn = gr.Button(
                    f"{sample['name']}",
                    variant="secondary",
                    size="sm"
                )
                sample_buttons.append((btn, sample))

        # 第二行：2个按钮
        with gr.Row():
            for sample in SAMPLE_INVOICES[3:]:
                btn = gr.Button(
                    f"{sample['name']}",
                    variant="secondary",
                    size="sm"
                )
                sample_buttons.append((btn, sample))

        # 显示样本信息
        sample_info = gr.Textbox(
            label="样本说明",
            value="点击上方按钮选择样本发票",
            interactive=False,
            lines=2
        )

    return col, sample_buttons, sample_info


def create_result_component() -> Tuple:
    """创建结果展示组件"""
    with gr.Column() as col:
        gr.Markdown("### 识别结果")

        with gr.Tabs():
            with gr.TabItem("结构化信息"):
                result_json = gr.JSON(
                    label="提取的字段"
                )

            with gr.TabItem("原始文本"):
                result_text = gr.Textbox(
                    label="OCR 识别文本",
                    lines=10,
                    max_lines=20
                )

            with gr.TabItem("印章信息"):
                seal_gallery = gr.Gallery(
                    label="识别到的印章",
                    columns=3,
                    height=200
                )
                seal_info = gr.Textbox(
                    label="印章分析",
                    lines=3
                )

        with gr.Row():
            validation_status = gr.Textbox(
                label="验证状态",
                interactive=False
            )

    return col, result_json, result_text, seal_gallery, seal_info, validation_status


def format_seal_info(seals: list, analysis: Optional[dict]) -> Tuple[list, str]:
    """格式化印章信息用于展示"""
    images = []
    for seal in seals:
        try:
            # 下载印章图片
            response = requests.get(seal["url"], timeout=10)
            img = Image.open(io.BytesIO(response.content))
            images.append((img, seal["type"]))
        except Exception:
            continue

    if analysis:
        info_text = f"""印章数量：{analysis.get('count', 0)}
印章类型：{', '.join(analysis.get('types', []))}
真伪提示：{analysis.get('authenticity_hint', '')}"""
    else:
        info_text = "未检测到印章"

    return images, info_text


def format_validation_result(validation: dict) -> str:
    """格式化验证结果"""
    if validation.get("is_valid"):
        status = "验证通过"
    else:
        status = "验证失败"

    issues = validation.get("issues", [])
    warnings = validation.get("warnings", [])

    result = f"**{status}**\n\n"

    if issues:
        result += "**问题：**\n"
        for issue in issues:
            result += f"- {issue}\n"

    if warnings:
        result += "\n**警告：**\n"
        for warning in warnings:
            result += f"- {warning}\n"

    return result


def get_sample_path(sample_file: str) -> str:
    """获取样本文件路径"""
    return str(SAMPLES_DIR / sample_file)
```

### 13. ModelScope 入口 (app.py)

```python
"""
智能票据报销助手 - ModelScope 创空间入口
基于 PaddleOCR-VL-1.5 + LangChain + ERINE
"""
import os

# 设置环境变量（ModelScope 创空间会自动注入）
if not os.getenv("AISTUDIO_API_KEY"):
    # 尝试从 ModelScope 环境变量获取
    api_key = os.getenv("MODELSCOPE_API_KEY") or os.getenv("API_KEY")
    if api_key:
        os.environ["AISTUDIO_API_KEY"] = api_key

from src.web import launch_app

if __name__ == "__main__":
    launch_app(server_name="0.0.0.0", server_port=7860)
```

### 14. 环境变量配置 (.env.example)

```bash
# PaddleOCR Access Token (推荐)
# 获取方式: https://www.paddleocr.com -> API -> PaddleOCR-VL-1.5
PADDLEOCR_ACCESS_TOKEN=your_paddleocr_token_here

# PaddleOCR API URL (可选，有默认值)
PADDLEOCR_API_URL=https://q6mbb0r0t8m9q4pf.aistudio-app.com/layout-parsing

# 向后兼容: 也可以使用 AISTUDIO_API_KEY
# AISTUDIO_API_KEY=your_aistudio_api_key_here
```

**获取 Token 步骤**：
1. 访问 https://www.paddleocr.com
2. 点击顶部导航栏【API】
3. 选择【PaddleOCR-VL-1.5】
4. 复制 TOKEN 到 `.env` 文件

### 15. 模块初始化文件

**src/chains/__init__.py**:
```python
"""LangChain 链模块"""
from .ocr_chain import OCRChain
from .extraction_chain import ExtractionChain
from .classification_chain import ClassificationChain

__all__ = ["OCRChain", "ExtractionChain", "ClassificationChain"]
```

**src/llm/__init__.py**:
```python
"""LLM 模块"""
from .ernie import ERINEClient, ReceiptExtractionChain

__all__ = ["ERINEClient", "ReceiptExtractionChain"]
```

**src/utils/__init__.py**:
```python
"""工具函数模块"""
from .validators import validate_receipt, validate_amount, validate_date
from .seal_extractor import extract_seals_from_response, classify_seal

__all__ = [
    "validate_receipt",
    "validate_amount",
    "validate_date",
    "extract_seals_from_response",
    "classify_seal"
]
```

**src/web/__init__.py**:
```python
"""Web 模块"""
from .app import create_app, launch_app

__all__ = ["create_app", "launch_app"]
```

---

## 关键踩坑提醒

### 1. 兼容层必须最先导入

```python
# 错误：直接导入 langchain_paddleocr
from langchain_paddleocr import PaddleOCRVLLoader  # 会报错！

# 正确：先设置兼容层
from src.langchain_compat import setup_langchain_compat
setup_langchain_compat()

from langchain_paddleocr import PaddleOCRVLLoader  # 正常工作
```

### 2. API Key 延迟验证

```python
# 错误：导入时立即验证，会导致 ImportError
API_KEY = os.getenv("AISTUDIO_API_KEY")
if not API_KEY:
    raise ValueError("请配置 API Key")

# 正确：调用时才验证
def get_api_key() -> str:
    api_key = os.getenv("PADDLEOCR_ACCESS_TOKEN") or os.getenv("AISTUDIO_API_KEY")
    if not api_key:
        raise ValueError("请配置 API Key")
    return api_key
```

### 3. 印章提取位置

```python
# 印章可能在两个位置，都要检查
# 位置1: res["outputImages"]
# 位置2: res["markdown"]["images"]

# 推荐使用独立的 seal_extractor.py 模块
from src.utils.seal_extractor import extract_seals_from_response
seals = extract_seals_from_response(raw_response)
```

### 4. Gradio 文件上传

```python
# 错误：gr.Image 不支持 PDF
file_input = gr.Image()

# 正确：使用 gr.File
file_input = gr.File(
    file_types=[".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"],
    type="filepath"
)
```

### 5. uv 环境管理

```bash
# 错误：使用 pip
pip install -r requirements.txt

# 正确：使用 uv
uv sync
uv run python -m src.main recognize invoice.pdf
```

### 6. ModelScope 部署

```bash
# ModelScope 使用 master 分支，不是 main
git push origin master
```

---

## 测试验证步骤

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/your-username/smart-receipt-assistant.git
cd smart-receipt-assistant

# 安装 uv（如果未安装）
# Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/macOS:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 PADDLEOCR_ACCESS_TOKEN
```

### 2. CLI 测试

```bash
# 识别单张票据
uv run python -m src.main recognize examples/sample_invoices/dinner.pdf

# 识别并保存结果
uv run python -m src.main recognize examples/sample_invoices/train.pdf --output result.json

# 禁用印章识别
uv run python -m src.main recognize invoice.jpg --no-seal

# 启动 Web 界面
uv run python -m src.main web
```

### 3. Web 测试

```bash
# 启动 Web 服务
uv run python app.py

# 或使用 CLI 命令
uv run python -m src.main web --port 7860

# 创建公共链接
uv run python -m src.main web --share
```

### 4. 功能验证清单

- [ ] **OCR 识别**
  - [ ] PDF 文件识别
  - [ ] 图片文件识别（jpg, png, bmp, tiff, webp）
  - [ ] 错误文件处理

- [ ] **印章识别**
  - [ ] 发票专用章识别
  - [ ] 财务专用章识别
  - [ ] 公章识别
  - [ ] 发票监制章识别

- [ ] **信息提取**
  - [ ] 发票代码/号码提取
  - [ ] 金额提取
  - [ ] 日期提取
  - [ ] 购买方/销售方信息提取

- [ ] **分类功能**
  - [ ] 增值税发票分类
  - [ ] 火车票分类
  - [ ] 出租车票分类
  - [ ] 报销类别自动分配

- [ ] **Web 界面**
  - [ ] 文件上传
  - [ ] 样本发票按钮
  - [ ] 结果展示
  - [ ] 导出功能

### 5. 单元测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_ocr.py -v

# 带覆盖率
uv run pytest --cov=src
```

---

## 部署指南

### ModelScope 创空间

1. **创建创空间**
   - 访问 https://modelscope.cn/studios
   - 点击「创建创空间」
   - 选择 Gradio SDK

2. **配置环境变量**
   - 在创空间设置中添加：
   - `PADDLEOCR_ACCESS_TOKEN` 或 `AISTUDIO_API_KEY`

3. **推送代码**
   ```bash
   # ModelScope 使用 master 分支
   git push origin master
   ```

### GitHub 开源

```bash
# 添加 GitHub 远程仓库
git remote add github https://github.com/your-username/smart-receipt-assistant.git

# 推送到 GitHub
git push github main
```

---

## 参考链接

- [langchain-paddleocr 官方文档](https://github.com/PaddlePaddle/PaddleOCR/tree/main/docs/ppocr/langchain)
- [PaddleOCR 官方网站](https://www.paddleocr.com)
- [LangChain 官方文档](https://python.langchain.com/)
- [百度 AIStudio](https://aistudio.baidu.com/)
- [uv 包管理器](https://docs.astral.sh/uv/)
- [国家税务总局发票查验](https://inv-veri.chinatax.gov.cn)
