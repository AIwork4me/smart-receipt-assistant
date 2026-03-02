"""Web 界面模块"""
from .app import create_app, launch_app
from .components import create_upload_component, create_result_component

__all__ = [
    "create_app",
    "launch_app",
    "create_upload_component",
    "create_result_component"
]
