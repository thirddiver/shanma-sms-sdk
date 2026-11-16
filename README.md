# Codex SMS Python SDK

[![CI](https://github.com/thirddiver/shanma-sms-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/thirddiver/shanma-sms-sdk/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.3.3-green.svg)](https://github.com/thirddiver/shanma-sms-sdk)

Official lightweight Python SDK for **Codex SMS** guest CDK SMS verification workflows ([shanma.store](https://shanma.store/)).

Built for developers and automation workflows interacting with single-use guest CDKs (`POST /api/guest/cdkeys/*`) with zero third-party runtime dependencies. (7-day rental/prolong cards `rent_7d` are operated via the web console and are outside the scope of this SDK.)

---

## Key Highlights

- **Zero Third-Party Dependencies**: Pure Python 3.10+ standard library (`urllib`, `json`, `dataclasses`) with PEP 561 `py.typed` support.
- **Zero-Registration CDK Authentication**: Purchase a single-use guest CDK at [shanma.store](https://shanma.store/) (live pricing, stock, and supported payment methods follow the public catalog at `https://shanma.store/api/cdkey/catalog` and checkout page) and pass it as a Bearer token. Target service and country routing are determined by the purchased CDK itself.
- **Context Manager Workflow**: Use `with client.activation() as act:` to redeem, poll with monotonic timing bounds, resend, and switch numbers.
- **Quota-Bounded Number Replacement**: If an SMS code is not received, call `client.switch_phone()` or `act.switch()` for free replacement within validity windows and the system limit of **up to 30 total acquired numbers per CDK** (contact support if the limit is reached). Abandoning a number that already received an SMS requires `confirm_abandon_sms=True` and is limited to **once per single-use CDK**.
- **Explicit Session & Carrier Error Mapping**: Translates HTTP `401/403`, `404` / `status="expired"`, `409`, `410`, `429`, `502`, and `503` into typed exceptions (`ConflictError`, `ActivationNotFoundError`, `UpstreamCarrierError`, `NumberUnavailableError`, `InsufficientBalanceError`).

---

## Installation

Install from PyPI (distribution `codex-sms`, once the PyPI release is published):

```bash
pip install codex-sms
```

Or install the tagged release directly via git:

```bash
pip install git+https://github.com/thirddiver/shanma-sms-sdk.git@v0.3.3
```

Or install from local source:

```bash
git clone https://github.com/thirddiver/shanma-sms-sdk.git
cd shanma-sms-sdk
pip install .
```

> Both `from codex_sms import CodexSmsClient` and legacy `from shanma import CodexSmsClient` are supported.

---

## Quickstart

### 1. Recommended: Context Manager Pattern

```python
from codex_sms import CodexSmsClient, ActivationNotFoundError, CodexSmsError

# Purchase a single-use CDK for your target service at https://shanma.store/
client = CodexSmsClient(cdkey="YOUR_CDK_SECRET_KEY")

try:
    with client.activation() as act:
        print(f"Allocated phone: {act.phone_number}")
        print(f"Activation ID: {act.activation_id}")

        # Returns SmsResult or None if timeout elapses without an SMS
        sms = act.wait_for_sms(timeout=120)
        if sms:
            print(f"Verification code received: {sms.code}")
            print(f"Full SMS text: {sms.full_text}")
        else:
            print("Timeout without SMS. Requesting replacement within CDK quota...")
            act.switch()
            print(f"Replacement phone: {act.phone_number}")
            sms = act.wait_for_sms(timeout=120)
            if sms:
                print(f"Code received on replacement number: {sms.code}")
except ActivationNotFoundError:
    print("CDK not found or activation session expired.")
except CodexSmsError as e:
    print(f"API operation failed: {e}")
```

---

### 2. Manual Step-by-Step Workflow

```python
from codex_sms import CodexSmsClient, CodexSmsError, AuthenticationError, ConflictError

client = CodexSmsClient(cdkey="YOUR_CDK_SECRET_KEY")

try:
    order = client.redeem()
    print(f"Phone: {order.phone_number} (Country: {order.country})")

    sms = client.wait_for_sms(timeout=120, interval=5)
    if sms:
        print(f"Received code: {sms.code}")
    else:
        new_order = client.switch_phone()
        print(f"Switched to: {new_order.phone_number}")

except AuthenticationError:
    print("Invalid or unpaid CDK. Verify your order at https://shanma.store.")
except ConflictError:
    # Raised if an SMS was already received on the current number;
    # pass switch_phone(confirm_abandon_sms=True) only if you intend to abandon it (1x limit).
    print("Replacement requires confirm_abandon_sms=True or another switch is in progress.")
except CodexSmsError as e:
    print(f"Operation failed: {e}")
```

---

## Service Aliases

`normalize_service()` maps common local labels to canonical service codes (note: `/api/guest/cdkeys/redeem` validates `{}` with `extra="forbid"`, so target service is always governed by the purchased CDK itself):

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
- `CodexSmsClient(cdkey: str, base_url: str = "https://shanma.store", timeout: int = 30)`: Initialize client with a guest CDK.
- `client.redeem(service: Optional[str] = None) -> OrderResult`: Redeem the CDK via `POST /api/guest/cdkeys/redeem` with `{}` (`service` is optional local metadata fallback).
- `client.get_status() -> Dict[str, Any]`: Query current activation state, remaining time, and allocated phone.
- `client.query_sms() -> Optional[SmsResult]`: Poll `POST /api/guest/cdkeys/sms`; returns `SmsResult` if received, `None` if waiting, or raises `ActivationNotFoundError` if `status == "expired"`.
- `client.wait_for_sms(timeout: int = 180, interval: int = 5, on_poll: Optional[Callable]) -> Optional[SmsResult]`: Poll with `time.monotonic()` up to `timeout` (interval clamped `>= 4s` to respect per-CDK rate limits); returns `None` when timeout elapses without raising `TimeoutError`.
- `client.switch_phone(confirm_abandon_sms: bool = False) -> OrderResult`: Switch to a replacement number within the 30-number per-CDK cap; pass `confirm_abandon_sms=True` only when abandoning a previously received SMS (allowed once per CDK).
- `client.resend_sms() -> Dict[str, Any]`: Request carrier resend (`POST /api/guest/cdkeys/resend`).
- `client.activation(service: Optional[str] = None) -> ActivationContext`: Context manager factory (`act.switch(confirm_abandon_sms=...)`).

---

## Error Hierarchy

All exceptions inherit from `CodexSmsError` (aliased as `ShanmaError` for code compatibility):

```text
CodexSmsError (alias ShanmaError)
 ├── AuthenticationError      (HTTP 401/403: Invalid or unpaid CDK)
 ├── ActivationNotFoundError  (HTTP 404 or status="expired": CDK/session unavailable)
 ├── ConflictError            (HTTP 409: Requires confirm_abandon_sms=True or switch in progress)
 ├── CdkAlreadyUsedError      (HTTP 410: CDK already used or expired)
 ├── RateLimitError           (HTTP 429: Per-IP, per-CDK, or 30-number limit exceeded)
 ├── UpstreamCarrierError     (HTTP 502: Upstream carrier gateway error)
 ├── NumberUnavailableError   (HTTP 503: No numbers currently available)
 ├── InsufficientBalanceError (HTTP 503: Upstream balance unavailable)
 └── TimeoutError             (Optional exception class; wait_for_sms returns None on timeout)
```

---

## Running Tests

The unit test suite runs completely offline using mocked HTTP responses:

```bash
python -m unittest discover -s tests -v
```

---

## Verification Guides & Historical Line-Type Notes

Core troubleshooting and verification boundary documentation is published at **[guide.shanma.store](https://guide.shanma.store/)**:

| Topic | Documentation |
|---|---|
| **OpenAI / ChatGPT / Sora** | [OpenAI SMS Verification & VoIP Troubleshooting](https://guide.shanma.store/news/openai-sms-verification.html) |
| **Anthropic / Claude** | [Claude Phone Verification Guide](https://guide.shanma.store/news/claude-phone-verification.html) |
| **Google / Gmail** | [Google Account Phone Verification Guide](https://guide.shanma.store/news/google-account-phone-verification.html) |
| **Platform Model Comparison** | [SMS Verification Platforms Comparison (2026)](https://guide.shanma.store/news/sms-platform-comparison-2026.html) |

### Reference Dataset & Architectural Comparison ([`benchmark/`](./benchmark/))

- **Historical Reference Table**: [`benchmark/platform-voip-policy-2026.csv`](./benchmark/platform-voip-policy-2026.csv) records team-maintained historical line-type observations (not official platform policies). Provenance: field observations compiled by the Codex SMS engineering team alongside the co-maintained historical dataset on **NumHarbor (numharbor.com, historical dataset N=1,784 observations as of 2026-11)**; past observations do not certify current delivery rates.

| Evaluation Dimension | Type A: Prepaid Balance Aggregators (5sim / HeroSMS) | Type B: Stateless Pay-per-OTP Gateways (Codex SMS) |
| :--- | :--- | :--- |
| **Line-Type Routing** | Shared wholesale pools with varying VoIP ratios | Overseas mobile carrier number ranges; actual country and operator follow live redemption allocation |
| **Account & Pricing** | Account registration with pre-funded wallet balance (minimums follow each platform's current rules) | Zero registration, single-use CDK fulfillment; current pricing, catalog, and payment methods follow [shanma.store](https://shanma.store/) checkout |
| **Failover & Limits** | Unreceived codes return to internal platform wallet balance | Free number replacement before code receipt within validity windows and the **30 total acquired numbers per CDK** limit (contact support if reached) |

*(Note: Receiving an SMS code confirms delivery on a temporary number only and does not guarantee third-party account approval or long-term retention.)*

---

## Links & Resources

- Official Service & Catalog: [shanma.store](https://shanma.store/)
- Verification Guides: [guide.shanma.store](https://guide.shanma.store/)
- Issue Tracker: [GitHub Issues](https://github.com/thirddiver/shanma-sms-sdk/issues)

---

## License

- **Code & SDK**: [MIT License](LICENSE)
- **Reference Data & Documentation**: [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
