"""校验函数"""
from typing import Optional
from datetime import datetime
import re


def validate_amount(amount: Optional[str], tax: Optional[str], total: Optional[str]) -> dict:
    """验证金额计算是否正确

    Args:
        amount: 金额（不含税）
        tax: 税额
        total: 价税合计

    Returns:
        验证结果
    """
    issues = []

    if not all([amount, tax, total]):
        return {
            "is_valid": True,
            "issues": ["金额信息不完整，无法验证"]
        }

    try:
        amount_val = float(amount.replace(",", "").replace("￥", ""))
        tax_val = float(tax.replace(",", "").replace("￥", ""))
        total_val = float(total.replace(",", "").replace("￥", ""))

        calculated_total = amount_val + tax_val

        if abs(calculated_total - total_val) > 0.01:
            issues.append(
                f"金额计算有误：{amount_val} + {tax_val} = {calculated_total}，"
                f"但发票显示 {total_val}"
            )
    except (ValueError, AttributeError) as e:
        issues.append(f"金额格式错误：{str(e)}")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues
    }


def validate_date(date_str: Optional[str]) -> dict:
    """验证日期是否合理

    Args:
        date_str: 日期字符串

    Returns:
        验证结果
    """
    issues = []

    if not date_str:
        return {
            "is_valid": True,
            "issues": ["日期为空"]
        }

    # 尝试多种日期格式
    date_formats = [
        "%Y-%m-%d",
        "%Y年%m月%d日",
        "%Y/%m/%d",
        "%Y%m%d",
        "%d %b %Y",
    ]

    parsed_date = None
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue

    if not parsed_date:
        issues.append(f"无法解析日期格式：{date_str}")
        return {
            "is_valid": False,
            "issues": issues
        }

    # 检查是否为未来日期
    today = datetime.now()
    if parsed_date > today:
        issues.append("日期为未来日期，请核实")

    # 检查是否过于久远（超过5年）
    days_diff = (today - parsed_date).days
    if days_diff > 365 * 5:
        issues.append(f"日期距今已超过5年（{days_diff // 365}年），请确认是否有效")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "parsed_date": parsed_date.strftime("%Y-%m-%d")
    }


def validate_receipt(receipt_info: dict) -> dict:
    """验证票据信息完整性

    Args:
        receipt_info: 票据信息字典

    Returns:
        验证结果
    """
    issues = []
    warnings = []

    # 必填字段检查
    required_fields = {
        "receipt_type": "票据类型",
        "date": "开票日期",
    }

    for field, name in required_fields.items():
        if not receipt_info.get(field):
            issues.append(f"缺少必填字段：{name}")

    # 发票特有字段检查
    receipt_type = receipt_info.get("receipt_type", "")
    if "发票" in receipt_type:
        invoice_fields = {
            "invoice_code": "发票代码",
            "invoice_number": "发票号码",
            "buyer_name": "购买方名称",
            "seller_name": "销售方名称",
        }
        for field, name in invoice_fields.items():
            if not receipt_info.get(field):
                warnings.append(f"建议补充字段：{name}")

    # 金额验证
    amount_result = validate_amount(
        receipt_info.get("amount"),
        receipt_info.get("tax"),
        receipt_info.get("total")
    )
    issues.extend(amount_result.get("issues", []))

    # 日期验证
    date_result = validate_date(receipt_info.get("date"))
    issues.extend(date_result.get("issues", []))

    # 印章检查
    seals = receipt_info.get("seals", [])
    if not seals and "发票" in receipt_type:
        warnings.append("未检测到印章，建议人工核实发票真伪")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }


def validate_tax_id(tax_id: Optional[str]) -> dict:
    """验证纳税人识别号格式

    Args:
        tax_id: 纳税人识别号

    Returns:
        验证结果
    """
    if not tax_id:
        return {
            "is_valid": True,
            "issues": ["纳税人识别号为空"]
        }

    # 中国纳税人识别号通常是 15、17、18 或 20 位
    tax_id = tax_id.strip()

    if not re.match(r"^[0-9A-Z]+$", tax_id):
        return {
            "is_valid": False,
            "issues": ["纳税人识别号格式错误，只能包含数字和大写字母"]
        }

    if len(tax_id) not in [15, 17, 18, 20]:
        return {
            "is_valid": False,
            "issues": [f"纳税人识别号长度异常：{len(tax_id)}位（通常为15/17/18/20位）"]
        }

    return {
        "is_valid": True,
        "issues": []
    }
