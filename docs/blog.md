# 当 OCR 遇上大模型：用 LangChain-paddleocr + ERINE 打造智能票据助手

> 本文将介绍如何使用官方 langchain-paddleocr 集成包、LangChain 和文心一言（ERINE）打造一个智能票据报销助手，重点展示三大技术组件如何协同解决中小企业的发票处理痛点。

**在线体验**：[ModelScope 创空间](https://modelscope.cn/studios/Devkit/reciept-agent) | **开源代码**：[GitHub](https://github.com/AIwork4me/smart-receipt-assistant)

---

## 一、引言：中小企业的发票处理痛点

每个月的报销季，是多少财务人员和职场人的噩梦。

**对于中小企业来说，发票处理面临三大挑战：**

### 1. 人工成本高

```
一张发票，需要录入：
- 发票代码、发票号码、开票日期
- 购买方名称、购买方税号
- 销售方名称、销售方税号
- 金额、税额、价税合计
- 印章信息...

100 张发票 = 半天工作量
```

中小企业往往没有专职财务，发票处理成为负担。

### 2. 发票真伪难辨

```
财务说：
- "这张发票没有发票专用章"
- "那张发票章不清晰"
- "这张发票代码和号码对不上"

真假发票肉眼难辨，一旦报销了假发票，企业面临税务风险。
```

### 3. 报销流程繁琐

```
传统报销流程：
1. 收集纸质发票
2. 手动录入信息
3. 贴票、签字
4. 财务审核
5. 打款报销

全程人工，效率低下。
```

**能不能有个工具，拍张照就自动识别发票信息，顺便还能验证真伪？**

答案是：**当然可以！**

本文将带你打造一个智能票据报销助手，实现：

1. **自动识别**票据类型（增值税发票/火车票等）
2. **智能提取**关键字段（发票代码、金额、日期等）
3. **印章识别**辅助验证真伪
4. **自动分类**报销类别
5. **一键导出**Excel 报销单

---

## 二、技术选型：为什么是它们

在构建智能票据助手时，我们选择 **LangChain + langchain-paddleocr + ERINE** 的组合。

### 2.1 为什么选择 LangChain？

LangChain 是 LLM 应用开发的事实标准框架，它解决了"如何组织 LLM 应用"的核心问题。

#### 票据处理是多步骤流程

```
发票图片 → OCR 识别 → 信息提取 → 分类 → 验证
```

LangChain 让每个环节独立、可复用，形成**链式工作流**：

```python
# 使用 LangChain 组织票据处理流程
ocr_chain = OCRChain(api_key)
extraction_chain = ExtractionChain(api_key)
classification_chain = ClassificationChain(api_key)

# 链式调用
ocr_result = ocr_chain.process(file_path)
info = extraction_chain.extract(ocr_result["text"])
category = classification_chain.classify(ocr_result["text"])
```

#### LangChain 的核心价值

| 能力 | 说明 | 在票据场景的应用 |
|------|------|-----------------|
| **链式编排** | 将多步骤流程组织为链 | OCR → 提取 → 分类 → 验证 |
| **Prompt 模板** | 管理 LLM 的输入输出 | 发票信息提取的标准化 Prompt |
| **输出解析** | 将 LLM 输出转为结构化数据 | JSON 格式的发票信息 |
| **生态集成** | 与各种工具无缝对接 | langchain-paddleocr、langchain-openai |

#### 使用 LCEL 表达式语言

LangChain 的管道语法让代码更清晰：

```python
# Prompt → LLM → JSON Parser
extraction_chain = (
    {"ocr_text": itemgetter("ocr_text")}
    | extraction_prompt
    | llm
    | JsonOutputParser()
)

result = extraction_chain.invoke({"ocr_text": ocr_text})
```

### 2.2 为什么选择 langchain-paddleocr？

**2024 年，LangChain 正式集成了 PaddleOCR-VL-1.5！**

这意味着 PaddleOCR 成为 LangChain 生态的**一等公民**，可以像其他 Document Loader 一样使用。

#### 官方集成的优势

```python
# 之前：自定义封装，需要自己维护
from src.ocr import PaddleOCRVL
ocr = PaddleOCRVL(api_key)
result = ocr.recognize(file_path)

# 现在：官方集成，开箱即用
from langchain_paddleocr import PaddleOCRVLLoader
from pydantic import SecretStr

loader = PaddleOCRVLLoader(
    file_path="invoice.pdf",
    api_url="your-api-endpoint",
    access_token=SecretStr("your-token"),
    use_seal_recognition=True,  # 开启印章识别
)

docs = loader.load()
print(docs[0].page_content)  # OCR 识别的文本
```

#### PaddleOCR-VL-1.5 的独有优势

**1. 中文场景深度优化**

中国发票体系复杂，有独特的格式和字段：发票代码、发票号码、购买方税号、价税合计（大写）……PaddleOCR 针对中文场景进行了深度优化，识别准确率高。

**2. 独有的印章识别能力**

这是 PaddleOCR-VL-1.5 的**杀手级功能**：

```python
loader = PaddleOCRVLLoader(
    file_path="invoice.jpg",
    use_seal_recognition=True,  # 开启印章识别
)

docs = loader.load()

# 访问原始 API 响应，提取印章信息
raw_response = docs[0].metadata["paddleocr_vl_raw_response"]
seals = extract_seals_from_response(raw_response)
# [{'type': '发票专用章', 'url': 'https://...'}, ...]
```

**3. 云端 API，零配置启动**

无需本地安装 PaddlePaddle 框架，无需 GPU，一行代码即可调用。

**4. 自动文件类型检测**

支持 PDF 和图片格式自动识别：

```python
# 自动检测文件类型
PaddleOCRVLLoader(file_path="invoice.pdf")   # PDF
PaddleOCRVLLoader(file_path="invoice.jpg")   # 图片
PaddleOCRVLLoader(file_path="invoice.png")   # 图片
```

#### 印章识别：发票验真的关键

| 印章类型 | 说明 | 验真价值 |
|---------|------|---------|
| 发票专用章 | 企业盖在发票上的章 | 高 - 有此章更可信 |
| 财务专用章 | 企业财务部门印章 | 中 - 辅助判断 |
| 公章 | 企业公章 | 中 - 辅助判断 |
| 发票监制章 | 发票上预印的官方章 | 低 - 所有发票都有 |

### 2.3 为什么选择 ERINE（文心一言）？

ERINE 是百度自研的大语言模型，在中文票据场景有独特优势。

#### 中文理解能力出众

发票是典型的中文文档，包含大量专业术语：

```
"价税合计（大写）：壹仟零陆拾元整"
"购买方纳税人识别号：91110000XXXXXXXXXX"
"收款人：张三  复核人：李四  开票人：王五"
```

ERINE 能准确理解这些表达并提取结构化信息：

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

#### OpenAI 兼容 API

ERINE 提供了 OpenAI 兼容接口，学习成本为零：

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="ernie-4.5-turbo-128k-preview",
    api_key="your_aistudio_token",
    base_url="https://aistudio.baidu.com/llm/lmapi/v3"
)
```

#### 与 PaddleOCR 统一认证

最贴心的是：**一个 API Key 搞定两个服务**

```python
# 只需一个 Token
PADDLEOCR_ACCESS_TOKEN = "your_token"

