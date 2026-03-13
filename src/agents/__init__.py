"""LangChain Agents for Receipt Processing

This module provides LangChain Agent implementations that can intelligently
orchestrate receipt processing tools (OCR, extraction, classification).

Example:
    >>> from src.agents import create_receipt_agent
    >>> agent = create_receipt_agent(api_key="your-api-key")
    >>> result = agent.invoke({
    ...     "input": "Process this invoice: invoice.jpg"
    ... })
"""

from .receipt_agent import (
    create_receipt_agent,
    ReceiptAgentExecutor,
    RECEIPT_AGENT_PROMPT,
)

__all__ = [
    "create_receipt_agent",
    "ReceiptAgentExecutor",
    "RECEIPT_AGENT_PROMPT",
]
