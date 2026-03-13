"""配置管理模块

Token 获取方式：
访问 PaddleOCR 官方网站：https://www.paddleocr.com
完成注册后，在模型服务页面点击"API"按钮，可获得 TOKEN 和 API_URL

注意：ERINE 的 Token 与 PaddleOCR 一致，无需额外获取！
"""
import os
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()


def get_api_token() -> SecretStr:
    """获取 PaddleOCR Access Token

    此 Token 同时用于 PaddleOCR 和 ERINE 大模型。
    优先使用 PADDLEOCR_ACCESS_TOKEN，向后兼容 AISTUDIO_API_KEY。

    Returns:
        SecretStr: Access Token

    Raises:
        ValueError: 未设置任何有效的环境变量
    """
    token = os.getenv("PADDLEOCR_ACCESS_TOKEN") or os.getenv("AISTUDIO_API_KEY")
    if not token:
        raise ValueError(
            "请设置 PADDLEOCR_ACCESS_TOKEN 环境变量\n"
            "获取方式：\n"
            "1. 访问 PaddleOCR 官方网站：https://www.paddleocr.com\n"
            "2. 完成注册\n"
            "3. 在模型服务页面点击「API」按钮\n"
            "4. 获得 PaddleOCR-VL-1.5 的 TOKEN 和 API_URL\n"
            "\n"
            "提示：ERINE 的 Token 与 PaddleOCR 一致，无需额外获取"
        )
    return SecretStr(token)


# PaddleOCR API URL（从环境变量读取）
PADDLEOCR_API_URL = os.getenv(
    "PADDLEOCR_API_URL",
    "https://q6mbb0r0t8m9q4pf.aistudio-app.com/layout-parsing"
)

# ERINE 配置 - 使用与 PaddleOCR 相同的 Token
ERINE_BASE_URL = os.getenv(
    "ERINE_BASE_URL",
    "https://aistudio.baidu.com/llm/lmapi/v3"
)
ERINE_MODEL = "ernie-4.5-turbo-128k-preview"


def get_api_key() -> str:
    """获取 API Key（向后兼容）

    Returns:
        str: API Key 字符串
    """
    token = get_api_token()
    return token.get_secret_value()


# 别名，保持向后兼容
get_paddleocr_token = get_api_token
