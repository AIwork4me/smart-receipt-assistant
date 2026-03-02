"""数据模型模块"""
from .receipt import ReceiptInfo, SealInfo
from .invoice import VATInvoice, TrainTicket

__all__ = ["ReceiptInfo", "SealInfo", "VATInvoice", "TrainTicket"]
