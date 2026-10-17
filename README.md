# Codex SMS Python SDK

[![CI](https://github.com/thirddiver/shanma-sms-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/thirddiver/shanma-sms-sdk/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-guide.shanma.store-green.svg)](https://guide.shanma.store/)

Official Python SDK for **Codex SMS Verification Service**. A robust, lightweight, and developer-friendly client designed for receiving automated SMS verification codes across 100+ global regions.

---

## Key Features

- **Lightweight Standard Library**: Zero mandatory third-party runtime dependencies; utilizes native `urllib` and `json`.
- **Codex SMS & ShanMa Ecosystem**: Full support for virtual phone numbers, OpenAI / Claude / Telegram / WhatsApp activation workflows.
- **Smart SMS Polling**: Automatic polling mechanism with configurable interval, exponential backoff, and strict timeout boundaries.
- **Resilient Error Handling**: Clear exception hierarchy (`AuthenticationError`, `InsufficientBalanceError`, `UpstreamCarrierError`, `TimeoutError`).
- **Automatic Refund Safety**: Unfulfilled activations are automatically cancelled, preventing wasted credits.
- **Fully Typed**: Complete Python `typing` hints and dataclass returns (`OrderResult`, `SmsResult`).

---

## Installation

```bash
pip install git+https://github.com/thirddiver/shanma-sms-sdk.git
```

*(PyPI package `shanma-sms-sdk` coming soon in v0.2 release)*

---

## Quickstart

### 1. Initialize the Client

```python
from shanma import CodexSmsClient  # or ShanmaClient

# Initialize with your API token
client = CodexSmsClient(api_key="YOUR_API_TOKEN")
```

### 2. Check Service & Price Availability

```python
# List available services and current stock status
services = client.get_available_services(country="usa")
for svc in services[:5]:
    print(f"Service: {svc['name']} | Cost: {svc['cost']} | Count: {svc['count']}")
```

### 3. Request a Number & Wait for SMS

```python
from shanma import AuthenticationError, InsufficientBalanceError, ShanmaError

try:
    # Order a temporary virtual phone number (e.g. OpenAI verification)
    order = client.order_number(service="openai", country="usa")
    print(f"Activation ID: {order.activation_id}")
    print(f"Assigned Phone Number: {order.phone_number}")

    # Poll for incoming SMS code (default timeout: 300 seconds)
    sms = client.wait_for_sms(order.activation_id, timeout=180, interval=5)

    if sms and sms.code:
        print(f"Verification Code Received: {sms.code}")
        print(f"Full Message: {sms.full_text}")
    else:
        # If no SMS arrives within the timeout window, safely cancel to refund
        client.cancel_order(order.activation_id)
        print("No SMS received within timeout. Order safely cancelled and refunded.")

except InsufficientBalanceError:
    print("Insufficient account balance. Please top up your credits.")
except ShanmaError as e:
    print(f"Operation failed: {e}")
```

---

## Technical Documentation & Guides

For complete architecture details, API endpoints reference, and carrier routing guides:

- 📖 **Official Developer Guide**: [https://guide.shanma.store/](https://guide.shanma.store/)
- 🌐 **Codex SMS Platform**: [https://shanma.store/](https://shanma.store/)
- 📑 **Best Practices**:
  - [OpenAI Registration Phone Risk Assessment](https://guide.shanma.store/)
  - [Global Carrier Line-Type (VoIP vs Real SIM) Routing](https://guide.shanma.store/)

---

## Running Tests

```bash
python -m unittest discover tests
```

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for bug fixes, documentation improvements, or additional client features.

## License

This project is licensed under the [MIT License](LICENSE).
