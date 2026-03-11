"""印章提取工具

从 PaddleOCR-VL API 原始响应中提取印章信息。
"""
from typing import List, Dict, Any


def extract_seals_from_response(raw_response: dict) -> List[Dict[str, Any]]:
    """从 PaddleOCR API 原始响应中提取印章信息

    Args:
        raw_response: PaddleOCRVLLoader 返回的 paddleocr_vl_raw_response

    Returns:
        印章信息列表，每个元素包含:
        - name: 印章图片名称
        - url: 印章图片 URL
        - page: 所在页码
        - type: 印章类型（发票专用章、财务专用章等）
    """
    seals = []

    # 处理可能的响应结构
    result = raw_response.get("result", raw_response)
    layout_results = result.get("layoutParsingResults", [])

    for i, res in enumerate(layout_results):
        # 获取 markdown 文本用于分析印章类型
        markdown = res.get("markdown", {})
        full_text = markdown.get("text", "")

        # 方法1: 从 outputImages 中提取
        output_images = res.get("outputImages", {})
        for img_name, img_url in output_images.items():
            if "seal" in img_name.lower():
                seals.append({
                    "name": img_name,
                    "url": img_url,
                    "page": i,
                    "type": classify_seal(img_name, full_text)
                })

        # 方法2: 从 markdown.images 中提取
        images = markdown.get("images", {})
        for img_name, img_url in images.items():
            if "seal" in img_name.lower():
                seals.append({
                    "name": img_name,
                    "url": img_url,
                    "page": i,
                    "type": classify_seal(img_name, full_text)
                })

    return seals


def classify_seal(name: str, surrounding_text: str = "") -> str:
    """根据名称和周围文本判断印章类型

    Args:
        name: 印章图片名称
        surrounding_text: 印章周围的 OCR 文本

    Returns:
        印章类型字符串
    """
    name_lower = name.lower()

    # 发票专用章
    if "invoice" in name_lower or "发票专用章" in surrounding_text or "发票章" in surrounding_text:
        return "发票专用章"

    # 财务专用章
    if "finance" in name_lower or "财务专用章" in surrounding_text or "财务章" in surrounding_text:
        return "财务专用章"

    # 公章
    if "official" in name_lower or "公章" in surrounding_text:
        return "公章"

    # 发票监制章（预印在发票上）
    if "监制章" in surrounding_text or "监督章" in surrounding_text:
        return "发票监制章"

    # 合同章
    if "合同" in surrounding_text and "章" in surrounding_text:
        return "合同章"

    return "其他印章"
