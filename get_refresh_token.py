#!/usr/bin/env python3
"""Script to generate OAuth refresh token for Google Ads API."""

from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os

# Google Ads API scope
SCOPES = ['https://www.googleapis.com/auth/adwords']

def find_client_secret_file():
    """Find the client secret file in the current directory."""
    # First check if explicitly set via environment variable
    env_file = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET_FILE')
    if env_file and os.path.exists(env_file):
        return env_file
    
    # Otherwise, look for any client_secret_*.txt file
    import glob
    files = glob.glob('client_secret_*.txt')
    if files:
        return files[0]
    
    return None

def main():
    # Find the client secret file
    CLIENT_SECRET_FILE = find_client_secret_file()
    if not CLIENT_SECRET_FILE:
        print("Error: Client secret file not found!")
        print("Please either:")
        print("  1. Set GOOGLE_OAUTH_CLIENT_SECRET_FILE environment variable")
        print("  2. Place a client_secret_*.txt file in the current directory")
        print("     (Download from Google Cloud Console > APIs & Services > Credentials)")
        return
    
    # Read the client secret file
    with open(CLIENT_SECRET_FILE, 'r') as f:
        client_config = json.load(f)
    
    # Check if it's a web client (we need to convert it for desktop flow)
    if 'web' in client_config:
        # Get redirect URIs from the web config
        web_redirect_uris = client_config['web'].get('redirect_uris', [])
        print(f"Configured redirect URIs in OAuth client: {web_redirect_uris}")
        
        # For installed app flow, we need to use the same redirect URIs
        # The run_local_server will use http://localhost:PORT/ by default
        # Make sure http://localhost:8080 is in the list
        if not web_redirect_uris:
            print("Warning: No redirect URIs found in client config. Adding defaults.")
            web_redirect_uris = ['http://localhost', 'http://localhost:8080']
        
        # Convert web client config to installed app config
        installed_config = {
            'installed': {
                'client_id': client_config['web']['client_id'],
                'client_secret': client_config['web']['client_secret'],
                'auth_uri': client_config['web']['auth_uri'],
                'token_uri': client_config['web']['token_uri'],
                'auth_provider_x509_cert_url': client_config['web']['auth_provider_x509_cert_url'],
                'redirect_uris': web_redirect_uris
            }
        }
        print(f"Using redirect URIs: {web_redirect_uris}")
        
        # Verify http://localhost:8080 is configured
        if 'http://localhost:8080' not in web_redirect_uris and 'http://localhost:8080/' not in web_redirect_uris:
            print("\n⚠️  WARNING: http://localhost:8080 is not in your redirect URIs!")
            print("Please add 'http://localhost:8080' to your OAuth client's Authorised redirect URIs in Google Cloud Console.")
            print("Current redirect URIs:", web_redirect_uris)
    else:
        installed_config = client_config
    
    print("Starting OAuth flow...")
    print("A browser window will open for you to authenticate.")
    print("Make sure you use a Google account that has access to Google Ads accounts.\n")
    
    # Create the flow with offline access to get refresh token
    flow = InstalledAppFlow.from_client_config(installed_config, SCOPES)
    flow.redirect_uri = 'http://localhost:8080/'  # Explicitly set redirect URI
    
    # Run the OAuth flow
    # Use port 8080 explicitly to match OAuth client configuration
    print("\nStarting OAuth flow...")
    print("Using port 8080 - make sure http://localhost:8080/ is in your OAuth client.")
    print("A browser window will open for authentication.")
    print("\n⚠️  IMPORTANT: Make sure you sign in with jacob.sander@fiskars.com (or another account with Google Ads access)")
    print("   The account you use here must have access to Google Ads accounts.")
    print("   If you see a 'Select Account' screen, choose jacob.sander@fiskars.com\n")
    
    try:
        # Use run_local_server which automatically opens browser and handles redirect
        # We need to ensure offline access and consent prompt are included
        # The flow needs to be configured before calling run_local_server
        
        # Create a custom authorization URL with offline access
        # This will be used by run_local_server
        print("\nOpening browser for authentication...")
        print("Make sure to select jacob.sander@fiskars.com when prompted!\n")
        
        # Use run_local_server with a custom authorization URL builder
        # We'll override the authorization_url method temporarily to include offline access
        original_auth_url = flow.authorization_url
        
        def auth_url_with_offline(**kwargs):
            """Custom authorization URL that always includes offline access."""
            kwargs.setdefault('access_type', 'offline')
            kwargs.setdefault('prompt', 'consent')
            kwargs.setdefault('include_granted_scopes', 'true')
            return original_auth_url(**kwargs)
        
        flow.authorization_url = auth_url_with_offline
        
        # Now run the local server - it will use our custom auth_url method
        creds = flow.run_local_server(
            port=8080,
            open_browser=True,
            authorization_prompt_message="\nPlease visit this URL to authorize this application:",
            success_message="\n✓ Authentication successful! You may close this window."
        )
        
        # Verify we got a refresh token
        if not creds.refresh_token:
            print("\n" + "="*60)
            print("⚠️  WARNING: No refresh token received!")
            print("="*60)
            print("\nThis usually means the account already has a refresh token.")
            print("\nTo get a new refresh token:")
            print("  1. Go to: https://myaccount.google.com/permissions")
            print("  2. Find your app (search for 'Google Ads' or the client ID)")
            print("  3. Click 'Remove Access' or 'Revoke'")
            print("  4. Run this script again")
            print("\nAlternatively, you can use the existing refresh token if you have it.")
            return
    except OSError as e:
        # Port 8080 might be in use
        print(f"Port 8080 is not available: {e}")
        print("Please close any application using port 8080 and try again.")
        return
    except Exception as e:
        error_str = str(e).lower()
        if 'redirect_uri_mismatch' in error_str or 'redirect_uri' in error_str:
            print("\n" + "="*60)
            print("ERROR: Redirect URI mismatch!")
            print("="*60)
            print("\nThe library is trying to use: http://localhost:8080/")
            print("\nPlease verify in Google Cloud Console:")
            print("  1. Go to APIs & Services > Credentials")
            print("  2. Click on your OAuth client 'MCP server'")
            print("  3. In 'Authorised redirect URIs', make sure you have EXACTLY:")
            print("     http://localhost:8080/")
            print("     (WITH trailing slash, port 8080)")
            print("\nImportant:")
            print("  - Changes can take 2-5 minutes to propagate")
            print("  - The URI must match EXACTLY: http://localhost:8080/")
            print("  - Must include the trailing slash")
            print("  - Must be http:// not https://")
            print("\nAfter updating, wait 2-3 minutes, then try again.")
            return
        else:
            raise
    
    # Extract the credentials
    print("\n" + "="*60)
    print("OAuth credentials obtained successfully!")
    print("="*60)
    print(f"\nClient ID: {installed_config['installed']['client_id']}")
    print(f"Client Secret: {installed_config['installed']['client_secret']}")
    print(f"Refresh Token: {creds.refresh_token}")
    print("\n" + "="*60)
    print("IMPORTANT: Save these values securely!")
    print("You'll need them to configure Cloud Run.")
    print("="*60)
    
    # Save to a file for easy reference (but don't commit to git!)
    output = {
        'client_id': installed_config['installed']['client_id'],
        'client_secret': installed_config['installed']['client_secret'],
        'refresh_token': creds.refresh_token
    }
    
    with open('oauth_credentials.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\nCredentials also saved to: oauth_credentials.json")
    print("⚠️  DO NOT commit this file to git!")

if __name__ == '__main__':
    main()

