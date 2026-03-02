"""ERINE API 封装"""
import json
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from typing import Optional

# AIStudio ERINE 配置
ERINE_BASE_URL = "https://aistudio.baidu.com/llm/lmapi/v3"
ERINE_MODEL = "ernie-4.5-turbo-128k-preview"


class ERINEClient:
    """ERINE API 客户端 (AIStudio OpenAI 兼容)"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: AIStudio Access Token
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=ERINE_BASE_URL,
        )

    def chat(self, messages: list, stream: bool = False) -> str:
        """发送聊天请求

        Args:
            messages: 消息列表
            stream: 是否流式输出

        Returns:
            模型回复内容
        """
        response = self.client.chat.completions.create(
            model=ERINE_MODEL,
            messages=messages,
            stream=stream,
            temperature=0.8,
            top_p=0.8,
            max_completion_tokens=12000,
        )

        if stream:
            result = []
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    if hasattr(chunk.choices[0].delta, "content"):
                        result.append(chunk.choices[0].delta.content or "")
            return "".join(result)
        else:
            return response.choices[0].message.content


class ReceiptExtractionChain:
    """票据信息提取链

    使用 LangChain + ERINE 从 OCR 文本中提取结构化信息
    """

    EXTRACTION_PROMPT = """你是一个专业的票据信息提取助手。请从以下 OCR 识别文本中提取关键信息。

OCR 文本：
{ocr_text}

请提取以下字段（如果存在）：
- 票据类型：[增值税发票/火车票/出租车票/其他]
- 发票代码：
- 发票号码：
- 开票日期：
- 购买方名称：
- 购买方税号：
- 销售方名称：
- 销售方税号：
- 金额（不含税）：
- 税额：
- 价税合计：
- 印章信息：

要求：
1. 请以 JSON 格式返回结果，确保字段名使用英文
2. 日期格式统一为 YYYY-MM-DD
3. 金额保留两位小数
4. 如果某字段不存在，值设为 null
5. 只返回 JSON，不要其他说明文字

返回格式示例：
{{
    "receipt_type": "增值税发票",
    "invoice_code": "1234567890",
    "invoice_number": "12345678",
    "date": "2024-01-15",
    "buyer_name": "某某公司",
    "buyer_tax_id": "91110000XXXXXXXXXX",
    "seller_name": "某某商家",
    "seller_tax_id": "91110000YYYYYYYYYY",
    "amount": "1000.00",
    "tax": "60.00",
    "total": "1060.00",
    "seal_info": "发票专用章"
}}"""

    CLASSIFICATION_PROMPT = """请判断以下票据文本属于哪种类型。

OCR 文本：
{ocr_text}

请从以下类型中选择一个：
- 增值税专用发票
- 增值税普通发票
- 火车票
- 出租车票
- 住宿发票
- 其他

只返回类型名称，不要其他说明。"""

    VALIDATION_PROMPT = """请验证以下票据信息是否合理。

票据信息：
{receipt_info}

请检查：
1. 日期是否合理（不是未来日期，且在合理范围内）
2. 金额计算是否正确（金额 + 税额 = 价税合计）
3. 必填字段是否完整

请返回 JSON 格式：
{{
    "is_valid": true/false,
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"]
}}"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: AIStudio Access Token
        """
        # 使用 LangChain 的 ChatOpenAI 封装
        self.llm = ChatOpenAI(
            model=ERINE_MODEL,
            api_key=api_key,
            base_url=ERINE_BASE_URL,
            temperature=0.1,  # 低温度保证提取准确性
        )

        # 提取链
        self.extraction_prompt = PromptTemplate(
            template=self.EXTRACTION_PROMPT,
            input_variables=["ocr_text"]
        )
        self.extraction_chain = self.extraction_prompt | self.llm

        # 分类链
        self.classification_prompt = PromptTemplate(
            template=self.CLASSIFICATION_PROMPT,
            input_variables=["ocr_text"]
        )
        self.classification_chain = self.classification_prompt | self.llm

        # 验证链
        self.validation_prompt = PromptTemplate(
            template=self.VALIDATION_PROMPT,
            input_variables=["receipt_info"]
        )
        self.validation_chain = self.validation_prompt | self.llm

    def extract(self, ocr_text: str) -> dict:
        """从 OCR 文本中提取结构化信息

        Args:
            ocr_text: OCR 识别的文本

        Returns:
            结构化的票据信息字典
        """
        response = self.extraction_chain.invoke({"ocr_text": ocr_text})
        content = response.content

        # 尝试解析 JSON
        try:
            # 尝试提取 JSON 块
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            return json.loads(json_str)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始内容
            return {
                "raw_response": content,
                "parse_error": "无法解析为 JSON"
            }

    def classify(self, ocr_text: str) -> str:
        """对票据进行分类

        Args:
            ocr_text: OCR 识别的文本

        Returns:
            票据类型
        """
        response = self.classification_chain.invoke({"ocr_text": ocr_text})
        return response.content.strip()

    def validate(self, receipt_info: dict) -> dict:
        """验证票据信息

        Args:
            receipt_info: 票据信息字典

        Returns:
            验证结果
        """
        response = self.validation_chain.invoke({
            "receipt_info": json.dumps(receipt_info, ensure_ascii=False, indent=2)
        })
        content = response.content

        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            return json.loads(json_str)
        except json.JSONDecodeError:
            return {
                "is_valid": True,
                "raw_response": content
            }