# 用于 PaddleOCR
loader = PaddleOCRVLLoader(access_token=SecretStr(PADDLEOCR_ACCESS_TOKEN))

# 用于 ERINE
llm = ChatOpenAI(api_key=PADDLEOCR_ACCESS_TOKEN, base_url="...")
```

这大大简化了配置，降低了使用门槛。

#### 128K 上下文，处理长文档无压力

```python
model="ernie-4.5-turbo-128k-preview"  # 128K 上下文
```

### 2.4 三大组件的协同效应

三个技术组合在一起，产生了协同效应：

```
┌─────────────────────────────────────────────────────────────┐
│  发票图片 (PDF/JPG/PNG)                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  langchain-paddleocr (PaddleOCRVLLoader)                     │
│  • 自动检测文件类型                                           │
│  • 识别所有文字 (page_content)                               │
│  • 开启印章识别 (use_seal_recognition=True)                  │
│  • 保存原始响应 (metadata["paddleocr_vl_raw_response"])      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  LangChain 编排层                                            │
│  • OCR 链 → 提取链 → 分类链 → 验证链                          │
│  • Prompt 模板管理                                           │
│  • JSON 解析与错误处理                                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ERINE 大模型 (langchain-openai)                             │
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
│    "seals": [{"type": "发票专用章"}],                         │
│    "reimbursement_category": "办公费用"                       │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、技术实现：如何协同解决问题

