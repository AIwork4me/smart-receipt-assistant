# 当 OCR 遇上大模型：用 PaddleOCR + LangChain + 文心一言打造智能票据助手

> 本文将介绍如何使用 PaddleOCR-VL-1.5、LangChain 和文心一言（ERINE）打造一个智能票据报销助手，重点展示 PaddleOCR 独有的印章识别能力。

**在线体验**：[ModelScope 创空间](https://modelscope.cn/studios/Devkit/reciept-agent) | **开源代码**：[GitHub](https://github.com/AIwork4me/smart-receipt-assistant)

## 一、引言：报销那些痛

每个月的报销季，是多少职场人的噩梦。

翻开抽屉，一堆发票、火车票、出租车票杂乱无章。增值税发票要填发票代码、发票号码、购买方、销售方、金额、税额……火车票要填车次、出发站、到达站……光是手动录入这些信息，就要花上大半天。

更让人头疼的是，发票真假难辨。财务说这张发票没有发票专用章，那张发票章不清晰……一趟报销跑下来，心力交瘁。

能不能有个工具，拍张照就自动识别发票信息，顺便还能看看印章是否齐全？

答案是：**当然可以！**

本文将带你打造一个智能票据报销助手，结合 **PaddleOCR-VL-1.5** 的票据识别能力（含印章识别）、**LangChain** 的工作流编排、**文心一言** 的语义理解能力，实现：

1. 自动识别票据类型（增值税发票/火车票等）
2. 提取关键字段（发票代码、金额、日期等）
3. **识别印章并辅助验证真伪**
4. 自动分类报销类别

## 二、技术选型：为什么是它们

在构建智能票据助手时，我们面临一个核心问题：**如何从一张发票图片得到结构化的数据？**

传统的方案各有局限：

| 方案 | 问题 |
|------|------|
| 只用 OCR | 只能输出原始文本，无法提取结构化字段 |
| OCR + 规则解析 | 发票格式多样，规则难以覆盖所有情况 |
| **OCR + LLM** | 理解语义，自动提取，适应不同格式 |

因此我们选择了 **PaddleOCR + LangChain + ERINE** 的组合。

### 2.1 为什么选择 PaddleOCR-VL-1.5？

PaddleOCR-VL-1.5 是百度飞桨团队推出的多模态文档理解模型，在票据识别场景有独特优势：

**1. 中文场景深度优化**

中国发票体系复杂，有独特的格式和字段：发票代码、发票号码、购买方税号、价税合计（大写）……PaddleOCR 针对中文场景进行了深度优化，识别准确率高。

```python
# 典型的中文发票 OCR 输出
"""
发票代码：1100221130
发票号码：12345678
购买方名称：某某科技有限公司
购买方纳税人识别号：91110000XXXXXXXXXX
价税合计（大写）：壹仟零陆拾元整
"""
```

**2. 独有的印章识别能力**

这是 PaddleOCR-VL-1.5 的**杀手级功能**。其他 OCR 只能识别文字，而 PaddleOCR 可以：

- 识别发票上的印章位置
- 提取印章图片
- 区分印章类型：发票专用章、财务专用章、公章、发票监制章等

```python
# 开启印章识别
result = ocr.recognize("invoice.jpg", use_seal_recognition=True)

# 提取印章
seals = ocr.extract_seals(result)
# [{'type': '发票专用章', 'url': 'https://...'}, ...]
```

**3. 云端 API，零配置启动**

无需本地安装 PaddlePaddle 框架，无需 GPU，一行代码即可调用：

```python
ocr = PaddleOCRVL(api_key="your_token")
result = ocr.recognize("invoice.pdf")  # 自动检测 PDF/图片
```

**4. 自动文件类型检测**

支持 PDF 和图片格式自动识别，无需手动指定：

```python
# 自动检测文件类型
file_type, type_desc = self._get_file_type(file_path)
# PDF 文件 → fileType=0
# 图片文件 → fileType=1
```

### 2.2 为什么选择 LangChain？

LangChain 是 LLM 应用开发的标准框架，解决了"如何组织 LLM 应用"的问题。

**1. 链式工作流编排**

票据处理是多步骤流程：OCR → 信息提取 → 分类 → 验证。LangChain 让每个环节独立、可复用：

```python
# 信息提取链
extraction_chain = ReceiptExtractionChain(api_key)
info = extraction_chain.extract(ocr_result["text"])

# 分类链
category = extraction_chain.classify(ocr_result["text"])

# 验证链
validation = extraction_chain.validate(info)
```

**2. Prompt 模板管理**

LLM 应用的核心是 Prompt。LangChain 提供了优雅的模板管理：

```python
EXTRACTION_PROMPT = """你是一个专业的票据信息提取助手。

OCR 文本：
{ocr_text}

请提取以下字段并以 JSON 格式返回：
- 票据类型、发票代码、发票号码、开票日期
- 购买方名称、销售方名称
- 金额、税额、价税合计
- 印章信息"""

prompt = PromptTemplate(
    template=EXTRACTION_PROMPT,
    input_variables=["ocr_text"]
)
```

**3. LCEL 表达式语言**

LangChain 的管道语法让代码更清晰：

```python
# Prompt → LLM → Output
self.extraction_chain = self.extraction_prompt | self.llm
result = self.extraction_chain.invoke({"ocr_text": text})
```

### 2.3 为什么选择 ERINE（文心一言）？

ERINE 是百度自研的大语言模型，在中文票据场景有独特优势。

**1. 中文理解能力出众**

发票是典型的中文文档，包含大量专业术语和特定表达：

```
"价税合计（大写）：壹仟零陆拾元整"
"购买方纳税人识别号：91110000XXXXXXXXXX"
"收款人：张三  复核人：李四  开票人：王五"
```

ERINE 对中文语义理解准确，能正确提取这些字段：

```python
# ERINE 提取结果
{
    "total": "1060.00",
    "total_chinese": "壹仟零陆拾元整",
    "buyer_tax_id": "91110000XXXXXXXXXX",
    "payee": "张三",
    "reviewer": "李四",
    "drawer": "王五"
}
```

**2. OpenAI 兼容 API**

ERINE 提供了 OpenAI 兼容接口，学习成本为零：

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_aistudio_token",
    base_url="https://aistudio.baidu.com/llm/lmapi/v3"
)

