# 智能票据报销助手 - 项目开发提示词

> 使用此提示词指导 Claude Code 从零开始完成「智能票据报销助手」项目

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
| OCR | PaddleOCR-VL-1.5 云端 API | 无需本地安装，支持印章识别 |
| LLM | ERINE（文心一言） | 中文理解强，OpenAI 兼容 API |
| 编排 | LangChain | 链式工作流，模型无关性 |
| Web | Gradio | 快速搭建界面 |
| 部署 | ModelScope 创空间 | 百度生态集成 |

**关键优势**：
- 一个 AIStudio API Key 同时用于 OCR 和 LLM
- 云端 API，无需本地安装 PaddlePaddle
- 支持 PDF 和图片格式自动检测

---

## 项目结构

```
smart-receipt-assistant/
├── app.py                  # 创空间入口
├── requirements.txt        # 依赖列表
├── .env.example           # 环境变量模板
├── src/
│   ├── __init__.py
│   ├── main.py            # CLI 入口
│   ├── config.py          # 配置管理
│   ├── ocr/
│   │   ├── __init__.py
│   │   └── paddle_ocr.py  # PaddleOCR API 封装
│   ├── llm/
│   │   ├── __init__.py
│   │   └── ernie.py       # ERINE + LangChain 封装
│   ├── web/
│   │   ├── __init__.py
│   │   ├── app.py         # Gradio 应用
│   │   └── components.py  # UI 组件
│   └── utils/
│       ├── __init__.py
│       └── validators.py  # 验证函数
├── examples/
│   └── sample_invoices/   # 样本发票
└── docs/
    └── blog.md            # 技术博客
```

---

## 核心实现代码

### 1. 依赖配置 (requirements.txt)

```txt
# Core
openai>=1.0.0
langchain>=0.1.0
langchain-community>=0.0.1
langchain-openai>=0.1.0
requests>=2.31.0
pydantic>=2.0.0
python-dotenv>=1.0.0

# UI
gradio>=4.0.0
rich>=13.0.0
pillow>=10.0.0

# Export
openpyxl>=3.1.0
```

### 2. 配置管理 (src/config.py)

```python
"""配置管理"""
import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key() -> str:
    """获取 API Key（延迟验证，避免导入时报错）"""
    api_key = os.getenv("AISTUDIO_API_KEY")
    if not api_key:
        raise ValueError(
            "请配置 AISTUDIO_API_KEY 环境变量\n"
            "获取方式：https://aistudio.baidu.com/"
        )
    return api_key

# PaddleOCR-VL-1.5 配置
PADDLEOCR_API_URL = "https://q6mbb0r0t8m9q4pf.aistudio-app.com/layout-parsing"

# ERINE 配置
ERINE_BASE_URL = "https://aistudio.baidu.com/llm/lmapi/v3"
ERINE_MODEL = "ernie-4.5-turbo-128k-preview"
```

### 3. PaddleOCR API 封装 (src/ocr/paddle_ocr.py)

