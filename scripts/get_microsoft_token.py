"""
Run this script once locally to get a Microsoft refresh token for OneNote access.

Steps:
  1. Go to https://portal.azure.com -> Azure Active Directory -> App registrations -> New registration
  2. Name it anything (e.g. "Jarvis")
  3. Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
  4. No redirect URI needed
  5. After creating, go to Authentication -> Advanced settings -> enable "Allow public client flows"
  6. Copy the Application (client) ID
  7. Run this script: uv run python scripts/get_microsoft_token.py

Then save the printed refresh token as MICROSOFT_REFRESH_TOKEN in your Render environment variables
and MICROSOFT_CLIENT_ID as the client ID.
"""

import msal

client_id = input("Paste your Azure AD Application (client) ID: ").strip()
authority = "https://login.microsoftonline.com/common"
scopes = ["Notes.Read"]  # offline_access is reserved and handled by MSAL automatically

app = msal.PublicClientApplication(client_id, authority=authority)
flow = app.initiate_device_flow(scopes=scopes)

print("\n" + flow["message"])
input("\nPress Enter after you have authenticated in the browser...")

result = app.acquire_token_by_device_flow(flow)

if "refresh_token" in result:
    print("\n--- SUCCESS ---")
    print(f"MICROSOFT_CLIENT_ID={client_id}")
    print(f"MICROSOFT_REFRESH_TOKEN={result['refresh_token']}")
    print("\nAdd both to your Render environment variables and your local .env file.")
else:
    print("\nFailed:", result.get("error_description", result))
