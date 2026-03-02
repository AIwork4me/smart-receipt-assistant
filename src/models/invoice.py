"""发票数据模型"""
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class InvoiceType(str, Enum):
    """发票类型"""
    VAT_SPECIAL = "增值税专用发票"
    VAT_NORMAL = "增值税普通发票"
    ELECTRONIC = "电子发票"


class VATInvoice(BaseModel):
    """增值税发票数据模型"""
    invoice_type: InvoiceType = Field(..., description="发票类型")
    invoice_code: str = Field(..., description="发票代码")
    invoice_number: str = Field(..., description="发票号码")
    date: str = Field(..., description="开票日期")
    buyer_name: str = Field(..., description="购买方名称")
    buyer_tax_id: str = Field(..., description="购买方纳税人识别号")
    buyer_address: Optional[str] = Field(None, description="购买方地址电话")
    buyer_bank: Optional[str] = Field(None, description="购买方开户行及账号")
    seller_name: str = Field(..., description="销售方名称")
    seller_tax_id: str = Field(..., description="销售方纳税人识别号")
    seller_address: Optional[str] = Field(None, description="销售方地址电话")
    seller_bank: Optional[str] = Field(None, description="销售方开户行及账号")
    items: List[dict] = Field(default_factory=list, description="货物或应税劳务列表")
    amount: str = Field(..., description="合计金额")
    tax: str = Field(..., description="合计税额")
    total: str = Field(..., description="价税合计（大写）")
    total_lowercase: str = Field(..., description="价税合计（小写）")
    remarks: Optional[str] = Field(None, description="备注")
    payee: Optional[str] = Field(None, description="收款人")
    reviewer: Optional[str] = Field(None, description="复核人")
    drawer: Optional[str] = Field(None, description="开票人")

    class Config:
        use_enum_values = True


class TrainTicket(BaseModel):
    """火车票数据模型"""
    train_number: str = Field(..., description="车次")
    departure_station: str = Field(..., description="出发站")
    arrival_station: str = Field(..., description="到达站")
    departure_time: str = Field(..., description="出发时间")
    seat_type: str = Field(..., description="座位类型")
    seat_number: Optional[str] = Field(None, description="座位号")
    price: str = Field(..., description="票价")
    passenger_name: str = Field(..., description="乘车人姓名")
    ticket_number: str = Field(..., description="票号")
    date: str = Field(..., description="乘车日期")

    class Config:
        use_enum_values = True

    def to_receipt_dict(self) -> dict:
        """转换为通用票据字典"""
        return {
            "receipt_type": "火车票",
            "invoice_number": self.ticket_number,
            "date": self.date,
            "total": self.price,
            "buyer_name": self.passenger_name,
            "train_number": self.train_number,
            "departure_station": self.departure_station,
            "arrival_station": self.arrival_station,
            "seat_type": self.seat_type
        }
