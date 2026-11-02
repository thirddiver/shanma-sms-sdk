"""
Codex SMS Python SDK - Quickstart Example (v0.3.1)
Demonstrates redeeming an overseas number, receiving SMS, and handling free replacements.
"""

import sys
import os

# Allow running directly from local repo source
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shanma import (
    CodexSmsClient,
    CodexSmsError,
    AuthenticationError,
    CdkAlreadyUsedError,
    RateLimitError,
)


def run_live_workflow(cdk: str) -> None:
    """Executes a real workflow against the live Codex SMS service using a valid CDK."""
    print(f"Connecting to Codex SMS with CDK: {cdk[:8]}***")
    client = CodexSmsClient(cdkey=cdk)

    try:
        # Context Manager Workflow
        with client.activation(service="chatgpt") as act:
            print(f"Allocated overseas phone number: {act.phone_number}")
            print(f"Activation ID: {act.activation_id}")
            print("Waiting for SMS verification code (polling every 5s)...")

            sms = act.wait_for_sms(timeout=120)
            if sms:
                print(f"[SUCCESS] Verification code received: {sms.code}")
                print(f"Full message: {sms.full_text}")
            else:
                print("[TIMEOUT] Did not receive code. Requesting free replacement phone...")
                new_order = act.switch()
                print(f"New replacement phone: {new_order.phone_number}")
                sms = act.wait_for_sms(timeout=120)
                if sms:
                    print(f"[SUCCESS] Received code on replacement phone: {sms.code}")

    except AuthenticationError:
        print("[ERROR] CDK authentication failed. Please verify your CDK at https://shanma.store")
    except CdkAlreadyUsedError:
        print("[ERROR] This CDK has already been redeemed and completed.")
    except RateLimitError:
        print("[ERROR] Polling rate limit exceeded. Please wait a moment.")
    except CodexSmsError as e:
        print(f"[ERROR] API operation failed: {e}")


def show_demo_walkthrough() -> None:
    """Displays code guidance when no environment variable is provided."""
    print("=" * 60)
    print("Codex SMS Python SDK (v0.3.1) - Quickstart Walkthrough")
    print("=" * 60)
    print("\n[NOTE] No CODEX_SMS_CDK environment variable detected.")
    print("To execute against the live service, set CODEX_SMS_CDK or pass your key directly:")
    print("  $env:CODEX_SMS_CDK = \"YOUR_CDK_KEY\"")
    print("  python examples/quickstart.py\n")

    print("Code Example 1: Context Manager Workflow (Recommended)")
    print("-" * 60)
    print("""
from shanma import CodexSmsClient, CodexSmsError

client = CodexSmsClient(cdkey="YOUR_PURCHASED_CDK")

with client.activation(service="chatgpt") as act:
    print(f"Allocated phone: {act.phone_number}")
    sms = act.wait_for_sms(timeout=120)
    if sms:
        print(f"Received code: {sms.code}")
    else:
        # Request free replacement if no code arrives
        act.switch()
        print(f"New phone: {act.phone_number}")
        sms = act.wait_for_sms(timeout=120)
""")

    print("\nCode Example 2: Batch Processing Multiple CDKs (Scrapers / AI Agents)")
    print("-" * 60)
    print("""
cdk_list = ["CDK-KEY-1", "CDK-KEY-2", "CDK-KEY-3"]

for key in cdk_list:
    client = CodexSmsClient(cdkey=key)
    try:
        order = client.redeem()
        print(f"[{key}] Phone: {order.phone_number}")
        sms = client.wait_for_sms(timeout=120)
        if sms:
            print(f"[{key}] Code: {sms.code}")
    except CodexSmsError as err:
        print(f"[{key}] Failed: {err}")
""")
    print("=" * 60)


def main():
    cdk = os.getenv("CODEX_SMS_CDK")
    if cdk and not cdk.startswith("CDK_DEMO"):
        run_live_workflow(cdk)
    else:
        show_demo_walkthrough()


if __name__ == "__main__":
    main()
