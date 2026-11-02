# Codex SMS Python SDK

[![CI](https://github.com/thirddiver/shanma-sms-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/thirddiver/shanma-sms-sdk/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.3.1-green.svg)](https://github.com/thirddiver/shanma-sms-sdk)

The official, lightweight Python SDK for **Codex SMS** verification and overseas mobile number services ([shanma.store](https://shanma.store/)).

Built for developers, AI agent builders, and automation workflows needing programmatic, reliable overseas SMS verification codes across OpenAI / ChatGPT, Telegram, Google, WhatsApp, and more.

---

## Key Highlights

- **Zero Third-Party Dependencies**: Pure Python standard library implementation (`urllib`, `json`, `dataclasses`). Zero external runtime bloat.
- **CDK-as-Token Authentication**: No account registration or password required. Purchase single-use or multi-use CDKs instantly via Alipay at [shanma.store](https://shanma.store/) and pass the CDK directly as a Bearer Token.
- **Pythonic Context Manager**: Elegant `with client.activation(service=...) as act:` workflow with automated phone switching and polling.
- **Free Replacement Guarantee**: Seamlessly call `client.switch_phone()` or `act.switch()` if a number does not receive an SMS or is flagged by the target service — replacement numbers are free until code is received.
- **Service Alias Normalization**: Transparently maps aliases (`chatgpt`, `dr`, `go`, `gmail`, `tg`, `wa`) to canonical platform service codes.
- **Strict Typing & Typed Exceptions**: 100% typed with dataclasses (`OrderResult`, `SmsResult`) and specific error handling (`CodexSmsError`, `AuthenticationError`, `RateLimitError`, `CdkAlreadyUsedError`).

---

## Installation

Install directly via git:

```bash
pip install git+https://github.com/thirddiver/shanma-sms-sdk.git
```

Or install from local source:

```bash
git clone https://github.com/thirddiver/shanma-sms-sdk.git
cd shanma-sms-sdk
pip install .
```

---

## Quickstart

### 1. Recommended: Context Manager Pattern

The context manager automatically redeems the CDK and provides convenient helper methods for polling and switching numbers:

```python
from shanma import CodexSmsClient, CodexSmsError

# Initialize client using your purchased CDK
client = CodexSmsClient(cdkey="YOUR_CDK_SECRET_KEY")

with client.activation(service="chatgpt") as act:
    print(f"Allocated phone: {act.phone_number}")
    print(f"Activation ID: {act.activation_id}")
    
    # Poll for SMS code (default timeout: 180s, interval: 5s)
    sms = act.wait_for_sms(timeout=120)
    
    if sms:
        print(f"Verification code received: {sms.code}")
        print(f"Full SMS text: {sms.full_text}")
    else:
        print("Timeout without SMS. Requesting a free replacement number...")
        act.switch()
        print(f"New replacement phone: {act.phone_number}")
        sms = act.wait_for_sms(timeout=120)
        if sms:
            print(f"Code received on new number: {sms.code}")
```

---

### 2. Manual Step-by-Step Workflow

For fine-grained control across separate functions or microservices:

```python
from shanma import CodexSmsClient, CodexSmsError, AuthenticationError

client = CodexSmsClient(cdkey="YOUR_CDK_SECRET_KEY")

try:
    # 1. Redeem CDK and allocate number
    order = client.redeem(service="telegram")
    print(f"Phone: {order.phone_number} (Country: {order.country})")

    # 2. Poll for SMS verification code
    sms = client.wait_for_sms(timeout=120, interval=5)
    if sms:
        print(f"Received code: {sms.code}")
    else:
        # 3. If unreceived, switch to a fresh number
        new_order = client.switch_phone()
        print(f"Switched to: {new_order.phone_number}")

except AuthenticationError:
    print("Invalid or unpaid CDK. Please check your key at shanma.store.")
except CodexSmsError as e:
    print(f"Operation failed: {e}")
```

---

### 3. Batch Automation (Multiple CDKs)

Process multiple verifications sequentially or in thread pools:

```python
from shanma import CodexSmsClient, CodexSmsError

cdk_list = [
    "CDK-ABCD-1111",
    "CDK-EFGH-2222",
    "CDK-IJKL-3333",
]

for cdk in cdk_list:
    client = CodexSmsClient(cdkey=cdk)
    try:
        with client.activation(service="openai") as act:
            print(f"[{cdk}] Number: {act.phone_number}")
            sms = act.wait_for_sms(timeout=90)
            if sms:
                print(f"[{cdk}] Code: {sms.code}")
    except CodexSmsError as err:
        print(f"[{cdk}] Failed: {err}")
```

---

## Service Aliases

The SDK automatically normalizes convenient aliases to official service identifiers:

| Service / App | Supported Aliases | Canonical Identifier |
|---|---|---|
| **OpenAI / ChatGPT / Sora** | `chatgpt`, `dr`, `openai` | `openai` |
| **Telegram** | `tg`, `telegram` | `telegram` |
| **Google / Gmail** | `google`, `gmail`, `go` | `google` |
| **WhatsApp** | `wa`, `whatsapp` | `whatsapp` |
| **Microsoft / Outlook** | `mm`, `microsoft` | `microsoft` |
| **Discord** | `ds`, `discord` | `discord` |
| **Twitter / X** | `tw`, `x`, `twitter` | `twitter` |

---

## API Reference

### `CodexSmsClient`
- `CodexSmsClient(cdkey: str, base_url: str = "https://shanma.store", timeout: int = 30)`: Initialize client with CDK.
- `client.redeem(service: Optional[str] = None) -> OrderResult`: Redeem CDK to allocate an overseas number.
- `client.get_status() -> Dict[str, Any]`: Query status, remaining time, and allocated phone.
- `client.query_sms() -> Optional[SmsResult]`: Single check for incoming SMS payload.
- `client.wait_for_sms(timeout: int = 180, interval: int = 5, on_poll: Optional[Callable]) -> Optional[SmsResult]`: Poll until SMS received or timeout reached.
- `client.switch_phone() -> OrderResult`: Cancel unfulfilled number and allocate a replacement number.
- `client.resend_sms() -> Dict[str, Any]`: Trigger carrier resend.
- `client.activation(service: Optional[str] = None) -> ActivationContext`: Context manager helper.

---

## Error Hierarchy

All exceptions inherit from `CodexSmsError` (aliased to `ShanmaError` for backwards compatibility):

```text
CodexSmsError (alias ShanmaError)
 ├── AuthenticationError      (HTTP 401/403: Invalid or unpaid CDK)
 ├── RateLimitError          (HTTP 429: Request rate limit exceeded)
 ├── CdkAlreadyUsedError      (HTTP 410: CDK already redeemed or expired)
 ├── ActivationNotFoundError (HTTP 404: Resource or CDK not found)
 ├── TimeoutError            (Timed out waiting for SMS)
 └── UpstreamCarrierError    (Upstream carrier allocation issue)
```

---

## Running Tests

The test suite runs completely offline with standard Python `unittest`:

```bash
python -m unittest discover tests
```

---

## Links & Resources

- Official Service: [shanma.store](https://shanma.store/)
- Troubleshooting & Verification Guides: [guide.shanma.store](https://guide.shanma.store/)
- Issue Tracker: [GitHub Issues](https://github.com/thirddiver/shanma-sms-sdk/issues)

---

## License

This project is licensed under the [MIT License](LICENSE).
