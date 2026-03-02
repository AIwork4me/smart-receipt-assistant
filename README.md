---
title: 智能票据报销助手
emoji: 🧾
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
short_description: 基于 PaddleOCR-VL-1.5 + LangChain + ERINE 的票据识别系统，支持印章识别
---

# 智能票据报销助手

<p align="center">
  <a href="https://modelscope.cn/studios/Devkit/reciept-agent">
    <img src="https://img.shields.io/badge/在线体验-ModelScope创空间-blue" alt="ModelScope">
  </a>
  <img src="https://img.shields.io/badge/PaddleOCR-VL--1.5-blue" alt="PaddleOCR">
  <img src="https://img.shields.io/badge/LangChain-0.1+-green" alt="LangChain">
  <img src="https://img.shields.io/badge/ERINE-4.5-orange" alt="ERINE">
  <img src="https://img.shields.io/badge/Gradio-4.0+-red" alt="Gradio">
</p>

基于 **PaddleOCR-VL-1.5 + LangChain + ERINE** 的票据识别与信息提取系统，支持印章识别，辅助验证发票真伪。

**[🚀 立即体验](https://modelscope.cn/studios/Devkit/reciept-agent)** - 无需安装，在线使用

## 特色功能

| 功能 | 说明 |
|------|------|
| 🧾 票据识别 | 支持 PDF 和图片格式，自动识别发票类型 |
| 🔴 印章识别 | PaddleOCR-VL-1.5 独有功能，识别发票专用章、财务章、公章 |
| 🤖 智能提取 | 使用 ERINE 大模型提取结构化字段（JSON 格式）|
| 📂 自动分类 | 按报销类别自动分类（交通费、住宿费、办公费用等）|
| ✅ 验证校验 | 金额计算校验、日期合理性检查、印章完整性检查 |
| 🎯 样本体验 | 内置 5 张样本发票，一键体验识别效果 |

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Gradio Web 界面                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  单张识别   │  │  样本发票   │  │  批量处理   │         │
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

## 使用方式

### 在线体验

**[ModelScope 创空间](https://modelscope.cn/studios/Devkit/reciept-agent)** 已部署本应用，可直接体验：

1. 点击左侧 **样本发票** 按钮，快速体验识别效果
2. 或上传自己的发票文件（支持 PDF/JPG/PNG）

### 本地部署

```bash
# 克隆项目
git clone https://www.modelscope.cn/studios/your-username/smart-receipt-assistant.git
cd smart-receipt-assistant

# 安装依赖
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env，填入 AIStudio Access Token

# 启动服务
python app.py
```

### 获取 API Key

1. 访问 [百度 AIStudio](https://aistudio.baidu.com/)
2. 注册/登录账号
3. 获取 Access Token
4. 填入 `.env` 文件的 `AISTUDIO_API_KEY`

> **注意**：PaddleOCR 和 ERINE 共用同一个 AIStudio Access Token

## 支持的票据类型

| 票据类型 | 报销类别 | 提取字段 |
|---------|---------|---------|
| 增值税专用发票 | 办公费用 | 代码、号码、日期、金额、税额、购买方、销售方 |
| 增值税普通发票 | 办公费用 | 同上 |
| 火车票 | 交通费 | 车次、出发站、到达站、座位、票价 |
| 出租车票 | 交通费 | 日期、金额 |
| 其他票据 | 其他 | 自动识别并提取 |

## 印章识别

PaddleOCR-VL-1.5 独有的印章识别功能：

| 印章类型 | 说明 | 验真价值 |
|---------|------|---------|
| 发票专用章 | 企业盖在发票上的章 | 高 - 有此章更可信 |
| 财务专用章 | 企业财务部门印章 | 中 - 辅助判断 |
| 公章 | 企业公章 | 中 - 辅助判断 |
| 发票监制章 | 发票上预印的官方章 | 低 - 所有发票都有 |

## 项目结构

```
smart-receipt-assistant/
├── app.py                  # 创空间入口
├── requirements.txt        # 依赖列表
├── src/
│   ├── main.py            # CLI 入口
│   ├── config.py          # 配置管理
│   ├── chains/            # LangChain 链
│   ├── ocr/               # OCR 模块
│   ├── llm/               # LLM 模块
│   ├── models/            # 数据模型
│   ├── web/               # Web 界面
│   └── utils/             # 工具函数
├── examples/              # 示例发票
│   └── sample_invoices/
└── docs/                  # 文档
```

## 许可证

MIT License

## 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [LangChain](https://python.langchain.com/)
- [百度 AIStudio](https://aistudio.baidu.com/)