```python
"""PaddleOCR-VL-1.5 云端 API 封装"""
import base64
import requests
from typing import Tuple
from pathlib import Path


class PaddleOCRVL:
    """PaddleOCR-VL-1.5 云端 API 封装

    特色功能：
    - 票据文字识别
    - 印章识别（独有功能）
    - 支持 PDF 和图片格式（自动检测）
    """

    API_URL = "https://q6mbb0r0t8m9q4pf.aistudio-app.com/layout-parsing"

    # 文件类型映射（重要！）
    FILE_TYPE_PDF = 0     # PDF 文档
    FILE_TYPE_IMAGE = 1   # 图片文件

    SUPPORTED_PDF_EXTENSIONS = {".pdf"}
    SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
    SUPPORTED_EXTENSIONS = SUPPORTED_PDF_EXTENSIONS | SUPPORTED_IMAGE_EXTENSIONS

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"token {api_key}",
            "Content-Type": "application/json"
        }

    def _get_file_type(self, file_path: str) -> Tuple[int, str]:
        """自动检测文件类型

        Returns:
            (文件类型代码, 类型描述)
            PDF=0, 图片=1
        """
        ext = Path(file_path).suffix.lower()
        if ext in self.SUPPORTED_PDF_EXTENSIONS:
            return self.FILE_TYPE_PDF, "PDF文档"
        elif ext in self.SUPPORTED_IMAGE_EXTENSIONS:
            return self.FILE_TYPE_IMAGE, "图片"
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    def recognize(self, file_path: str, use_seal_recognition: bool = True) -> dict:
        """识别票据（自动检测文件类型）"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 自动检测文件类型
        file_type, _ = self._get_file_type(file_path)

        # 读取并编码文件
        with open(path, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("ascii")

        payload = {
            "file": file_data,
            "fileType": file_type,  # 关键：PDF=0, 图片=1
            "useSealRecognition": use_seal_recognition,  # 开启印章识别
            "useLayoutDetection": True,
            "useDocOrientationClassify": False,
            "useDocUnwarping": False,
            "useChartRecognition": False,
            "useOcrForImageBlock": False,
            "mergeTables": True,
            "layoutNms": True,
            "promptLabel": "ocr",
            "temperature": 0,
        }

        response = requests.post(
            self.API_URL,
            json=payload,
            headers=self.headers,
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("result", {})

    def extract_text(self, result: dict) -> str:
        """从识别结果中提取纯文本"""
        texts = []
        for res in result.get("layoutParsingResults", []):
            markdown = res.get("markdown", {})
            text = markdown.get("text", "")
            if text:
                texts.append(text)
        return "\n\n".join(texts)

    def extract_seals(self, result: dict) -> list:
        """提取印章信息（检查两个位置）"""
        seals = []
        for i, res in enumerate(result.get("layoutParsingResults", [])):
            markdown = res.get("markdown", {})
            full_text = markdown.get("text", "")

            # 位置1: outputImages
            for img_name, img_url in res.get("outputImages", {}).items():
                if "seal" in img_name.lower():
                    seals.append({
                        "name": img_name,
                        "url": img_url,
                        "type": self._classify_seal(img_name, full_text)
                    })

            # 位置2: markdown.images
            for img_name, img_url in markdown.get("images", {}).items():
                if "seal" in img_name.lower():
                    seals.append({
                        "name": img_name,
                        "url": img_url,
                        "type": self._classify_seal(img_name, full_text)
                    })

        return seals

    def _classify_seal(self, name: str, surrounding_text: str = "") -> str:
        """判断印章类型"""
        combined = f"{name} {surrounding_text}".lower()

        if "发票专用章" in surrounding_text or "发票章" in surrounding_text:
            return "发票专用章"
        if "财务专用章" in surrounding_text or "财务章" in surrounding_text:
            return "财务专用章"
        if "公章" in surrounding_text:
            return "公章"
        if "监制章" in surrounding_text:
            return "发票监制章"
        if "合同章" in surrounding_text:
            return "合同章"

        return "其他印章"
```

### 4. ERINE + LangChain 封装 (src/llm/ernie.py)

```python
"""ERINE API 封装"""
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

ERINE_BASE_URL = "https://aistudio.baidu.com/llm/lmapi/v3"
ERINE_MODEL = "ernie-4.5-turbo-128k-preview"


class ReceiptExtractionChain:
    """票据信息提取链"""

    EXTRACTION_PROMPT = """你是一个专业的票据信息提取助手。

OCR 文本：
{ocr_text}

请提取以下字段（如果存在）：
- 票据类型：[增值税发票/火车票/出租车票/其他]
- 发票代码、发票号码、开票日期
- 购买方名称、购买方税号
- 销售方名称、销售方税号
- 金额（不含税）、税额、价税合计
- 印章信息

要求：
1. 以 JSON 格式返回，字段名使用英文
2. 日期格式 YYYY-MM-DD
3. 金额保留两位小数
4. 不存在的字段设为 null
5. 只返回 JSON，不要其他文字"""

    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model=ERINE_MODEL,
            api_key=api_key,
            base_url=ERINE_BASE_URL,
            temperature=0.1,
        )
        self.prompt = PromptTemplate(
            template=self.EXTRACTION_PROMPT,
            input_variables=["ocr_text"]
        )
        self.chain = self.prompt | self.llm

    def extract(self, ocr_text: str) -> dict:
        """从 OCR 文本中提取结构化信息"""
        response = self.chain.invoke({"ocr_text": ocr_text})
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
            return {"raw_response": content, "parse_error": "无法解析为 JSON"}
```

