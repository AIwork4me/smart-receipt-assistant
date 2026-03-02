<div align="center">

# 🧾 智能票据报销助手

**基于 PaddleOCR-VL-1.5 + LangChain + ERINE 的票据识别与信息提取系统**

支持印章识别，辅助验证发票真伪

[![ModelScope](https://img.shields.io/badge/在线体验-ModelScope创空间-blue?style=for-the-badge)](https://modelscope.cn/studios/Devkit/reciept-agent)
[![GitHub](https://img.shields.io/badge/GitHub-开源代码-black?style=for-the-badge&logo=github)](https://github.com/AIwork4me/smart-receipt-assistant)

[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-VL--1.5-0052cc?style=flat-square)](https://github.com/PaddlePaddle/PaddleOCR)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-1C3C3C?style=flat-square)](https://python.langchain.com/)
[![ERINE](https://img.shields.io/badge/ERINE-4.5-e3504b?style=flat-square)](https://aistudio.baidu.com/)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-f97316?style=flat-square)](https://gradio.app/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## ✨ 核心亮点

<table>
<tr>
<td width="50%">

### 🔴 印章识别

PaddleOCR-VL-1.5 独有功能，自动识别：
- 发票专用章
- 财务专用章
- 公章
- 发票监制章

辅助验证发票真伪

</td>
<td width="50%">

### 🤖 智能提取

ERINE 大模型驱动：
- 自动识别票据类型
- 结构化字段提取 (JSON)
- 智能报销分类
- 金额/日期自动校验

</td>
</tr>
</table>

---

## 🎯 功能演示

<div align="center">

| 票据识别 | 印章识别 |
|:---:|:---:|
| 自动识别发票类型、提取关键字段 | 检测印章位置、识别印章类型 |
| 支持 PDF / JPG / PNG 格式 | 辅助判断发票真伪 |

</div>

**支持的票据类型：**

- ✅ 增值税专用发票
- ✅ 增值税普通发票
- ✅ 火车票
- ✅ 出租车票
- ✅ 其他票据（自动识别）

---

## 🚀 快速开始

### 在线体验

访问 [ModelScope 创空间](https://modelscope.cn/studios/Devkit/reciept-agent)，无需安装：

1. 点击 **样本发票** 按钮，一键体验识别效果
2. 或上传自己的发票文件（支持 PDF/JPG/PNG）

### 本地部署

```bash
# 克隆项目
git clone https://github.com/AIwork4me/smart-receipt-assistant.git
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
2. 注册/登录账号，获取 Access Token
3. 填入 `.env` 文件的 `AISTUDIO_API_KEY`

> 💡 **提示**：PaddleOCR 和 ERINE 共用同一个 AIStudio Access Token，一次配置即可使用全部功能。

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Gradio Web 界面                         │
│         单张识别  │  样本发票  │  批量处理                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangChain 编排层                          │
│         OCR 识别链  →  信息提取链  →  分类验证链             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      能力层                                  │
│     PaddleOCR-VL-1.5 (OCR)     │     ERINE (语义理解)        │
└─────────────────────────────────────────────────────────────┘
```

**技术选型：**

| 组件 | 说明 |
|------|------|
| [PaddleOCR-VL-1.5](https://github.com/PaddlePaddle/PaddleOCR) | 百度飞桨 OCR，支持印章识别 |
| [LangChain](https://python.langchain.com/) | LLM 应用开发框架，链式工作流编排 |
| [ERINE](https://aistudio.baidu.com/) | 百度文心一言，中文语义理解 |
| [Gradio](https://gradio.app/) | Python Web 界面框架 |

---

## 📁 项目结构

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
└── docs/                  # 文档
```

---

## 📖 印章识别说明

| 印章类型 | 说明 | 验真价值 |
|---------|------|---------|
| 发票专用章 | 企业盖在发票上的章 | ⭐⭐⭐ 高 - 有此章更可信 |
| 财务专用章 | 企业财务部门印章 | ⭐⭐ 中 - 辅助判断 |
| 公章 | 企业公章 | ⭐⭐ 中 - 辅助判断 |
| 发票监制章 | 发票上预印的官方章 | ⭐ 低 - 所有发票都有 |

> ⚠️ **注意**：印章识别仅作为辅助验真手段，正式报销建议通过 [国家税务总局查验平台](https://inv-veri.chinatax.gov.cn) 核实。

---

## 📄 许可证

[MIT License](LICENSE)

---

## 🙏 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 百度飞桨 OCR 开源项目
- [LangChain](https://python.langchain.com/) - LLM 应用开发框架
- [百度 AIStudio](https://aistudio.baidu.com/) - AI 开发平台

---

<div align="center">

**[⬆ 返回顶部](#-智能票据报销助手)**

Made with ❤️ by [AIwork4me](https://github.com/AIwork4me)

</div>