### 3.1 项目架构

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
│  │(PaddleOCR)  │  │  (ERINE)    │  │  (ERINE)    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      能力层                                  │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ langchain-      │  │  langchain-     │                  │
│  │ paddleocr       │  │  openai(ERINE)  │                  │
│  │ (OCR+印章)      │  │  (语义理解)     │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 OCR 识别链：使用官方 langchain-paddleocr

```python
from langchain_paddleocr import PaddleOCRVLLoader
from pydantic import SecretStr

class OCRChain:
    """OCR 处理链 - 基于官方 PaddleOCRVLLoader"""

    def __init__(self, api_key: str, api_url: str):
        self.access_token = SecretStr(api_key)
        self.api_url = api_url

    def process(self, file_path: str, enable_seal: bool = True) -> dict:
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
        raw_response = docs[0].metadata.get("paddleocr_vl_raw_response", {})
        seals = extract_seals_from_response(raw_response)

        return {
            "text": text,
            "seals": seals,
            "raw_result": raw_response,
            "documents": docs
        }
```

### 3.3 印章提取：从原始响应中提取

```python
def extract_seals_from_response(raw_response: dict) -> list:
    """从 PaddleOCR API 原始响应中提取印章信息"""
    seals = []
    result = raw_response.get("result", raw_response)
    layout_results = result.get("layoutParsingResults", [])

    for i, res in enumerate(layout_results):
        markdown = res.get("markdown", {})
        full_text = markdown.get("text", "")

        # 从 outputImages 中提取
        for img_name, img_url in res.get("outputImages", {}).items():
            if "seal" in img_name.lower():
                seals.append({
                    "name": img_name,
                    "url": img_url,
                    "page": i,
                    "type": classify_seal(img_name, full_text)
                })

        # 从 markdown.images 中提取
        for img_name, img_url in markdown.get("images", {}).items():
            if "seal" in img_name.lower():
                seals.append({
                    "name": img_name,
                    "url": img_url,
                    "page": i,
                    "type": classify_seal(img_name, full_text)
                })

    return seals

def classify_seal(name: str, surrounding_text: str = "") -> str:
    """判断印章类型"""
    if "发票专用章" in surrounding_text or "发票章" in surrounding_text:
        return "发票专用章"
    if "财务专用章" in surrounding_text or "财务章" in surrounding_text:
        return "财务专用章"
    if "公章" in surrounding_text:
        return "公章"
    if "监制章" in surrounding_text:
        return "发票监制章"
    if "合同" in surrounding_text and "章" in surrounding_text:
        return "合同章"
    return "其他印章"
```

### 3.4 信息提取链：使用 ERINE

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class ExtractionChain:
    """信息提取链 - 使用 ERINE 大模型"""

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

