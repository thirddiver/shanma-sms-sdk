# Platform Verification Policy & Line-Type Reference (2026 Historical Notes)

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Reference: Guide Site](https://img.shields.io/badge/Reference-Codex_SMS_Guides-blue)](https://guide.shanma.store/)
[![Implementation: Codex SMS](https://img.shields.io/badge/Gateway-Codex_SMS-orange)](https://shanma.store/)

A team-maintained historical reference matrix summarizing observed **line-type screening behaviors**, **E.164 prefix restrictions**, and **account-phone association notes** across major developer and consumer platforms as of **2026-11**.

> **Provenance & Scope Disclosure:**
> This table reflects historical observations compiled by the **Codex SMS** engineering team (`guide.shanma.store`) alongside historical aggregate records co-maintained with **NumHarbor (numharbor.com)** (`N=1,784` total historical records, compiled through `2026-11`; original dataset did not distinguish paid vs. free acquisition sources). These entries are **not official platform policies** and do **not** guarantee future acceptance rates, live inventory, or account approval.

---

## 1. Observed Line-Type Support Matrix (Historical Reference)

Target services apply dynamic risk controls (E.164 prefix checks, line-type reputation, and client environment checks). Entries below summarize prior observations through `2026-11`:

| Target Service | `+86` Prefix Policy | Non-Fixed VoIP | MVNO Range | Physical SIM (`MNO`) | Association Retention | Primary Failure Vector | Observation Date |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenAI / ChatGPT** | Blocked (API Gate) | Hard Reject | Conditional | Observed Accepted | ~30 Days (Deletion release) / Unknown | VoIP line-type screening & recycled number binding limits | 2026-11 |
| **Anthropic / Claude** | Blocked | Hard Reject | High Risk | Observed Accepted | Unknown (Account Bound) | Browser fingerprint & E.164 region mismatch | 2026-11 |
| **Google / Gmail** | Rate-Limited | Soft Reject | Observed Conditional | Observed Accepted | Unknown (Dynamic Policy) | Risk challenge triggered by IP & carrier reputation | 2026-11 |
| **Telegram** | Restricted (+86) / High Delay | Blocked | Conditional | Observed Accepted | Unknown | International SMS filtering & gateway delay | 2026-11 |
| **Twitter / X** | Rate-Limited | Soft Reject | Observed Conditional | Observed Accepted | Unknown | Carrier SMS filtering & rate limiting | 2026-11 |
| **Discord** | Accepted | Hard Reject | Conditional | Observed Accepted | Unknown | Automated anti-bot line-type screening | 2026-11 |
| **Cursor / Windsurf** | Blocked (+86) | Hard Reject | Conditional | Observed Accepted | Unknown | Upstream OAuth & phone verification gating | 2026-11 |
| **Microsoft Outlook** | Accepted | Soft Reject | Observed Conditional | Observed Accepted | Unknown | IP and phone number risk reputation score | 2026-11 |

*(Raw CSV: [`platform-voip-policy-2026.csv`](./platform-voip-policy-2026.csv); field troubleshooting notes: **[guide.shanma.store](https://guide.shanma.store/)**.)*

---

## 2. Architectural Comparison: Verification Gateway Models

### Type A: Prepaid Balance Aggregators (Account Wallet Model)
* **Mechanism:** Users register an account and pre-deposit funds into an internal balance to rent numbers from shared pools. Minimum deposit thresholds and supported payment channels depend on each provider's current terms.
* **Representative Providers:** 5sim, HeroSMS.
* **Operational Trade-offs:** Well-suited for recurring API users who maintain standing wallet balances; cancelled or unreceived activations typically credit back to the internal account balance rather than the external payment source.

### Type B: Stateless Pay-per-OTP Token Gateways (Single-Use CDK Model)
* **Mechanism:** Zero-registration workflow using single-use cryptographic tokens (单次卡密) tied to a selected service at purchase time.
* **Representative Implementation:** **[Codex SMS (shanma.store)](https://shanma.store/)**
* **Operational Characteristics:**
  * **Live Catalog & Checkout Rules:** Available services, live pricing, stock, and payment rails follow the real-time public catalog (`https://shanma.store/api/cdkey/catalog`) and checkout page at the time of purchase.
  * **Zero Wallet Pre-Funding:** Single-purpose CDK purchase without mandatory account registration or pre-deposited wallet balance.
  * **Carrier Range Allocation:** Uses overseas mobile carrier number ranges; actual country and operator depend on live pool allocation at redemption time rather than manual pre-selection.
  * **Quota-Bounded Replacement:** If no SMS arrives within the waiting window, users can replace numbers free of charge up to the **30 total acquired numbers per CDK** safety ceiling (including initial and pool-prefetched numbers); contact customer support if the ceiling is reached. Abandoning a number after receiving an SMS is restricted to once per single-use CDK.
  * **Boundary:** Temporary number SMS delivery does not certify platform eligibility, long-term account survival, or recurring re-verification access.

---

## 3. Documentation & Attribution

- Full troubleshooting guides: **[guide.shanma.store](https://guide.shanma.store/)**
- **Code & SDK License**: [MIT License](../LICENSE)
- **Reference Data & Documentation License**: [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
- **Citation**: `Codex SMS (shanma.store) / NumHarbor (numharbor.com) Historical Verification Policy Reference (as of 2026-11)`
