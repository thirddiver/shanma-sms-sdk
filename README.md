# ShanMa SMS SDK (Python)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-guide.shanma.store-green.svg)](https://guide.shanma.store/)

Official Python SDK for **ShanMa SMS Verification Service**. A robust, lightweight, and developer-friendly client designed for receiving automated SMS verification codes across 100+ global regions.

---

## Key Features

- **Asynchronous & Synchronous Support**: Built with lightweight standard protocols; easily integrates into async worker tasks (Celery, FastAPI, asyncio) or synchronous automation scripts.
- **Smart SMS Polling**: Automatic polling mechanism with configurable interval, exponential backoff, and strict timeout boundaries.
- **Resilient Error Handling**: Clear exception hierarchy for network timeouts, balance shortage, and upstream carrier delays.
- **Automatic Refund Safety**: Unfulfilled activations are automatically cancelled, preventing wasted credits.
- **Developer First**: Fully typed with Python `typing` hints and complete IDE autocompletion support.

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
from shanma import ShanmaClient

# Initialize with your API access token
client = ShanmaClient(api_key="YOUR_SHANMA_API_KEY")
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
# Order a temporary virtual phone number (e.g. OpenAI verification)
order = client.order_number(service="openai", country="usa")
print(f"Activation ID: {order.activation_id}")
print(f"Assigned Phone Number: {order.phone_number}")

# Poll for incoming SMS code (default timeout: 300 seconds)
sms_result = client.wait_for_sms(order.activation_id, timeout=300, interval=5)

if sms_result and sms_result.code:
    print(f"Verification Code Received: {sms_result.code}")
    print(f"Full Message: {sms_result.full_text}")
else:
    # If no SMS arrives within the timeout window, safely cancel to refund
    client.cancel_order(order.activation_id)
    print("No SMS received within timeout. Order safely cancelled and refunded.")
```

---

## Technical Documentation & Guides

For complete architecture details, API endpoints reference, and carrier routing guides:

- 📖 **Official Developer Guide**: [https://guide.shanma.store/](https://guide.shanma.store/)
- 🌐 **Platform Console**: [https://shanma.store/](https://shanma.store/)
- 📑 **Best Practices**:
  - [OpenAI Registration Phone Risk Assessment](https://guide.shanma.store/)
  - [Global Carrier Line-Type (VoIP vs Real SIM) Routing](https://guide.shanma.store/)

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for bug fixes, documentation improvements, or additional client features.

## License

This project is licensed under the [MIT License](LICENSE).