response = client.chat.completions.create(
    model="ernie-4.5-turbo-128k-preview",
    messages=[{"role": "user", "content": "提取发票信息..."}]
)
```

**3. 与 PaddleOCR 统一认证**

最贴心的是：**一个 API Key 搞定两个服务**

```python
# 只需一个 Token
AISTUDIO_API_KEY = "your_aistudio_token"

# 用于 PaddleOCR
ocr = PaddleOCRVL(AISTUDIO_API_KEY)

# 用于 ERINE
llm = ChatOpenAI(api_key=AISTUDIO_API_KEY, base_url="...")
```

这大大简化了配置，也降低了使用门槛。

**4. 128K 上下文，处理长文档无压力**

发票 OCR 结果可能很长，ERINE 支持 128K tokens 上下文，轻松处理：

```python
model="ernie-4.5-turbo-128k-preview"  # 128K 上下文
```

### 2.4 技术栈协同效应

三个技术组合在一起，产生了协同效应：

```
┌─────────────────────────────────────────────────────────────┐
│  发票图片 (PDF/JPG/PNG)                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PaddleOCR-VL-1.5                                           │
│  • 自动检测文件类型 (PDF=0, 图片=1)                           │
│  • 识别所有文字                                              │
│  • 提取印章图片                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  LangChain 编排                                              │
│  • OCR 链 → 提取链 → 分类链 → 验证链                          │
│  • Prompt 模板管理                                           │
│  • JSON 解析与错误处理                                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ERINE 大模型                                                │
│  • 理解 OCR 文本语义                                         │
│  • 提取结构化字段 (JSON)                                     │
│  • 判断票据类型                                              │
│  • 分析印章信息                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  结构化数据输出                                               │
│  {                                                          │
│    "receipt_type": "增值税发票",                              │
│    "invoice_number": "12345678",                            │
│    "total": "1060.00",                                      │
│    "seals": [{"type": "发票专用章"}]                          │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

## 三、项目架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户界面层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  CLI 命令行 │  │  Gradio Web │  │  样本体验   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangChain 编排层                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ OCR 识别链  │→│ 信息提取链  │→│ 分类验证链  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      能力层                                  │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ PaddleOCR-VL-1.5│  │   ERINE API     │                  │
│  │  (云端 API)     │  │  (语义理解)     │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## 四、核心实现

### 4.1 环境搭建

```bash
# 克隆项目
git clone https://github.com/AIwork4me/smart-receipt-assistant.git
cd smart-receipt-assistant

# 安装依赖
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env，填入 AIStudio Access Token
```

**只需一个 API Key**：PaddleOCR 和 ERINE 共用 AIStudio Access Token

```bash
# .env
AISTUDIO_API_KEY=your_token_here
```

### 4.2 PaddleOCR 票据识别

调用云端 API，无需本地安装 PaddlePaddle：

```python
import base64
import requests
from pathlib import Path

class PaddleOCRVL:
    API_URL = "https://q6mbb0r0t8m9q4pf.aistudio-app.com/layout-parsing"

    # 文件类型映射
    FILE_TYPE_PDF = 0     # PDF 文档
    FILE_TYPE_IMAGE = 1   # 图片文件

    def _get_file_type(self, file_path: str) -> tuple:
        """自动检测文件类型"""
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return self.FILE_TYPE_PDF, "PDF文档"
        elif ext in {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}:
            return self.FILE_TYPE_IMAGE, "图片"
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    def recognize(self, file_path: str, use_seal_recognition: bool = True) -> dict:
        # 自动检测文件类型
        file_type, _ = self._get_file_type(file_path)

        # 读取文件并编码
        with open(file_path, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("ascii")

        payload = {
            "file": file_data,
            "fileType": file_type,  # 自动检测: 0=PDF, 1=图片
            "useSealRecognition": use_seal_recognition,  # 开启印章识别
            "useLayoutDetection": True,
            "promptLabel": "ocr",
        }

        response = requests.post(
            self.API_URL,
            json=payload,
            headers={"Authorization": f"token {self.api_key}"}
        )

        return response.json()["result"]
```

**印章识别结果**：

```python
def extract_seals(self, result: dict) -> list:
    """从识别结果中提取印章信息"""
    seals = []
    for i, res in enumerate(result.get("layoutParsingResults", [])):
        markdown = res.get("markdown", {})
        full_text = markdown.get("text", "")

        # 方法1: 从 outputImages 中提取
        for img_name, img_url in res.get("outputImages", {}).items():
            if "seal" in img_name.lower():
                seals.append({
                    "name": img_name,
                    "url": img_url,
                    "type": self._classify_seal(img_name, full_text)
                })

        # 方法2: 从 markdown.images 中提取
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

### 4.3 LangChain 链式处理

使用 LangChain 组织 OCR → 提取 → 分类 → 验证 的流程：

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import json

class ReceiptExtractionChain:
    EXTRACTION_PROMPT = """你是一个专业的票据信息提取助手。
请从以下 OCR 识别文本中提取关键信息。

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
1. 请以 JSON 格式返回结果，确保字段名使用英文
2. 日期格式统一为 YYYY-MM-DD
3. 金额保留两位小数
4. 如果某字段不存在，值设为 null
5. 只返回 JSON，不要其他说明文字"""

    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="ernie-4.5-turbo-128k-preview",
            api_key=api_key,
            base_url="https://aistudio.baidu.com/llm/lmapi/v3",
            temperature=0.1,  # 低温度保证提取准确性
        )

        # 使用 LCEL 管道语法
        self.extraction_prompt = PromptTemplate(
            template=self.EXTRACTION_PROMPT,
            input_variables=["ocr_text"]
        )
        self.extraction_chain = self.extraction_prompt | self.llm

    def extract(self, ocr_text: str) -> dict:
        """从 OCR 文本中提取结构化信息"""
        response = self.extraction_chain.invoke({"ocr_text": ocr_text})
        content = response.content

        # 解析 JSON 响应
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

### 4.4 完整流程演示

```bash
# CLI 使用
python -m src.main recognize invoice.jpg

# 输出示例
╭───────────────────────────────────────────╮
│ 智能票据报销助手                          │
│ 基于 PaddleOCR-VL-1.5 + LangChain + ERINE │
╰───────────────────────────────────────────╯

┌──────────────────────────────────────┐
│           票据信息                    │
├──────────────┬───────────────────────┤
│ 票据类型      │ 增值税专用发票         │
│ 发票代码      │ 1234567890            │
│ 发票号码      │ 12345678              │
│ 开票日期      │ 2024-01-15            │
│ 购买方        │ 某某科技有限公司        │
│ 销售方        │ 某某办公设备公司        │
│ 金额          │ 1000.00               │
│ 税额          │ 60.00                 │
│ 价税合计      │ 1060.00               │
└──────────────┴───────────────────────┘

┌──────────────────────────────────────┐
│           印章信息                    │
├──────────────┬───────────────────────┤
│ 发票专用章    │ 已识别                 │
│ 发票监制章    │ 已识别                 │
└──────────────┴───────────────────────┘

真伪提示: 发票专用章齐全，建议通过税务局官网验证真伪
验证通过
```

## 五、Web 界面体验

项目提供了 Gradio Web 界面，支持：

- **样本发票一键体验**：内置 5 张样本发票，无需上传即可体验
- **自定义上传**：支持 PDF/JPG/PNG 格式
- **印章可视化**：识别到的印章图片直接展示
- **验证状态**：实时显示验真结果

```bash
# 启动 Web 界面
python app.py

# 或使用 CLI
python -m src.main web
```

**在线体验**：[ModelScope 创空间](https://modelscope.cn/studios/Devkit/reciept-agent)

## 六、发票验真：如何判断发票真伪？

发票验真是票据报销的核心需求。本方案实现了**三层辅助验真**，并预留了接入税务局 API 的扩展接口。

### 6.1 当前实现：三层辅助验真

#### 第一层：印章识别

PaddleOCR-VL-1.5 可以识别发票上的印章类型：

| 印章类型 | 说明 | 验真价值 |
|---------|------|---------|
| 发票专用章 | 企业盖在发票上的章 | ⭐⭐⭐ 高 - 有此章更可信 |
| 财务专用章 | 企业财务部门印章 | ⭐⭐ 中 - 辅助判断 |
| 公章 | 企业公章 | ⭐⭐ 中 - 辅助判断 |
| 发票监制章 | 发票上预印的官方章 | ⭐ 低 - 所有发票都有 |
| 合同章 | 合同专用章 | ⭐ 低 - 非发票专用 |

```python
# 印章识别代码
seals = ocr.extract_seals(result)
# [{'type': '发票专用章', 'url': 'https://...'}, ...]

# 印章分析
seal_types = [s["type"] for s in seals]
if "发票专用章" in seal_types:
    hint = "发票专用章齐全，建议通过税务局官网验证真伪"
elif "发票监制章" in seal_types:
    hint = "检测到发票监制章（预印），建议核实是否有发票专用章"
else:
    hint = "未检测到发票专用章，建议人工核实"
```

#### 第二层：字段校验

对提取的字段进行逻辑校验：

```python
# 金额计算校验
amount + tax == total  # 价税合计是否正确

# 日期合理性
date <= today  # 不是未来日期
date > 5_years_ago  # 不是过期太久

# 必填字段检查
required = ["invoice_code", "invoice_number", "date", "buyer_name", "seller_name"]
```

#### 第三层：完整性检查

检查发票信息是否完整：

```python
def validate_receipt(receipt_info: dict) -> dict:
    issues = []
    warnings = []

    # 发票特有字段检查
    if "发票" in receipt_info.get("receipt_type", ""):
        if not receipt_info.get("invoice_code"):
            warnings.append("建议补充字段：发票代码")

    # 印章检查
    if not receipt_info.get("seals"):
        warnings.append("未检测到印章，建议人工核实发票真伪")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }
