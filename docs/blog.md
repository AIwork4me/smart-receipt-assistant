# 当 OCR 遇上大模型：用 PaddleOCR + LangChain + 文心一言打造智能票据助手

> 本文将介绍如何使用 PaddleOCR-VL-1.5、LangChain 和文心一言（ERINE）打造一个智能票据报销助手，重点展示 PaddleOCR 独有的印章识别能力。

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
- 区分印章类型：发票专用章、财务专用章、公章等

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

支持 PDF 和图片格式自动识别，`fileType` 参数自动配置：
- `fileType=0`：PDF 文档
- `fileType=1`：图片文件

### 2.2 为什么选择 LangChain？

LangChain 是 LLM 应用开发的标准框架，解决了"如何组织 LLM 应用"的问题。

**1. 链式工作流编排**

票据处理是多步骤流程：OCR → 信息提取 → 分类 → 验证。LangChain 让每个环节独立、可复用：

```python
# OCR 识别链
ocr_chain = OCRChain(api_key)
ocr_result = ocr_chain.process("invoice.jpg")

# 信息提取链
extraction_chain = ExtractionChain(api_key)
info = extraction_chain.extract(ocr_result["text"])

# 分类链
classification_chain = ClassificationChain(api_key)
category = classification_chain.classify(ocr_result["text"])
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
- 金额、税额、价税合计"""

prompt = PromptTemplate(
    template=EXTRACTION_PROMPT,
    input_variables=["ocr_text"]
)
```

**3. 模型无关性**

今天用 ERINE，明天想换 GPT-4？LangChain 让切换模型只需改一行代码：

```python
# 使用 ERINE
llm = ChatOpenAI(
    model="ernie-4.5-turbo-128k-preview",
    base_url="https://aistudio.baidu.com/llm/lmapi/v3"
)

# 切换到 GPT-4
llm = ChatOpenAI(model="gpt-4")

# 切换到 Claude
llm = ChatAnthropic(model="claude-3-opus")
```

**4. LCEL 表达式语言**

LangChain 的管道语法让代码更清晰：

```python
# Prompt → LLM → Output
chain = prompt | llm | output_parser
result = chain.invoke({"ocr_text": text})
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
│  • 自动检测文件类型 (PDF/图片)                                │
│  • 识别所有文字                                              │
│  • 提取印章图片                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  LangChain 编排                                              │
│  • OCR 链 → 提取链 → 分类链 → 验证链                          │
│  • Prompt 模板管理                                           │
│  • 错误处理与重试                                            │
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
│  │  CLI 命令行 │  │  Gradio Web │  │  批量处理   │         │
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

使用 uv 管理依赖，配置简单：

```toml
# pyproject.toml
[project]
name = "smart-receipt-assistant"
dependencies = [
    "openai>=1.0.0",        # ERINE API
    "langchain>=0.1.0",
    "langchain-openai>=0.1.0",
    "gradio>=4.0.0",
    "pillow>=10.0.0",
    "openpyxl>=3.1.0",
]
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

