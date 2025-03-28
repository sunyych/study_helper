#!/usr/bin/env python3
"""
Simple script to test the auth token endpoint.
Usage: python test_auth.py
"""

import requests
import sys
import json

API_URL = "http://localhost:8000/api/v1"

def test_auth_token(username="admin", password="admin"):
    """Test the auth token endpoint by attempting to log in with the provided credentials."""
    print(f"Testing auth token endpoint with username: {username}")
    
    # Create form data for token request
    data = {
        "username": username,
        "password": password
    }
    
    # Make request to token endpoint
    try:
        response = requests.post(
            f"{API_URL}/auth/token", 
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Print status and response
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("\nAuthentication successful!")
            return True
        else:
            print(f"Response: {response.text}")
            print("\nAuthentication failed!")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the API: {e}")
        return False

if __name__ == "__main__":
    # Use command line arguments if provided, otherwise use defaults
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    password = sys.argv[2] if len(sys.argv) > 2 else "admin"
    
    test_auth_token(username, password) 