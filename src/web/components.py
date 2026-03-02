"""UI 组件"""
import gradio as gr
from typing import Optional, Tuple
from PIL import Image
import io
import requests
from pathlib import Path


# 支持的文件格式
SUPPORTED_FILE_TYPES = [".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"]

# 样本发票路径
SAMPLES_DIR = Path(__file__).parent.parent.parent / "examples" / "sample_invoices"

# 样本发票信息
SAMPLE_INVOICES = [
    {
        "file": "dinner.pdf",
        "name": "餐饮发票",
        "type": "增值税发票",
        "description": "餐饮服务增值税发票"
    },
    {
        "file": "didi.pdf",
        "name": "滴滴出行",
        "type": "增值税发票",
        "description": "滴滴出行电子发票"
    },
    {
        "file": "train.pdf",
        "name": "火车票",
        "type": "火车票",
        "description": "铁路电子客票"
    },
    {
        "file": "invoice1.png",
        "name": "增值税发票",
        "type": "增值税发票",
        "description": "增值税普通发票（含印章）"
    },
    {
        "file": "invoice2.png",
        "name": "航空发票",
        "type": "其他",
        "description": "航空服务发票"
    }
]


def create_upload_component() -> gr.Column:
    """创建上传组件

    Returns:
        Gradio Column 组件
    """
    with gr.Column() as col:
        gr.Markdown("### 上传票据文件")
        gr.Markdown("支持 PDF 和图片格式（增值税发票、火车票、出租车票等）")

        file_input = gr.File(
            label="票据文件",
            file_types=SUPPORTED_FILE_TYPES,
            type="filepath"
        )

        with gr.Row():
            enable_seal = gr.Checkbox(
                label="启用印章识别",
                value=True,
                info="识别发票上的公章、财务章等"
            )

        submit_btn = gr.Button(
            "识别票据",
            variant="primary",
            size="lg"
        )

    return col, file_input, enable_seal, submit_btn


def create_sample_component() -> Tuple[gr.Column, list]:
    """创建样本发票组件

    Returns:
        (Column 组件, 样本按钮列表)
    """
    with gr.Column() as col:
        gr.Markdown("### 📁 样本发票")
        gr.Markdown("点击下方按钮，快速体验识别效果")

        sample_buttons = []

        # 第一行：3个按钮
        with gr.Row():
            for sample in SAMPLE_INVOICES[:3]:
                btn = gr.Button(
                    f"📄 {sample['name']}",
                    variant="secondary",
                    size="sm"
                )
                sample_buttons.append((btn, sample))

        # 第二行：2个按钮
        with gr.Row():
            for sample in SAMPLE_INVOICES[3:]:
                btn = gr.Button(
                    f"📄 {sample['name']}",
                    variant="secondary",
                    size="sm"
                )
                sample_buttons.append((btn, sample))

        # 显示样本信息
        sample_info = gr.Textbox(
            label="样本说明",
            value="点击上方按钮选择样本发票",
            interactive=False,
            lines=2
        )

    return col, sample_buttons, sample_info


def create_result_component() -> gr.Column:
    """创建结果展示组件

    Returns:
        Gradio Column 组件
    """
    with gr.Column() as col:
        gr.Markdown("### 识别结果")

        with gr.Tabs():
            with gr.TabItem("结构化信息"):
                result_json = gr.JSON(
                    label="提取的字段"
                )

            with gr.TabItem("原始文本"):
                result_text = gr.Textbox(
                    label="OCR 识别文本",
                    lines=10,
                    max_lines=20
                )

            with gr.TabItem("印章信息"):
                seal_gallery = gr.Gallery(
                    label="识别到的印章",
                    columns=3,
                    height=200
                )
                seal_info = gr.Textbox(
                    label="印章分析",
                    lines=3
                )

        with gr.Row():
            validation_status = gr.Textbox(
                label="验证状态",
                interactive=False
            )

        with gr.Row():
            export_json_btn = gr.Button("导出 JSON")
            export_excel_btn = gr.Button("导出 Excel")

        export_file = gr.File(
            label="下载文件",
            visible=False
        )

    return col, result_json, result_text, seal_gallery, seal_info, validation_status


def create_batch_component() -> gr.Column:
    """创建批量处理组件

    Returns:
        Gradio Column 组件
    """
    with gr.Column() as col:
        gr.Markdown("### 批量处理")

        file_input = gr.File(
            label="上传多个票据文件",
            file_count="multiple",
            file_types=SUPPORTED_FILE_TYPES
        )

        batch_btn = gr.Button(
            "批量识别",
            variant="primary"
        )

        batch_results = gr.Dataframe(
            label="识别结果",
            headers=[
                "文件名", "票据类型", "日期", "金额",
                "销售方", "印章数量", "状态"
            ],
            datatype=["str"] * 7
        )

        batch_export_btn = gr.Button("导出全部结果")
        batch_file = gr.File(label="下载", visible=False)

    return col, file_input, batch_btn, batch_results, batch_export_btn, batch_file


def format_seal_info(seals: list, analysis: Optional[dict]) -> Tuple[list, str]:
    """格式化印章信息用于展示

    Args:
        seals: 印章列表
        analysis: 印章分析结果

    Returns:
        (印章图片列表, 印章分析文本)
    """
    images = []
    for seal in seals:
        try:
            # 下载印章图片
            response = requests.get(seal["url"], timeout=10)
            img = Image.open(io.BytesIO(response.content))
            images.append((img, seal["type"]))
        except Exception:
            continue

    if analysis:
        info_text = f"""印章数量：{analysis.get('count', 0)}
印章类型：{', '.join(analysis.get('types', []))}
真伪提示：{analysis.get('authenticity_hint', '')}"""
    else:
        info_text = "未检测到印章"

    return images, info_text


def format_validation_result(validation: dict) -> str:
    """格式化验证结果

    Args:
        validation: 验证结果字典

    Returns:
        格式化的文本
    """
    if validation.get("is_valid"):
        status = "验证通过"
        color = "green"
    else:
        status = "验证失败"
        color = "red"

    issues = validation.get("issues", [])
    warnings = validation.get("warnings", [])

    result = f"**{status}**\n\n"

    if issues:
        result += "**问题：**\n"
        for issue in issues:
            result += f"- {issue}\n"

    if warnings:
        result += "\n**警告：**\n"
        for warning in warnings:
            result += f"- {warning}\n"

    return result


def get_sample_path(sample_file: str) -> str:
    """获取样本文件路径

    Args:
        sample_file: 样本文件名

    Returns:
        样本文件完整路径
    """
    return str(SAMPLES_DIR / sample_file)
