"""票据数据模型"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date
from enum import Enum


class ReceiptType(str, Enum):
    """票据类型枚举"""
    VAT_SPECIAL = "增值税专用发票"
    VAT_NORMAL = "增值税普通发票"
    TRAIN_TICKET = "火车票"
    TAXI_TICKET = "出租车票"
    HOTEL_INVOICE = "住宿发票"
    OTHER = "其他"


class ReimbursementCategory(str, Enum):
    """报销类别枚举"""
    OFFICE = "办公费用"
    TRANSPORT = "交通费"
    ACCOMMODATION = "住宿费"
    DINING = "餐饮费"
    OTHER = "其他"


class SealInfo(BaseModel):
    """印章信息"""
    name: str = Field(..., description="印章名称")
    url: str = Field(..., description="印章图片URL")
    seal_type: str = Field(..., description="印章类型")
    page: int = Field(default=0, description="所在页码")


class ReceiptInfo(BaseModel):
    """票据基础信息"""
    receipt_type: str = Field(..., description="票据类型")
    invoice_code: Optional[str] = Field(None, description="发票代码")
    invoice_number: Optional[str] = Field(None, description="发票号码")
    date: Optional[str] = Field(None, description="开票日期")
    amount: Optional[str] = Field(None, description="金额（不含税）")
    tax: Optional[str] = Field(None, description="税额")
    total: Optional[str] = Field(None, description="价税合计")
    buyer_name: Optional[str] = Field(None, description="购买方名称")
    buyer_tax_id: Optional[str] = Field(None, description="购买方税号")
    seller_name: Optional[str] = Field(None, description="销售方名称")
    seller_tax_id: Optional[str] = Field(None, description="销售方税号")
    seals: List[SealInfo] = Field(default_factory=list, description="印章信息")
    seal_analysis: Optional[dict] = Field(None, description="印章分析")
    reimbursement_category: Optional[str] = Field(None, description="报销类别")
    validation_result: Optional[dict] = Field(None, description="验证结果")
    file_path: Optional[str] = Field(None, description="原始文件路径")

    class Config:
        use_enum_values = True

    def to_dict(self) -> dict:
        """转换为字典"""
        return self.model_dump()

    def to_excel_row(self) -> list:
        """转换为 Excel 行数据"""
        return [
            self.receipt_type,
            self.invoice_code or "",
            self.invoice_number or "",
            self.date or "",
            self.buyer_name or "",
            self.seller_name or "",
            self.amount or "",
            self.tax or "",
            self.total or "",
            self.reimbursement_category or "",
            len(self.seals) if self.seals else 0,
            self.seal_analysis.get("authenticity_hint", "") if self.seal_analysis else ""
        ]
