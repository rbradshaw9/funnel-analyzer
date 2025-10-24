#!/usr/bin/env python3
"""Test ThriveCart webhook WITHOUT signature (as ThriveCart actually sends them)."""

import json
import requests

# The refund payload you received from ThriveCart
payload = {
    "event": "order.refund",
    "mode": "live",
    "mode_int": "2",
    "thrivecart_account": "ignitiongo",
    "thrivecart_secret": "TK432YH7UTR9",  # This is validated from the payload
    "date": "2025-10-24 17:57:27",
    "date_iso8601": "2025-10-24T17:57:27+00:00",
    "date_unix": "1761328647",
    "base_product": "7",
    "base_product_name": "Funnel Analyzer Basic",
    "base_product_label": "Basic Funnel Analyzer Account",
    "base_product_owner": "72586",
    "base_payment_plan": "10521",
    "order_id": "38033257",
    "invoice_id": "000000005",
    "subscription_id": "5440433",
    "currency": "USD",
    "customer_id": "429583657898226838",
    "customer": {
        "id": "429583657898226838",
        "client_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "origin": "vanity",
        "email": "rbradshaw+2@gmail.com",
        "ip_address": "72.50.1.32",
        "address": {"country": "PR"},
        "name": " ",
        "checkbox_confirmation": "false",
        "first_name": "",
        "last_name": ""
    },
    "affiliate": "null",
    "order": {
        "id": "38033257",
        "invoice_id": "000000005",
        "processor": "stripe_connect+",
        "total": "5900",
        "total_str": "59.00",
        "total_gross": "5900",
        "total_gross_str": "59.00",
        "date": "2025-10-24 17:31:25",
        "date_iso8601": "2025-10-24T17:31:25+00:00",
        "date_unix": "1761327085",
        "tracking_id": "null",
        "tax": "null",
        "payment_method": "card"
    },
    "refund": {
        "type": "product",
        "id": "7",
        "product_id": "7",
        "name": "Funnel Analyzer Basic",
        "label": "Basic Funnel Analyzer Account",
        "processor": "stripe_connect+",
        "currency": "USD",
        "amount": "5900",
        "amount_str": "59.00",
        "amount_gross": "5900",
        "amount_gross_str": "59.00",
        "tax_paid": "0",
        "tax_paid_str": "0.00"
    },
    "event_id": "1325564304",
    "pro-rata": "false"
}

# Convert to JSON body
body = json.dumps(payload)

print("Testing ThriveCart webhook WITHOUT signature (like real ThriveCart webhooks)")
print(f"Body length: {len(body)} bytes")
print(f"Secret in payload: {payload['thrivecart_secret']}")
print()

# Send to local endpoint WITHOUT any signature header
response = requests.post(
    "http://localhost:3000/api/webhooks/thrivecart",
    data=body,
    headers={
        "Content-Type": "application/json",
        # NO signature header - ThriveCart doesn't send one by default
    }
)

print(f"Response status: {response.status_code}")
print(f"Response body: {response.text}")
print()

if response.status_code == 200:
    print("✅ SUCCESS! Webhook accepted without signature.")
    print("   The secret was validated from the payload itself.")
    
    # Check database
    response2 = requests.get(
        "http://localhost:3000/api/webhooks/thrivecart/events",
        params={"secret": "TK432YH7UTR9", "limit": 3}
    )
    
    print("\nRecent webhook events:")
    print(json.dumps(response2.json(), indent=2))
else:
    print(f"❌ FAILED with status {response.status_code}")
    print("Check backend.log for details")
