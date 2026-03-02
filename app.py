"""
智能票据报销助手 - ModelScope 创空间入口
基于 PaddleOCR-VL-1.5 + LangChain + ERINE
"""
import os

# 设置环境变量（ModelScope 创空间会自动注入）
if not os.getenv("AISTUDIO_API_KEY"):
    # 尝试从 ModelScope 环境变量获取
    api_key = os.getenv("MODELSCOPE_API_KEY") or os.getenv("API_KEY")
    if api_key:
        os.environ["AISTUDIO_API_KEY"] = api_key

from src.web import launch_app

if __name__ == "__main__":
    launch_app(server_name="0.0.0.0", server_port=7860)
