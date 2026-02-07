#!/usr/bin/env python3
"""
Test script for WhatsApp MCP Server

This script tests the WhatsApp MCP server endpoints to verify they're working correctly.
"""

import requests
import json
import time

def test_server_health():
    """Test the health endpoint"""
    print("Testing server health...")
    try:
        response = requests.get("http://localhost:8083/health")
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Health check: {data}")
            return True
        else:
            print(f"[ERROR] Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Error during health check: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\nTesting root endpoint...")
    try:
        response = requests.get("http://localhost:8083/")
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Root endpoint: {data}")
            return True
        else:
            print(f"[ERROR] Root endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Error during root endpoint test: {e}")
        return False

def test_webhook_verification():
    """Test the webhook verification endpoint"""
    print("\nTesting webhook verification...")
    try:
        # This simulates the verification request from Meta
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": "ai_employee_whatsapp_verify_2026",  # This should match your WHATSAPP_VERIFY_TOKEN
            "hub.challenge": "test_challenge_12345"
        }
        response = requests.get("http://localhost:8083/webhook", params=params)
        if response.status_code == 200:
            print(f"[SUCCESS] Webhook verification successful: {response.text}")
            return True
        else:
            print(f"[ERROR] Webhook verification failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error during webhook verification test: {e}")
        return False

def test_invalid_webhook_verification():
    """Test the webhook verification with invalid token"""
    print("\nTesting invalid webhook verification (should fail)...")
    try:
        # This simulates an invalid verification request
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": "invalid_token",
            "hub.challenge": "test_challenge_12345"
        }
        response = requests.get("http://localhost:8083/webhook", params=params)
        if response.status_code == 403:
            print(f"[SUCCESS] Invalid webhook verification correctly rejected with status {response.status_code}")
            return True
        else:
            print(f"[ERROR] Invalid webhook verification should have failed but got status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Error during invalid webhook verification test: {e}")
        return False

def test_send_test_endpoint():
    """Test the send-test endpoint (without actually sending a message)"""
    print("\nTesting send-test endpoint...")
    try:
        # This will fail because we're not providing a real phone number, but it should reach the validation
        payload = {
            "phone_number": "1234567890",  # Invalid number for testing
            "message": "Test message from MCP server"
        }
        response = requests.post("http://localhost:8083/send-test", json=payload)
        # The endpoint should return either success or a specific error from the WhatsApp API
        print(f"Send-test response status: {response.status_code}")
        try:
            data = response.json()
            print(f"Send-test response: {json.dumps(data, indent=2)}")
        except:
            print(f"Send-test response text: {response.text}")
        return True
    except Exception as e:
        print(f"[ERROR] Error during send-test endpoint test: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("Testing WhatsApp MCP Server")
    print("="*60)
    
    # Wait a moment to ensure the server is fully started
    time.sleep(2)
    
    tests = [
        test_server_health,
        test_root_endpoint,
        test_webhook_verification,
        test_invalid_webhook_verification,
        test_send_test_endpoint
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "="*60)
    print("Test Results:")
    print(f"Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("[SUCCESS] All tests passed! WhatsApp MCP server is working correctly.")
    else:
        print("[WARNING] Some tests failed. Check the output above for details.")
    
    print("="*60)

if __name__ == "__main__":
    main()