```

### 6.2 当前方案的局限性

当前实现只能**辅助判断**，无法确认发票真伪：

| 局限性 | 说明 |
|--------|------|
| 印章可伪造 | 只能判断是否有章，无法判断真假 |
| OCR 有误差 | 识别结果可能有错误 |
| 无法联网验证 | 不知道发票是否在税务系统登记 |

### 6.3 扩展方案：接入税务局 API

要实现真正的发票验真，需要接入**国家税务总局查验平台**。

#### 验真需要的核心信息

```python
# 税务局验真必填参数
{
    "invoice_code": "1100221130",    # 发票代码
    "invoice_number": "12345678",     # 发票号码
    "invoice_date": "20190219",       # 开票日期 (YYYYMMDD)
    "check_code": "123456",           # 校验码后6位（增值税发票）
    "total_amount": "1060.00"         # 价税合计（部分发票需要）
}
```

#### 验真流程

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   发票图片      │ ──→ │  OCR 识别       │ ──→ │  提取关键信息   │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                         ┌───────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     税务局发票查验 API                        │
│  https://inv-veri.chinatax.gov.cn                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       验证结果                               │
│  • 发票是否存在：是/否                                        │
│  • 开票方信息：名称、税号                                     │
│  • 当前状态：有效/作废/红冲                                   │
└─────────────────────────────────────────────────────────────┘
```

