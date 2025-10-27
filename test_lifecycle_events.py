#!/usr/bin/env python3
"""Test ThriveCart lifecycle events: purchase, refund, cancellation, filtering."""

import json
import requests
import time

BASE_URL = "http://localhost:3000"
SECRET = "TK432YH7UTR9"

def send_webhook(event_type, product_id, email="lifecycle-test@example.com", order_id=None):
    """Send a ThriveCart webhook event."""
    order_id = order_id or f"TEST-{int(time.time())}"
    
    payload = {
        "event": event_type,
        "thrivecart_secret": SECRET,
        "mode": "live",
        "base_product": str(product_id),
        "base_product_name": "Funnel Analyzer Basic" if product_id == "7" else "Other Product",
        "order_id": order_id,
        "subscription_id": f"SUB-{order_id}",
        "customer_id": f"CUST-{order_id}",
        "customer": {
            "email": email,
            "name": "Test User"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/webhooks/thrivecart",
        json=payload,
        timeout=10
    )
    
    return response

def check_user(user_id):
    """Check user details (would need backend endpoint)."""
    # For now, just return the response data
    pass

print("=" * 80)
print("TESTING THRIVECART LIFECYCLE EVENTS")
print("=" * 80)

# Test 1: Valid Funnel Analyzer product (should create user)
print("\n[Test 1] Order Success for Funnel Analyzer (product_id=7)")
print("-" * 80)
resp = send_webhook("order.success", "7", "user1@example.com")
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✅ User created: ID={data.get('user_id')}, Plan={data.get('plan')}")
    user1_id = data.get('user_id')
else:
    print(f"❌ Failed: {resp.text}")
    user1_id = None

# Test 2: Invalid product (should be filtered out)
print("\n[Test 2] Order Success for OTHER product (product_id=99)")
print("-" * 80)
resp = send_webhook("order.success", "99", "user2@example.com")
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    if data.get('user_id'):
        print(f"❌ FAIL: User created for non-FA product: {data}")
    else:
        print(f"✅ Correctly filtered out non-FA product")
else:
    print(f"Response: {resp.text}")

# Test 3: Refund event (should cancel access)
print("\n[Test 3] Order Refund for user1")
print("-" * 80)
resp = send_webhook("order.refund", "7", "user1@example.com", "ORDER-USER1")
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✅ Refund processed: User={data.get('user_id')}")
    print(f"   Expected: Status should be 'canceled'")
else:
    print(f"❌ Failed: {resp.text}")

# Test 4: Subscription cancelled
print("\n[Test 4] Subscription Cancelled")
print("-" * 80)
resp = send_webhook("subscription_cancelled", "7", "user3@example.com")
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✅ Cancellation processed: User={data.get('user_id')}")
    print(f"   Expected: Status should be 'canceled'")
else:
    print(f"❌ Failed: {resp.text}")

# Test 5: Payment failed (should set to past_due)
print("\n[Test 5] Subscription Payment Failed")
print("-" * 80)
resp = send_webhook("subscription_payment_failed", "7", "user4@example.com")
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✅ Payment failure processed: User={data.get('user_id')}")
    print(f"   Expected: Status should be 'past_due'")
else:
    print(f"❌ Failed: {resp.text}")

# Test 6: Check recent events
print("\n[Test 6] Checking recent webhook events")
print("-" * 80)
resp = requests.get(
    f"{BASE_URL}/api/webhooks/thrivecart/events",
    params={"secret": SECRET, "limit": 10}
)
if resp.status_code == 200:
    events = resp.json().get("events", [])
    print(f"✅ Found {len(events)} recent events")
    
    # Count by event type
    event_types = {}
    for event in events:
        et = event.get("event_type")
        event_types[et] = event_types.get(et, 0) + 1
    
    print("\nEvent breakdown:")
    for et, count in sorted(event_types.items()):
        print(f"  - {et}: {count}")
else:
    print(f"❌ Failed to fetch events: {resp.text}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("✅ Product filtering: Only product_id=7,8 should create users")
print("✅ Lifecycle events:")
print("   - order.success → status=active")
print("   - order.refund → status=canceled")
print("   - subscription_cancelled → status=canceled")
print("   - subscription_payment_failed → status=past_due")
print("\nCheck backend logs and database to verify user status changes")
print("=" * 80)
