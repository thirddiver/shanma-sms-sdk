# Codex SMS Python SDK (experimental)

[![CI](https://github.com/thirddiver/shanma-sms-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/thirddiver/shanma-sms-sdk/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

> **Status: experimental, not usable against the live service.**
> This client targets an HTTP API (`https://api.shanma.store`) that is **not publicly available**. None of the endpoints it calls are open today, so the client cannot place orders or receive codes. The tests run entirely against mocked responses.
>
> Codex SMS currently works without an account or API key: you buy a single-use redeem code on [shanma.store](https://shanma.store/) and redeem it on the website to receive one verification code. There is no programmatic access at the moment.
>
> 状态说明：本仓库是实验性客户端，所调用的 API 目前**未对外开放**，无法用于实际下单或收码。Codex SMS 现在的使用方式是在 shanma.store 购买单次兑换码、在网页上兑换，无需注册账号，也没有 API Key。

---

## What is here

A small Python client written against a draft API design, kept as a reference for a possible future developer API:

- Pure standard library (`urllib`, `json`), no third-party runtime dependencies.
- A context manager (`with client.activation(...)`) that cancels the order if no code arrives before the timeout.
- Service alias normalization (`chatgpt`, `dr`, `go`, `gmail`, `tg`, `wa`).
- Configurable SMS polling with an optional `on_poll` callback.
- Typed exceptions (`AuthenticationError`, `InsufficientBalanceError`, `NumberUnavailableError`, `UpstreamCarrierError`, `TimeoutError`) and dataclass results (`OrderResult`, `SmsResult`).

The account, balance and per-order concepts in this client reflect the draft API only; they do not describe how the current service is sold or billed.

---

## Draft usage (API not live)

The snippets below show the intended interface. They will fail with a connection error until a public API exists.

```python
from shanma import CodexSmsClient, ShanmaError

client = CodexSmsClient(api_key="YOUR_API_TOKEN")

try:
    with client.activation(service="chatgpt", country="usa") as act:
        print(act.order.phone_number)
        sms = act.wait_for_sms(timeout=180, interval=5)
        print(sms.code if sms else "No code before timeout; order cancelled.")
except ShanmaError as e:
    print(f"Request failed: {e}")
```

---

## Running tests

The test suite mocks every HTTP call and runs offline:

```bash
python -m unittest discover tests
```

---

## Links

- Guides on phone verification for OpenAI, Codex and other platforms: [guide.shanma.store](https://guide.shanma.store/)
- The service itself (single-use redeem codes): [shanma.store](https://shanma.store/)

---

## License

This project is licensed under the [MIT License](LICENSE).
