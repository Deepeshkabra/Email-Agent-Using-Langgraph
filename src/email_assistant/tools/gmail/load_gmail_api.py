# import logging
# import os
# import json
# from typing import Dict, Any
# from pathlib import Path
# import base64
# from googleapiclient.discovery import build
# from email.mime.text import MIMEText
# from datetime import timedelta
# from dateutil.parser import parse as parse_time
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

#     # Function to get credentials from token.json or environment variables
# def load_gmail_credentials_from_token(gmail_token=None, gmail_secret=None):
#         """
#         Get Gmail API credentials from token.json or environment variables.

#         This function attempts to load credentials from multiple sources in this order:
#         1. Directly passed gmail_token and gmail_secret parameters
#         2. Environment variables GMAIL_TOKEN and GMAIL_SECRET
#         3. Local files at token_path (.secrets/token.json) and secrets_path (.secrets/secrets.json)

#         Args:
#             gmail_token: Optional JSON string containing token data
#             gmail_secret: Optional JSON string containing credentials

#         Returns:
#             Google OAuth2 Credentials object or None if credentials can't be loaded
#         """
#         token_path = Path(__file__).parent.absolute() / ".secrets" / "token.json"
#         token_data = None

#         # Try to get token data from various sources
#         if gmail_token:
#             # 1. Use directly passed token parameter if available
#             try:
#                 token_data = json.loads(gmail_token) if isinstance(gmail_token, str) else gmail_token
#                 print("Using directly provided gmail_token parameter")
#             except Exception as e:
#                 print(f"Could not parse provided gmail_token: {str(e)}")

#         if token_data is None:
#             # 2. Try environment variable
#             env_token = os.getenv("GMAIL_TOKEN")
#             if env_token:
#                 try:
#                     token_data = json.loads(env_token)
#                     print("Using GMAIL_TOKEN environment variable")
#                 except Exception as e:
#                     print(f"Could not parse GMAIL_TOKEN environment variable: {str(e)}")

#         if token_data is None:
#             # 3. Try local file
#             if os.path.exists(token_path):
#                 try:
#                     with open(token_path, "r") as f:
#                         token_data = json.load(f)
#                     print(f"Using token from {token_path}")
#                 except Exception as e:
#                     print(f"Could not load token from {token_path}: {str(e)}")

#         # If we couldn't get token data from any source, return None
#         if token_data is None:
#             print("Could not find valid token data in any location")
#             return None

#         try:
#             from google.oauth2.credentials import Credentials

#             # Create credentials object with specific format
#             credentials = Credentials(
#                 token=token_data.get("token"),
#                 refresh_token=token_data.get("refresh_token"),
#                 token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
#                 client_id=token_data.get("client_id"),
#                 client_secret=token_data.get("client_secret"),
#                 scopes=token_data.get("scopes", ["https://www.googleapis.com/auth/gmail.modify"])
#             )

#             # Add authorize method to make it compatible with old code
#             credentials.authorize = lambda request: request

#             return credentials
#         except Exception as e:
#             print(f"Error creating credentials object: {str(e)}")
#             return None


