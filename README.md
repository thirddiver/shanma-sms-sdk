# Codex SMS Python SDK

[![CI](https://github.com/thirddiver/shanma-sms-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/thirddiver/shanma-sms-sdk/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

Official Python SDK for **Codex SMS Verification Service**. A robust, lightweight, and developer-friendly client designed for receiving automated SMS verification codes across 100+ global regions.

---

## Key Features

- **Zero Heavy Dependencies**: Pure Python standard library implementation (`urllib` and `json`); zero third-party runtime bloat.
- **Pythonic Context Manager**: Safe `with client.activation(...)` pattern that automatically cancels orders and preserves credits if verification times out.
- **Service Alias Normalization**: Transparently handles friendly aliases (`chatgpt`, `dr`, `go`, `gmail`, `tg`, `wa`) to canonical platform services.
- **Smart SMS Polling**: Configurable timeouts and polling intervals with optional real-time callback hooks (`on_poll`).
- **Resilient Error Hierarchy**: Typed exceptions (`AuthenticationError`, `InsufficientBalanceError`, `NumberUnavailableError`, `UpstreamCarrierError`, `TimeoutError`).
- **Fully Typed**: 100% Python typing annotations with dataclass return types (`OrderResult`, `SmsResult`).

---

## Installation

```bash
pip install git+https://github.com/thirddiver/shanma-sms-sdk.git
```

---

## Quickstart

### 1. Initialize Client

```python
from shanma import CodexSmsClient  # or ShanmaClient

client = CodexSmsClient(api_key="YOUR_API_TOKEN")
```

### 2. Context Manager Pattern (Recommended)

The context manager automatically cancels the order and refunds your credits if an SMS is not received before timeout:

```python
from shanma import CodexSmsClient, InsufficientBalanceError, ShanmaError

client = CodexSmsClient(api_key="YOUR_API_TOKEN")

try:
    # Service aliases like 'chatgpt' automatically resolve to canonical services
    with client.activation(service="chatgpt", country="usa") as act:
        print(f"Activation ID: {act.order.activation_id}")
        print(f"Assigned Number: {act.order.phone_number}")

        # Wait for verification code with optional callback
        sms = act.wait_for_sms(timeout=180, interval=5)
        if sms:
            print(f"Code received: {sms.code}")
            print(f"Full message: {sms.full_text}")
        else:
            print("Timeout reached; order safely auto-cancelled.")

except InsufficientBalanceError:
    print("Account balance is insufficient. Please top up.")
except ShanmaError as e:
    print(f"SMS operation failed: {e}")
```

### 3. Traditional Manual Workflow

```python
# 1. Order a virtual number
order = client.order_number(service="openai", country="usa")
print(f"Ordered: {order.phone_number}")

# 2. Poll for verification code
sms = client.wait_for_sms(order.activation_id, timeout=120)

if sms:
    print(f"Verification code: {sms.code}")
else:
    # Explicitly cancel to release number and trigger refund
    client.cancel_order(order.activation_id)
```

---

## Running Tests

Run the test suite directly with standard `unittest`:

```bash
python -m unittest discover tests
```

---

## Documentation & Community

- Technical Guides & API Reference: [https://guide.shanma.store/](https://guide.shanma.store/)
- Web Platform: [https://shanma.store/](https://shanma.store/)

---

## License

This project is licensed under the [MIT License](LICENSE).
