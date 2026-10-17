"""
Codex SMS (ShanMa) Python SDK - Quickstart Example
Demonstrates ordering a virtual phone number, waiting for SMS, and error handling.
"""

import sys
import os

# Allow running directly from local repo source
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shanma import ShanmaClient, AuthenticationError, InsufficientBalanceError, ShanmaError

def main():
    api_key = os.getenv("SHANMA_API_KEY", "demo_api_token_here")
    print(f"Initializing Codex SMS client...")
    
    try:
        client = ShanmaClient(api_key=api_key)
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

    # 3. Simulated Order & SMS Polling workflow
    print("\nDemonstrating order lifecycle (dry-run):")
    print(">>> order = client.order_number(service='openai', country='usa')")
    print(">>> print(f'Assigned number: {order.phone_number}')")
    print(">>> sms = client.wait_for_sms(order.activation_id, timeout=120)")
    print(">>> if sms: print(f'Verification code: {sms.code}')")
    print(">>> else: client.cancel_order(order.activation_id)  # Auto refund\n")
    print("Completed quickstart walkthrough.")

if __name__ == "__main__":
    main()