### 6.4 验真方式对比

| 验真方式 | 准确性 | 成本 | 实现难度 | 推荐场景 |
|---------|-------|------|---------|---------|
| 印章识别 | 低 | 免费 | 低 | 初步筛选 |
| 字段校验 | 中 | 免费 | 低 | 数据质量检查 |
| 税务局 API | **高** | 免费额度 | 中 | **正式验真** |
| 第三方服务 | 高 | 收费 | 低 | 企业快速接入 |

**推荐方案**：印章识别 + 字段校验作为第一道防线，有条件时接入税务局 API 实现真正的验真。

## 七、踩坑经验

### 7.1 OCR 识别优化

**问题**：模糊图片识别率低

**解决**：
1. 上传前进行图像预处理（调整对比度、去噪）
2. 确保图片分辨率足够（建议 300 DPI 以上）
3. 光线均匀，避免阴影

### 7.2 Prompt 优化

**问题**：LLM 提取字段不准确

**解决**：使用 Few-shot 示例 + 明确的输出格式要求

```python
PROMPT = """请从以下文本中提取发票信息。

要求：
1. 以 JSON 格式返回
2. 日期格式统一为 YYYY-MM-DD
3. 金额保留两位小数
4. 不存在的字段设为 null
5. 只返回 JSON，不要其他说明文字

示例输出：
{
    "receipt_type": "增值税发票",
    "invoice_code": "1100221130",
    "invoice_number": "12345678",
    "amount": "1000.00"
}

现在请处理：
{ocr_text}
"""
```