### 5. Gradio Web 界面 (src/web/app.py)

```python
"""Gradio Web 界面"""
import gradio as gr
from pathlib import Path

# 关键：使用 gr.File 而不是 gr.Image，因为 gr.Image 不支持 PDF
FILE_TYPES = [".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff"]

def create_app():
    with gr.Blocks(title="智能票据报销助手") as app:
        gr.Markdown("# 🧾 智能票据报销助手")

        with gr.Row():
            # 左侧：上传区 + 样本发票
            with gr.Column(scale=1):
                # 关键：使用 gr.File 支持 PDF
                file_input = gr.File(
                    label="上传发票",
                    file_types=FILE_TYPES,
                    type="filepath"
                )
                enable_seal = gr.Checkbox(
                    label="启用印章识别",
                    value=True
                )
                submit_btn = gr.Button("识别", variant="primary")

                # 样本发票按钮
                gr.Markdown("### 样本发票")
                sample_buttons = []
                samples = [
                    {"file": "dinner.pdf", "name": "餐饮发票"},
                    {"file": "train.pdf", "name": "火车票"},
                ]
                for sample in samples:
                    btn = gr.Button(sample["name"], size="sm")
                    sample_buttons.append((btn, sample))

            # 右侧：结果展示
            with gr.Column(scale=2):
                result_json = gr.JSON(label="提取结果")
                seal_gallery = gr.Gallery(label="印章图片", columns=3)
                validation_status = gr.Textbox(label="验证状态")

        return app

if __name__ == "__main__":
    app = create_app()
    app.launch()
```

---

## ⚠️ 关键踩坑提醒

### 1. API Key 延迟验证

```python
# ❌ 错误：导入时立即验证，会导致 ImportError
API_KEY = os.getenv("AISTUDIO_API_KEY")
if not API_KEY:
    raise ValueError("请配置 API Key")

# ✅ 正确：调用时才验证
def get_api_key() -> str:
    api_key = os.getenv("AISTUDIO_API_KEY")
    if not api_key:
        raise ValueError("请配置 API Key")
    return api_key
```

### 2. 文件类型参数

```python
# ❌ 错误
fileType = 2  # PDF

# ✅ 正确
FILE_TYPE_PDF = 0     # PDF 文档
FILE_TYPE_IMAGE = 1   # 图片文件
```

### 3. 印章提取位置

```python
# 印章可能在两个位置，都要检查
# 位置1: res["outputImages"]
# 位置2: res["markdown"]["images"]
```

### 4. Gradio 文件上传

```python
# ❌ 错误：gr.Image 不支持 PDF
file_input = gr.Image()

# ✅ 正确：使用 gr.File
file_input = gr.File(file_types=[".pdf", ".jpg", ".png"])
```

### 5. ModelScope 部署

```bash
# ModelScope 使用 master 分支，不是 main
git push origin master
```

---

## 测试验证步骤

### 1. 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 AIStudio API Key

# 测试 CLI
python -m src.main recognize invoice.pdf

# 测试 Web
python -m src.main web
```

### 2. 功能验证

- [ ] PDF 文件识别
- [ ] 图片文件识别
- [ ] 印章识别
- [ ] 结构化提取
- [ ] Web 界面上传
- [ ] 样本发票按钮

---

## 部署指南

### ModelScope 创空间

1. 创建创空间：https://modelscope.cn/studios
2. 添加环境变量：`AISTUDIO_API_KEY`
3. 推送代码到 `master` 分支

### GitHub 开源

```bash
git remote add github https://github.com/your-username/smart-receipt-assistant.git
git push github main
```

---

## 参考链接

- [PaddleOCR 官方文档](https://github.com/PaddlePaddle/PaddleOCR)
- [LangChain 官方文档](https://python.langchain.com/)
- [百度 AIStudio](https://aistudio.baidu.com/)
- [国家税务总局发票查验](https://inv-veri.chinatax.gov.cn)
