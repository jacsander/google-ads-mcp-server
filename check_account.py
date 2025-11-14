#!/usr/bin/env python3
"""Script to check which Google account is being used for OAuth."""

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import requests

# OAuth credentials - load from oauth_credentials.json or environment variables
import json
import os

# Try to load from oauth_credentials.json first
if os.path.exists('oauth_credentials.json'):
    with open('oauth_credentials.json', 'r') as f:
        creds_data = json.load(f)
        CLIENT_ID = creds_data.get('client_id')
        CLIENT_SECRET = creds_data.get('client_secret')
        REFRESH_TOKEN = creds_data.get('refresh_token')
else:
    # Fall back to environment variables
    CLIENT_ID = os.environ.get('GOOGLE_ADS_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('GOOGLE_ADS_CLIENT_SECRET')
    REFRESH_TOKEN = os.environ.get('GOOGLE_ADS_REFRESH_TOKEN')

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    print("Error: OAuth credentials not found!")
    print("Please either:")
    print("  1. Create oauth_credentials.json with client_id, client_secret, and refresh_token")
    print("  2. Set environment variables: GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN")
    exit(1)

# Create credentials
creds = Credentials(
    token=None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=['https://www.googleapis.com/auth/adwords']
)

# Refresh to get access token
print("Refreshing OAuth token...")
creds.refresh(Request())
print(f"Access token obtained: {creds.token[:20]}...")

# Try to get user info (may not work if scope not included)
print("\nAttempting to get user info...")
try:
    r = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {creds.token}'}
    )
    if r.status_code == 200:
        user_info = r.json()
        print(f"Email: {user_info.get('email', 'Not available')}")
        print(f"Name: {user_info.get('name', 'Not available')}")
    else:
        print(f"Could not get user info (status {r.status_code}): {r.text}")
        print("This is expected - the OAuth token only has adwords scope, not userinfo scope.")
except Exception as e:
    print(f"Error getting user info: {e}")

# Try to get account info from Google Ads API
print("\nAttempting to get account info from Google Ads API...")
try:
    from google.ads.googleads.client import GoogleAdsClient
    import os
    
    # Set up the client
    client = GoogleAdsClient(
        credentials=creds,
        developer_token=os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"),
        login_customer_id=None,
    )
    
    # Try to list accessible customers
    customer_service = client.get_service("CustomerService")
    # This might fail if account has no Ads access, but let's try
    print("Note: If this fails with NOT_ADS_USER, it confirms the account has no Google Ads access.")
    
except Exception as e:
    print(f"Error accessing Google Ads API: {e}")
    if "NOT_ADS_USER" in str(e):
        print("\n⚠️  CONFIRMED: The account used for OAuth does NOT have access to Google Ads accounts.")
        print("This is why you're getting the NOT_ADS_USER error.")
    elif "@gmail.com" in str(e) or "@" in str(e):
        # Try to extract email from error message
        import re
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', str(e))
        if email_match:
            print(f"\nFound email in error message: {email_match.group()}")

