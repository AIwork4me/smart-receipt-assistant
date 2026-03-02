# ModelScope 创空间上传步骤

## 一、准备工作

### 1. 确保 API Key 配置正确

在 ModelScope 创空间中，需要通过**环境变量**配置 API Key。

**方式一：在创空间设置中配置（推荐）**

在 ModelScope 创空间设置页面添加环境变量：
- 变量名：`AISTUDIO_API_KEY`
- 变量值：你的 AIStudio Access Token

**方式二：创建 .env 文件**

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 2. 获取 AIStudio API Key

1. 访问 https://aistudio.baidu.com/
2. 登录账号
3. 点击右上角头像 → 个人中心 → Access Token
4. 复制 Token

---

## 二、上传到 ModelScope

### 方式一：通过 Git 上传（推荐）

```bash
# 1. 初始化 Git 仓库
cd smart-receipt-assistant
git init

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "Initial commit: 智能票据报销助手"

# 4. 在 ModelScope 创建创空间后，添加远程仓库
git remote add origin https://www.modelscope.cn/studios/YOUR_USERNAME/smart-receipt-assistant.git

# 5. 推送到 ModelScope
git push -u origin main
```

### 方式二：通过网页上传

1. 登录 https://www.modelscope.cn/
2. 点击「创建创空间」
3. 选择 Gradio SDK
4. 在文件管理页面上传以下文件：

**必传文件：**
```
app.py                 # 入口文件
requirements.txt       # 依赖
README.md              # 项目说明
.env.example           # 环境变量模板
src/                   # 源代码目录（整个目录）
examples/              # 示例发票（整个目录）
```

---

## 三、配置创空间

### 1. 设置环境变量

在创空间设置页面：
- 变量名：`AISTUDIO_API_KEY`
- 变量值：你的 AIStudio Access Token

### 2. 选择 SDK 版本

- SDK：Gradio
- 版本：4.44.0 或更高

### 3. 设置硬件资源

- CPU：2 核以上
- 内存：4GB 以上
- 无需 GPU

---

## 四、验证部署

### 1. 检查日志

在创空间日志中查看：
```
✓ Gradio 应用创建成功
✓ 应用标题: 智能票据报销助手
Running on local URL:  http://0.0.0.0:7860
```

### 2. 测试功能

- 点击样本发票按钮，验证识别功能
- 上传自己的发票，验证 OCR 和提取功能

---

## 五、常见问题

### Q1: 启动失败，提示 API Key 未配置

**解决：** 在创空间设置中添加环境变量 `AISTUDIO_API_KEY`

### Q2: OCR 识别失败

**解决：** 检查 API Key 是否有效，是否为 AIStudio Access Token

### Q3: 依赖安装失败

**解决：** 检查 `requirements.txt` 是否完整上传

---

## 六、项目文件清单

```
smart-receipt-assistant/
├── app.py                  # 创空间入口 ✓
├── requirements.txt        # 依赖列表 ✓
├── README.md               # 项目说明（含 metadata）✓
├── .env.example            # 环境变量模板 ✓
├── .gitignore              # Git 忽略配置 ✓
├── pyproject.toml          # 项目配置 ✓
├── src/                    # 源代码 ✓
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── chains/
│   ├── llm/
│   ├── models/
│   ├── ocr/
│   ├── utils/
│   └── web/
├── examples/               # 示例发票 ✓
│   └── sample_invoices/
│       ├── dinner.pdf
│       ├── didi.pdf
│       ├── train.pdf
│       ├── invoice1.png
│       └── invoice2.png
├── tests/                  # 测试文件（可选）
└── docs/                   # 文档（可选）
```

---

## 七、联系与反馈

如有问题，请在 ModelScope 项目页面提交 Issue。
