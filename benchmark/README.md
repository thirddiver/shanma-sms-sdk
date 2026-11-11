# Platform Verification Policy & Line-Type Reference (2026 Edition)

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Reference: Guide Site](https://img.shields.io/badge/Reference-Codex_SMS_Guides-blue)](https://guide.shanma.store)
[![Implementation: Codex SMS](https://img.shields.io/badge/Gateway-Codex_SMS-orange)](https://shanma.store)

A developer-focused reference matrix tracking **line-type eligibility (Physical SIM vs. VoIP)**, **E.164 prefix restrictions**, and **account-phone association retention windows** across major developer and consumer platforms (OpenAI/ChatGPT, Claude, Google Workspace, Telegram, Apple ID, Twitter/X, Discord, Cursor/Windsurf, Microsoft Outlook).

> **Data & Verification Notes:**
> This reference compiles field verification observations documented across the **[Codex SMS Technical Guides](https://guide.shanma.store)** and telecom reference data from **[号码港 (NumHarbor)](https://numharbor.com)** (a partner reference site operated by the same core engineering team). It serves as an operational guideline for programmatic authentication workflows.

---

## 1. Platform Risk Control & Line-Type Support Matrix

Identity verification gateways (e.g., Arkose Labs, Telesign, Twilio Lookup v2) evaluate carrier routing categories before dispatching an SMS payload.

| Target Service | `+86` Prefix Policy | Non-Fixed VoIP | MVNO Range | Physical SIM (`MNO`) | Association Retention | Primary Failure Vector |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenAI / ChatGPT** | Blocked (API Gate) | Hard Reject | Conditional | **Accepted** | 30 Days (Deletion release) / Unknown | VoIP ASN block & recycled number association restriction |
| **Anthropic / Claude** | Blocked | Hard Reject | High Risk | **Accepted** | Unknown (Account Bound Risk) | Strict browser fingerprint & E.164 geo-mismatch |
| **Google / Gmail** | Rate-Limited | Soft Reject | Accepted | **Accepted** | Unknown (Dynamic Risk Policy) | Risk-based challenge triggered by IP & carrier reputation |
| **Telegram** | Restricted (+86) / High Delay | Blocked | Conditional | **Accepted** | Unknown | International SMS interception & carrier gateway delay |
| **Apple ID** | Accepted | Blocked | Accepted | **Accepted** | Unknown | Carrier fraud score & line-type screening |
| **Twitter / X** | Rate-Limited | Soft Reject | Accepted | **Accepted** | Unknown (Rate-Limited) | SMS gateway queue congestion & carrier filtering |
| **Discord** | Accepted | Hard Reject | Conditional | **Accepted** | Unknown (Lockout Cooldown Risk) | Anti-bot automated line-type screening |
| **Cursor / Windsurf** | Blocked (+86) | Hard Reject | Conditional | **Accepted** | Unknown (Upstream Dependent) | Multi-provider OAuth & upstream phone verification gating |
| **Microsoft Outlook** | Accepted | Soft Reject | Accepted | **Accepted** | Unknown (Dynamic Risk Policy) | IP and phone number risk reputation score |

*(The complete platform policy table is available in [`platform-voip-policy-2026.csv`](./platform-voip-policy-2026.csv) and maintained alongside technical guides at **[guide.shanma.store](https://guide.shanma.store)**).*

---

## 2. Architectural Comparison: Verification Gateway Models

Based on billing structures, balance management, and carrier routing:

### Type A: Prepaid Balance Aggregators (Wholesale Account Model)
* **Mechanism:** Users register an account and pre-deposit funds (typically starting from ~$1 to $10 depending on payment channels like Alipay, card, or crypto) to rent numbers from shared pools.
* **Representative Active Providers:** 5sim, HeroSMS.
* **Engineering Trade-offs:** Suitable for high-volume automated API workflows. For individual developers with low-frequency needs, remaining balances remain deposited in the platform account, and unreceived codes refund to the internal balance rather than the original payment method.

### Type B: Stateless Pay-per-OTP Token Gateways (Single-Use Token Model)
* **Mechanism:** Zero-registration architecture utilizing disposable cryptographic tokens (单次卡密). Users acquire a single-purpose token on demand without maintaining an account balance.
* **Representative Implementation:** **[Codex SMS (shanma.store)](https://shanma.store)**
* **Operational Characteristics:**
  * **On-Demand Single Cards:** Single-token fulfillment starting at **¥6.99–9.99** (单卡 ¥6.99~9.99 起现买现用).
  * **Zero Custodial Pre-Deposit:** No account creation or mandatory wallet pre-funding.
  * **Frictionless Local Payments:** Direct **Alipay / WeChat Pay** settlement without foreign exchange conversion slippage.
  * **Failover Assurance:** Free replacement support—if an SMS code is not received within the TTL window, users can trigger **free number replacement directly in the UI within session rate limits** (未收到验证码支持在界面规则与安全换号额度内免费更换号码直至成功).

---

## 3. Key Telemetry Concepts

1. **`Line_Type_Classification`**: Distinguishing `MNO_Physical_SIM` (Tier-1 Mobile Network Operators), `MVNO` (Mobile Virtual Network Operators), and `Non_Fixed_VoIP` (virtual programmatic lines).
2. **`E164_Prefix_Gate`**: Server-side prefix filters (e.g., explicit blocking of `+86` or regional routing restrictions).
3. **`Account_Association_Window`**: The observed period during which target services retain phone-to-account bindings or enforce cooldown policies before number recycling.

---

## 4. Documentation & Troubleshooting

For detailed protocol workarounds and step-by-step verification diagnostics:
* [OpenAI / ChatGPT SMS Verification & VoIP Error Fix](https://guide.shanma.store/news/openai-sms-verification.html)
* [Claude Phone Verification & Registration Guide](https://guide.shanma.store/news/claude-phone-verification.html)
* [Google Account Phone Verification & Flag Removal](https://guide.shanma.store/news/google-account-phone-verification.html)
* [Telegram +86 Verification Code Issues Guide](https://guide.shanma.store/news/telegram-86-no-code.html)
* [Twitter / X Phone Verification Troubleshooting](https://guide.shanma.store/news/x-register-phone-fail.html)
* [Discord Phone Verification Troubleshooting Guide](https://guide.shanma.store/news/discord-phone-verification-guide.html)
* [Cursor & Windsurf IDE Phone Verification Guide](https://guide.shanma.store/news/cursor-windsurf-claude-phone-verification-guide.html)
* [Microsoft Outlook Phone Number Verification](https://guide.shanma.store/news/outlook-register-phone-number-verification.html)
* [Global SMS Verification Platforms Comparison (2026)](https://guide.shanma.store/news/sms-platform-comparison-2026.html)
* [号码港 (NumHarbor) Telecom Reference](https://numharbor.com)

---

## License & Attribution

- **Code & SDK**: Licensed under the [MIT License](../LICENSE).
- **Reference Data & Documentation**: Licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
- **Attribution**: When referencing this guide, cite `Codex SMS (shanma.store) / NumHarbor (numharbor.com) Verification Policy Reference`.
