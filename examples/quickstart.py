"""
Codex SMS Python SDK - Quickstart Example (v0.3.0)
Demonstrates redeeming a phone number, receiving SMS, and handling replacement switches.
"""

import sys
import os

# Allow running directly from local repo source
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shanma import (
    CodexSmsClient,
    ShanmaError,
    AuthenticationError,
    CdkAlreadyUsedError,
    RateLimitError,
)

def main():
    # Pass your CDK (Card Secret Key) purchased from https://shanma.store
    cdkey = os.getenv("CODEX_SMS_CDK", "CDK_DEMO_SECRET_KEY")
    print("Initializing Codex SMS client (v0.3.0)...")

    try:
        client = CodexSmsClient(cdkey=cdkey)
    except AuthenticationError as e:
        print(f"Auth error: {e}")
        return

    print("Client initialized successfully.")
    print("Example 1: Context Manager Workflow (Recommended)")
    print("-" * 50)
    print("""
    from shanma import CodexSmsClient

    client = CodexSmsClient(cdkey="YOUR_CDK_HERE")

    with client.activation(service="chatgpt") as act:
        print(f"Allocated phone: {act.phone_number}")
        print("Waiting for SMS code...")
        
        sms = act.wait_for_sms(timeout=120)
        if sms:
            print(f"Received verification code: {sms.code}")
        else:
            print("Did not receive code within timeout. Requesting replacement number...")
            act.switch()
            print(f"New replacement phone: {act.phone_number}")
            sms = act.wait_for_sms(timeout=120)
    """)

    print("\nExample 2: Batch Processing Multiple CDKs")
    print("-" * 50)
    print("""
    cdkeys = ["CDK_KEY_1", "CDK_KEY_2", "CDK_KEY_3"]

    for key in cdkeys:
        client = CodexSmsClient(cdkey=key)
        try:
            order = client.redeem(service="telegram")
            print(f"[{key}] Number: {order.phone_number}")
            sms = client.wait_for_sms(timeout=120)
            if sms:
                print(f"[{key}] Code: {sms.code}")
        except Exception as e:
            print(f"[{key}] Failed: {e}")
    """)

if __name__ == "__main__":
    main()