### 7.3 印章识别注意事项

1. 印章清晰度影响识别效果
2. 红色印章识别效果最好
3. 复印件上的印章可能识别不准确
4. 印章图片可能在 `outputImages` 或 `markdown.images` 中，需要都检查

### 7.4 文件类型检测

**问题**：PDF 和图片需要不同的 `fileType` 参数

**解决**：根据文件扩展名自动检测

```python
def _get_file_type(self, file_path: str) -> tuple:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return 0, "PDF文档"  # fileType=0
    else:
        return 1, "图片"      # fileType=1
```

## 八、总结与展望

### 项目总结

本文介绍了如何使用 PaddleOCR + LangChain + ERINE 打造智能票据报销助手：

1. **PaddleOCR-VL-1.5**：实现票据 OCR 和印章识别
2. **LangChain**：组织 OCR → 提取 → 分类 → 验证的工作流
3. **ERINE**：理解 OCR 文本，提取结构化字段

**亮点**：
- 印章识别是 PaddleOCR-VL-1.5 的独有功能
- 支持 PDF 和图片格式自动检测
- 统一的 AIStudio API Key 配置
- Gradio Web 界面 + 样本发票一键体验

### 开源地址

- **GitHub**：https://github.com/AIwork4me/smart-receipt-assistant
- **在线体验**：https://modelscope.cn/studios/Devkit/reciept-agent

欢迎 Star 和 PR！

### 后续优化方向

1. **接入税务局 API 实现真正的发票验真**
2. **支持更多票据类型**：航空行程单、定额发票、过路费发票
3. **添加报销单自动生成功能**
4. **部署为服务，接入企业 OA 系统**

---

**参考资料**：

- [PaddleOCR 官方文档](https://github.com/PaddlePaddle/PaddleOCR)
- [LangChain 官方文档](https://python.langchain.com/)
- [百度 AIStudio](https://aistudio.baidu.com/)
- [国家税务总局发票查验平台](https://inv-veri.chinatax.gov.cn)