要求：
1. 以 JSON 格式返回结果
2. 日期格式统一为 YYYY-MM-DD
3. 金额保留两位小数
4. 不存在的字段设为 null
5. 只返回 JSON，不要其他说明文字"""

    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="ernie-4.5-turbo-128k-preview",
            api_key=api_key,
            base_url="https://aistudio.baidu.com/llm/lmapi/v3",
            temperature=0.1,
        )

        self.prompt = PromptTemplate(
            template=self.EXTRACTION_PROMPT,
            input_variables=["ocr_text"]
        )
        self.chain = self.prompt | self.llm

    def extract(self, ocr_text: str) -> dict:
        response = self.chain.invoke({"ocr_text": ocr_text})
        return parse_json_response(response.content)
```

### 3.5 完整流程演示

```python
# 初始化
api_key = get_paddleocr_token()
ocr_chain = OCRChain(api_key)
extraction_chain = ExtractionChain(api_key)
classification_chain = ClassificationChain(api_key)

# 处理发票
ocr_result = ocr_chain.process("invoice.jpg")

# 提取信息
info = extraction_chain.extract(ocr_result["text"])

# 分类
category = classification_chain.classify(ocr_result["text"])
info["reimbursement_category"] = category

# 验证
validation = validate_receipt(info)
info["validation_result"] = validation

# 输出
print(json.dumps(info, ensure_ascii=False, indent=2))
```

**输出示例：**

```json
{
  "receipt_type": "增值税专用发票",
  "invoice_code": "1100221130",
  "invoice_number": "12345678",
  "date": "2024-01-15",
  "buyer_name": "某某科技有限公司",
  "seller_name": "某某办公设备公司",
  "amount": "1000.00",
  "tax": "60.00",
  "total": "1060.00",
  "seals": [
    {"type": "发票专用章", "url": "https://..."}
  ],
  "seal_analysis": {
    "has_invoice_seal": true,
    "authenticity_hint": "发票专用章齐全，建议通过税务局官网验证真伪"
  },
  "reimbursement_category": "办公费用",
  "validation_result": {
    "is_valid": true,
    "issues": [],
    "warnings": []
  }
}
```

---

## 四、解决中小企业发票处理痛点

### 4.1 降低人工成本

| 传统方式 | 智能助手 |
|---------|---------|
| 手动录入，100 张发票 = 半天 | 自动识别，100 张发票 = 10 分钟 |
| 人工核对，容易出错 | 自动校验，准确率高 |
| 贴票、签字、扫描 | 电子化存储，一键导出 |

### 4.2 辅助发票验真

```
三层辅助验真：

1. 印章识别
   - 发票专用章 → 可信度高
   - 无发票专用章 → 需人工核实

2. 字段校验
   - 金额 + 税额 = 价税合计？
   - 日期是否合理？

3. 完整性检查
   - 必填字段是否齐全？
   - 发票代码/号码是否存在？
```

### 4.3 简化报销流程

```
智能报销流程：

1. 批量上传发票图片
2. 系统自动识别和提取
3. 生成 Excel 报销单
4. 财务审核
5. 打款报销

全程自动化，效率提升 10 倍！
```

---

## 五、环境搭建与部署

### 5.1 使用 uv 快速安装

```bash
# 安装 uv
pip install uv

# 克隆项目
git clone https://github.com/AIwork4me/smart-receipt-assistant.git
cd smart-receipt-assistant

# 安装依赖（自动创建虚拟环境）
uv sync

# 配置 API Key
cp .env.example .env
# 编辑 .env，填入 PaddleOCR Access Token
```

### 5.2 获取 API Key

1. 访问 [PaddleOCR 官网](https://www.paddleocr.com)
2. 点击左上角 **API** 按钮
3. 选择 **PaddleOCR-VL-1.5**
4. 复制 **TOKEN** 和 **API_URL**
5. 填入 `.env` 文件

```bash
# .env
PADDLEOCR_ACCESS_TOKEN=your_token_here
PADDLEOCR_API_URL=your_api_url_here
```

### 5.3 启动服务

```bash
# CLI 方式
uv run python -m src.main recognize invoice.jpg

# Web 方式
uv run python -m src.main web
```

---

## 六、踩坑经验：LangChain 兼容性问题

### 6.1 问题现象

使用 `langchain-paddleocr` 时，遇到以下错误：

```
ModuleNotFoundError: No module named 'langchain.docstore'
ModuleNotFoundError: No module named 'langchain.text_splitter'
```

### 6.2 问题原因

`langchain-paddleocr` 依赖的 `paddlex` 包使用了 **LangChain 0.x** 的导入路径：

```python
# paddlex/inference/pipelines/components/retriever/base.py
from langchain.docstore.document import Document      # 旧版路径
from langchain.text_splitter import RecursiveCharacterTextSplitter  # 旧版路径
```

而 LangChain **1.0** 已经将这些路径移到独立包：

```
LangChain 0.x (旧版)              LangChain 1.x (新版)
─────────────────────────────────────────────────────────
langchain.docstore.document  →   langchain_core.documents
langchain.text_splitter      →   langchain_text_splitters
```

### 6.3 解决方案：Monkey Patch 兼容层

创建一个兼容层，在导入 `langchain-paddleocr` 之前设置：

```python
# src/langchain_compat.py
import sys
from types import ModuleType

def setup_langchain_compat():
    """设置 LangChain 兼容层"""
    import langchain_core.documents
    import langchain_text_splitters

    # 创建 langchain.docstore.document 兼容模块
    if 'langchain.docstore.document' not in sys.modules:
        document_module = ModuleType('langchain.docstore.document')
        document_module.Document = langchain_core.documents.Document
        sys.modules['langchain.docstore.document'] = document_module

    # 创建 langchain.text_splitter 兼容模块
    if 'langchain.text_splitter' not in sys.modules:
        text_splitter_module = ModuleType('langchain.text_splitter')
        for attr in dir(langchain_text_splitters):
            if not attr.startswith('_'):
                setattr(text_splitter_module, attr,
                        getattr(langchain_text_splitters, attr))
        sys.modules['langchain.text_splitter'] = text_splitter_module
```

**使用方式：**

```python
# 必须在导入 langchain_paddleocr 之前调用
from src.langchain_compat import setup_langchain_compat
setup_langchain_compat()

from langchain_paddleocr import PaddleOCRVLLoader  # 现在可以正常导入
```

这是 Python 社区处理依赖兼容性问题的标准做法。

---

## 七、总结与展望

### 项目总结

本文介绍了如何使用 **LangChain + langchain-paddleocr + ERINE** 打造智能票据报销助手：

| 组件 | 作用 |
|------|------|
| **LangChain** | 编排层，组织 OCR → 提取 → 分类 → 验证的工作流 |
| **langchain-paddleocr** | OCR 层，识别票据文字和印章 |
| **ERINE** | 语义层，理解 OCR 文本，提取结构化字段 |

**核心价值：**
- 降低人工成本：100 张发票从半天 → 10 分钟
- 辅助发票验真：印章识别 + 字段校验
- 简化报销流程：批量处理 + Excel 导出

### 开源地址

- **GitHub**：https://github.com/AIwork4me/smart-receipt-assistant
- **在线体验**：https://modelscope.cn/studios/Devkit/reciept-agent

欢迎 Star 和 PR！

### 后续优化方向

1. **接入税务局 API** 实现真正的发票验真
2. **支持更多票据类型**：航空行程单、定额发票、过路费发票
3. **添加报销单自动生成**功能
4. **部署为服务**，接入企业 OA 系统

---

**参考资料：**

- [PaddleOCR 官方文档](https://github.com/PaddlePaddle/PaddleOCR)
- [langchain-paddleocr 集成](https://github.com/PaddlePaddle/PaddleOCR/tree/main/langchain-paddleocr)
- [LangChain 官方文档](https://python.langchain.com/)
- [百度 AIStudio](https://aistudio.baidu.com/)
- [国家税务总局发票查验平台](https://inv-veri.chinatax.gov.cn)