class PaddleOCRVL:
    API_URL = "https://q6mbb0r8m9q4pf.aistudio-app.com/layout-parsing"

    def recognize(self, file_path: str, use_seal_recognition: bool = True) -> dict:
        # 读取图片并编码
        with open(file_path, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("ascii")

        payload = {
            "file": file_data,
            "fileType": 1,
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
# 提取印章信息
def extract_seals(self, result: dict) -> list:
    seals = []
    for res in result.get("layoutParsingResults", []):
        for img_name, img_url in res.get("outputImages", {}).items():
            if "seal" in img_name.lower():
                seals.append({
                    "name": img_name,
                    "url": img_url,
                    "type": self._classify_seal(img_name)  # 判断印章类型
                })
    return seals
```

### 4.3 LangChain 链式处理

使用 LangChain 组织 OCR → 提取 → 分类 的流程：

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

class ReceiptExtractionChain:
    EXTRACTION_PROMPT = """你是一个专业的票据信息提取助手。
请从以下 OCR 识别文本中提取关键信息。

OCR 文本：
{ocr_text}

请提取以下字段并以 JSON 格式返回：
- 票据类型、发票代码、发票号码、开票日期
- 购买方名称、销售方名称
- 金额、税额、价税合计
- 印章信息"""

    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="ernie-4.5-turbo-128k-preview",
            api_key=api_key,
            base_url="https://aistudio.baidu.com/llm/lmapi/v3",
            temperature=0.1,  # 低温度保证准确性
        )
        self.prompt = PromptTemplate(
            template=self.EXTRACTION_PROMPT,
            input_variables=["ocr_text"]
        )
        self.chain = self.prompt | self.llm

    def extract(self, ocr_text: str) -> dict:
        response = self.chain.invoke({"ocr_text": ocr_text})
        return json.loads(response.content)
```

### 4.4 完整流程演示

```python
# CLI 使用
uv run python -m src.main recognize invoice.jpg

# 输出示例
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
│ 财务专用章    │ 已识别                 │
└──────────────┴───────────────────────┘

真伪提示: 发票专用章齐全，建议通过税务局官网验证真伪
验证通过
```

## 五、效果展示

### 5.1 增值税发票识别

上传一张增值税发票图片：

- OCR 识别：提取发票上所有文字
- 信息提取：自动提取发票代码、号码、金额等字段
- 印章识别：检测发票专用章、财务章
- 验证：金额计算校验、日期合理性检查

### 5.2 火车票识别

上传火车票图片：

- 自动识别为"火车票"类型
- 提取车次、出发站、到达站、座位、票价
- 自动归类为"交通费"

### 5.3 批量处理

批量上传多张票据：

- 自动生成汇总报表
- 统计各类别金额
- 导出 Excel 格式

## 六、发票验真：如何判断发票真伪？

发票验真是票据报销的核心需求。本方案实现了**三层辅助验真**，并预留了接入税务局 API 的扩展接口。

### 6.1 当前实现：三层辅助验真

#### 第一层：印章识别

PaddleOCR-VL-1.5 可以识别发票上的印章类型：

| 印章类型 | 说明 | 验真价值 |
|---------|------|---------|
| 发票专用章 | 企业盖在发票上的章 | **高** - 有此章更可信 |
| 财务专用章 | 企业财务部门印章 | 中 - 辅助判断 |
| 公章 | 企业公章 | 中 - 辅助判断 |
| 发票监制章 | 发票上预印的官方章 | 低 - 所有发票都有 |

```python
# 印章识别代码
seals = ocr.extract_seals(result)
# [{'type': '发票专用章', 'url': 'https://...'}, ...]

# 印章分析
if "发票专用章" in seal_types:
    hint = "发票专用章齐全，建议通过税务局官网验证真伪"
elif "发票监制章" in seal_types:
    hint = "检测到发票监制章（预印），建议核实是否有发票专用章"
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

#### 验真效果示例

```
┌─────────────────────────────────────────────────────────────┐
│  invoice1.png 验真结果                                       │
├─────────────────────────────────────────────────────────────┤
│  印章识别：发票专用章 × 2                                     │
│  金额校验：900.00 = 774.33 + 125.67 ✓                        │
│  日期检查：2019-02-19（距今7年，需确认是否有效）               │
│  真伪提示：发票专用章齐全，建议通过税务局官网验证真伪           │
└─────────────────────────────────────────────────────────────┘
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

#### 实现代码示例

```python
import requests
import hashlib

class InvoiceVerifier:
    """发票真伪验证（接入税务局 API）"""

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.api_url = "https://inv-veri.chinatax.gov.cn/api/query"

    def verify(self, invoice_info: dict) -> dict:
        """验证发票真伪"""
        params = {
            "fpdm": invoice_info["invoice_code"],    # 发票代码
            "fphm": invoice_info["invoice_number"],  # 发票号码
            "kprq": invoice_info["date"].replace("-", ""),
            "kjje": invoice_info["total"],
            "yzm": invoice_info.get("check_code", "")[-6:],
        }

        # 生成签名并调用 API
        sign = self._generate_sign(params)
        response = requests.post(
            self.api_url,
            json={**params, "sign": sign},
            headers={"AppKey": self.app_key}
        )

        return response.json()
```

#### 验证结果示例

```json
{
    "code": "0000",
    "message": "查询成功",
    "data": {
        "exist": true,
        "invoiceCode": "1100221130",
        "invoiceNumber": "12345678",
        "sellerName": "某某科技有限公司",
        "sellerTaxId": "91110000XXXXXXXXXX",
        "totalAmount": "1060.00",
        "status": "有效"
    }
}
```

### 6.4 第三方验真服务

如果无法直接接入税务局 API，可以使用第三方服务：

| 服务商 | 特点 | 费用 |
|--------|------|------|
| 百度 AI 发票验真 | OCR + 验真一体 | 按次收费 |
| 阿里云发票验真 | 支持多种发票类型 | 按次收费 |
| 腾讯云发票验真 | 高并发支持 | 按次收费 |

### 6.5 验真方式对比

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

**解决**：使用 Few-shot 示例

```python
PROMPT = """请从以下文本中提取发票信息。

示例：
输入：发票代码：1100221130，发票号码：12345678，金额：￥1000.00
输出：{"invoice_code": "1100221130", "invoice_number": "12345678", "amount": "1000.00"}

现在请处理：
{ocr_text}
"""
```

### 7.3 印章识别注意事项

1. 印章清晰度影响识别效果
2. 红色印章识别效果最好
3. 复印件上的印章可能识别不准确

## 八、总结与展望

### 项目总结

本文介绍了如何使用 PaddleOCR + LangChain + ERINE 打造智能票据报销助手：

1. **PaddleOCR-VL-1.5**：实现票据 OCR 和印章识别
2. **LangChain**：组织 OCR → 提取 → 分类的工作流
3. **ERINE**：理解 OCR 文本，提取结构化字段

**亮点**：印章识别是 PaddleOCR-VL-1.5 的独有功能，可用于辅助验证发票真伪。

### 后续优化方向

**1. 接入税务局 API 实现真正的发票验真**

```python
# 扩展验真模块
# src/verification/tax_api.py
class TaxBureauAPI:
    """税务局发票查验 API"""

    def verify(self, invoice_info: dict) -> dict:
        # 调用税务局接口
        # 返回发票状态：有效/作废/红冲
        pass
```

申请地址：https://inv-veri.chinatax.gov.cn

**2. 支持更多票据类型**

- 航空行程单
- 定额发票
- 过路费发票
- 银行回单

**3. 添加报销单自动生成功能**

- 根据识别结果自动填写报销单
- 关联企业费用科目
- 生成报销汇总表

**4. 部署为服务，接入企业 OA 系统**

- 提供 REST API
- 支持批量导入导出
- 与企业财务系统对接

### 开源地址

完整代码已开源：`smart-receipt-assistant/`

欢迎 Star 和 PR！

---

**参考资料**：

- [PaddleOCR 官方文档](https://github.com/PaddlePaddle/PaddleOCR)
- [LangChain 官方文档](https://python.langchain.com/)
- [百度 AIStudio](https://aistudio.baidu.com/)
