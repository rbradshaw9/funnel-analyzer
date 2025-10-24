#!/usr/bin/env python3
"""Test complete purchase flow: webhook -> user created -> magic link sent -> dashboard access."""

import json
import requests

# Test configuration
BASE_URL = "http://localhost:3000"
SECRET = "TK432YH7UTR9"
TEST_EMAIL = "test-buyer@example.com"

print("=" * 80)
print("TESTING COMPLETE PURCHASE FLOW")
print("=" * 80)

# Step 1: Simulate ThriveCart order.success webhook
print("\n[Step 1] Simulating ThriveCart order.success webhook...")
print(f"  Customer email: {TEST_EMAIL}")

order_payload = {
    "event": "order.success",
    "mode": "live",
    "mode_int": "2",
    "thrivecart_account": "ignitiongo",
    "thrivecart_secret": SECRET,
    "date": "2025-10-24 18:30:00",
    "date_iso8601": "2025-10-24T18:30:00+00:00",
    "date_unix": "1761330600",
    "base_product": "7",
    "base_product_name": "Funnel Analyzer Basic",
    "base_product_label": "Basic Funnel Analyzer Account",
    "base_payment_plan": "10521",
    "order_id": "TEST-ORDER-001",
    "invoice_id": "TEST-INV-001",
    "subscription_id": "TEST-SUB-001",
    "currency": "USD",
    "customer_id": "TEST-CUST-001",
    "customer": {
        "id": "TEST-CUST-001",
        "email": TEST_EMAIL,
        "name": "Test Buyer",
        "first_name": "Test",
        "last_name": "Buyer"
    },
    "order": {
        "id": "TEST-ORDER-001",
        "invoice_id": "TEST-INV-001",
        "processor": "stripe",
        "total": "5900",
        "total_str": "59.00",
        "date": "2025-10-24 18:30:00",
        "payment_method": "card"
    }
}

body = json.dumps(order_payload)

try:
    response = requests.post(
        f"{BASE_URL}/api/webhooks/thrivecart",
        data=body,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"  ✓ Webhook status: {response.status_code}")
    
    if response.status_code == 200:
        webhook_data = response.json()
        print(f"  ✓ Response: {json.dumps(webhook_data, indent=2)}")
        
        user_id = webhook_data.get("user_id")
        plan = webhook_data.get("plan")
        
        if user_id:
            print(f"  ✓ User created/updated: ID={user_id}, Plan={plan}")
        
        print("\n  ✅ SUCCESS: Purchase webhook processed")
        print(f"  → Magic link should be sent to {TEST_EMAIL}")
        print(f"  → Check your email service (SendGrid/Resend) for delivery")
        
    else:
        print(f"  ❌ FAILED: {response.text}")
        exit(1)
        
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    exit(1)

# Step 2: Check that user was created with correct status
print("\n[Step 2] Verifying user creation...")
print("  (This would require a backend endpoint to query user by email)")
print("  For now, check the database directly or backend logs")

# Step 3: Instructions for testing magic link
print("\n[Step 3] Testing magic link login...")
print("  1. Check your email service dashboard for the magic link email")
print(f"  2. The email should be sent to: {TEST_EMAIL}")
print("  3. Click the magic link in the email")
print("  4. It should redirect to: http://localhost:3001/dashboard?token=...")
print("  5. The dashboard should load with your account info")

print("\n" + "=" * 80)
print("MANUAL VERIFICATION STEPS:")
print("=" * 80)
print(f"1. Check SendGrid/Resend dashboard for email to {TEST_EMAIL}")
print("2. Extract the token from the magic link URL")
print("3. Open: http://localhost:3001/dashboard?token=YOUR_TOKEN")
print("4. Verify dashboard shows:")
print("   - User is authenticated")
print(f"   - Email: {TEST_EMAIL}")
print("   - Plan: basic")
print("   - Status: active")
print("   - Access granted: Yes")
print("\n" + "=" * 80)

# Optional: Test magic link request endpoint
print("\n[Optional] Testing /api/auth/magic-link endpoint...")
try:
    magic_response = requests.post(
        f"{BASE_URL}/api/auth/magic-link",
        json={"email": TEST_EMAIL},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if magic_response.status_code == 200:
        magic_data = magic_response.json()
        print(f"  ✓ Magic link request: {magic_data.get('status')}")
        print(f"  ✓ Message: {magic_data.get('message')}")
    else:
        print(f"  ⚠ Magic link request failed: {magic_response.status_code}")
        
except Exception as e:
    print(f"  ⚠ Could not test magic link endpoint: {e}")

print("\n✅ Test script complete!")
print("Check your email and follow the manual verification steps above.")
