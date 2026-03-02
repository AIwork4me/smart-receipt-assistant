# 发票验真实现方案

## 一、当前实现：辅助验真

### 1. 印章识别

通过 PaddleOCR-VL-1.5 识别发票上的印章：

```python
# 印章类型判断
- 发票专用章：企业盖在发票上的章，验真重要依据
- 财务专用章：企业财务部门印章
- 公章：企业公章
- 发票监制章：发票上预印的官方监制章（不是企业盖的）
```

### 2. 字段校验

```python
# 金额计算校验
amount + tax == total  # 价税合计是否正确

# 日期合理性
date <= today  # 不是未来日期
date > 5_years_ago  # 不是过期太久

# 必填字段检查
invoice_code, invoice_number, date, buyer, seller
```

### 3. 局限性

当前方案只能**辅助判断**，无法确认发票真伪：
- 印章可以被伪造
- OCR 识别可能有误差
- 无法验证发票是否在税务系统登记

---

## 二、真正的发票验真：接入税务局 API

### 1. 国家税务总局查验平台

官方提供了发票查验接口，需要以下信息：

```python
# 必填参数
invoice_code = "1100221130"  # 发票代码
invoice_number = "12345678"   # 发票号码
invoice_date = "20190219"     # 开票日期 (YYYYMMDD)
check_code = "123456"         # 校验码后6位（增值税发票）
total_amount = "1060.00"      # 价税合计（部分发票需要）
```

### 2. 验真流程

```
┌─────────────────┐
│   发票图片      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OCR 识别       │
│  提取关键信息    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  税务局 API     │
│  发票查验       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  返回验证结果   │
│  • 发票是否存在 │
│  • 开票方信息   │
│  • 当前状态     │
└─────────────────┘
```

### 3. 实现代码示例

```python
import requests
import hashlib

class InvoiceVerifier:
    """发票真伪验证（接入税务局 API）"""

    def __init__(self, app_key: str, app_secret: str):
        """
        Args:
            app_key: 税务局开放平台应用 Key
            app_secret: 税务局开放平台应用 Secret
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.api_url = "https://inv-veri.chinatax.gov.cn/api/query"  # 示例

    def verify(self, invoice_info: dict) -> dict:
        """验证发票真伪

        Args:
            invoice_info: 发票信息字典

        Returns:
            验证结果
        """
        # 构建请求参数
        params = {
            "fpdm": invoice_info["invoice_code"],  # 发票代码
            "fphm": invoice_info["invoice_number"], # 发票号码
            "kprq": invoice_info["date"].replace("-", ""),  # 开票日期
            "kjje": invoice_info["total"],  # 价税合计
            "yzm": invoice_info.get("check_code", "")[-6:],  # 校验码后6位
        }

        # 生成签名
        sign = self._generate_sign(params)

        # 调用 API
        response = requests.post(
            self.api_url,
            json={**params, "sign": sign},
            headers={"AppKey": self.app_key}
        )

        return response.json()

    def _generate_sign(self, params: dict) -> str:
        """生成请求签名"""
        sorted_params = sorted(params.items())
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign_str += f"&appsecret={self.app_secret}"
        return hashlib.md5(sign_str.encode()).hexdigest().upper()
```

### 4. 验证结果示例

```json
{
    "code": "0000",
    "message": "查询成功",
    "data": {
        "exist": true,
        "invoiceCode": "1100221130",
        "invoiceNumber": "12345678",
        "invoiceDate": "2019-02-19",
        "sellerName": "某某科技有限公司",
        "sellerTaxId": "91110000XXXXXXXXXX",
        "buyerName": "某某公司",
        "buyerTaxId": "91110000YYYYYYYYYY",
        "totalAmount": "1060.00",
        "taxAmount": "60.00",
        "status": "有效",  // 有效/作废/红冲
        "invoiceType": "增值税普通发票"
    }
}
```

---

## 三、第三方验真服务

如果无法直接接入税务局 API，可以使用第三方服务：

| 服务商 | 特点 | 费用 |
|--------|------|------|
| 百度 AI 发票验真 | OCR + 验真一体 | 按次收费 |
| 阿里云发票验真 | 支持多种发票类型 | 按次收费 |
| 腾讯云发票验真 | 高并发支持 | 按次收费 |

### 百度 AI 示例

```python
from aip import AipOcr

# 百度 AI 配置
APP_ID = 'your_app_id'
API_KEY = 'your_api_key'
SECRET_KEY = 'your_secret_key'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

# 发票验真
result = client.vatInvoiceVerify(
    invoice_code="1100221130",
    invoice_number="12345678",
    invoice_date="20190219",
    check_code="123456"
)
```

---

## 四、推荐的完整验真流程

```python
def full_verify(file_path: str) -> dict:
    """完整验真流程"""

    # 1. OCR 识别
    ocr_result = ocr.recognize(file_path)
    extracted_info = llm.extract(ocr_result.text)

    # 2. 本地校验
    local_check = validate_receipt(extracted_info)

    # 3. 印章识别
    seals = ocr.extract_seals(ocr_result)

    # 4. 税务局验真（如果有必要信息）
    if has_required_fields(extracted_info):
        tax_check = tax_api.verify(extracted_info)
    else:
        tax_check = {"status": "skip", "reason": "缺少必要字段"}

    return {
        "ocr_info": extracted_info,
        "seals": seals,
        "local_validation": local_check,
        "tax_verification": tax_check,
        "final_result": determine_authenticity(
            local_check, seals, tax_check
        )
    }
```

---

## 五、当前项目扩展建议

要实现完整的发票验真，需要：

1. **申请税务局开放平台账号**
   - 地址：https://inv-veri.chinatax.gov.cn
   - 需要企业资质

2. **添加验真模块**

```python
# src/verification/tax_api.py
class TaxBureauAPI:
    """税务局发票查验 API"""
    pass
```

3. **更新验真链**

```python
# src/chains/verification_chain.py
class VerificationChain:
    """发票验真链"""

    def verify(self, invoice_info: dict) -> dict:
        # 本地校验
        local_result = self.local_verify(invoice_info)

        # 税务局验真
        if self.should_call_tax_api(invoice_info):
            tax_result = self.tax_api.verify(invoice_info)
        else:
            tax_result = {"skipped": True}

        return self.merge_results(local_result, tax_result)
```

---

## 六、总结

| 验真方式 | 准确性 | 成本 | 实现难度 |
|---------|-------|------|---------|
| 印章识别（当前） | 低 | 免费 | 低 |
| 字段校验（当前） | 中 | 免费 | 低 |
| 税务局 API | 高 | 免费额度 | 中 |
| 第三方服务 | 高 | 收费 | 低 |

**建议**：当前印章识别 + 字段校验作为第一道防线，有条件时接入税务局 API 实现真正的验真。
