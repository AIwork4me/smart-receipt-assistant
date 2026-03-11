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
