"""
Codex SMS Python SDK - Quickstart Example (v0.2.0)
Demonstrates ordering a virtual phone number, context manager, and error handling.
"""

import sys
import os

# Allow running directly from local repo source
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shanma import (
    CodexSmsClient,
    ShanmaClient,
    AuthenticationError,
    InsufficientBalanceError,
    ShanmaError,
)

def main():
    api_key = os.getenv("SHANMA_API_KEY", "demo_api_token_here")
    print("Initializing Codex SMS client (v0.2.0)...")
    
    try:
        client = CodexSmsClient(api_key=api_key)
    except AuthenticationError as e:
        print(f"Auth error: {e}")
        return

    # 1. Check account balance
    try:
        balance = client.get_balance()
        print(f"Current balance: {balance:.2f} credits")
    except ShanmaError as e:
        print(f"Notice: Balance check returned: {e}")

    # 2. Check available services & stock
    try:
        services = client.get_available_services(country="usa")
        print(f"Found {len(services)} available services for USA.")
        for svc in services[:3]:
            print(f" - {svc.get('name')}: {svc.get('cost')} credits ({svc.get('count')} in stock)")
    except ShanmaError as e:
        print(f"Notice: Services lookup returned: {e}")

    # 3. Recommended: Context Manager Pattern (Auto-cancel on timeout/failure)
    print("\nDemonstrating Pythonic Context Manager workflow:")
    print(">>> with client.activation(service='chatgpt', country='usa') as act:")
    print(">>>     print(f'Assigned number: {act.order.phone_number}')")
    print(">>>     sms = act.wait_for_sms(timeout=180)")
    print(">>>     if sms: print(f'Verification code: {sms.code}')")
    print(">>> # If no SMS arrives, order is automatically cancelled & refunded!\n")

    print("Completed quickstart walkthrough.")

if __name__ == "__main__":
    main()
