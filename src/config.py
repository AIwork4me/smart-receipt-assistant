"""配置管理模块"""
import os
from dotenv import load_dotenv

load_dotenv()

# AIStudio API Key（统一用于 PaddleOCR 和 ERINE）
AISTUDIO_API_KEY = os.getenv("AISTUDIO_API_KEY")

# PaddleOCR-VL-1.5 配置
PADDLEOCR_API_URL = "https://q6mbb0r0t8m9q4pf.aistudio-app.com/layout-parsing"

# ERINE 配置
ERINE_BASE_URL = "https://aistudio.baidu.com/llm/lmapi/v3"
ERINE_MODEL = "ernie-4.5-turbo-128k-preview"

# 验证配置（延迟到实际使用时检查）
def get_api_key() -> str:
    """获取 API Key，如果未设置则抛出错误"""
    if not AISTUDIO_API_KEY:
        raise ValueError(
            "请设置 AISTUDIO_API_KEY 环境变量\n"
            "1. 复制 .env.example 为 .env\n"
            "2. 在 .env 中填入你的 AIStudio Access Token\n"
            "3. 获取 Token: https://aistudio.baidu.com/"
        )
    return AISTUDIO_API_KEY
