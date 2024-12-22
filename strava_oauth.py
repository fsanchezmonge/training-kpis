import os
import time
import requests
import streamlit as st
from supabase import create_client, Client
import datetime

################################################################################
# 1. Configuration
################################################################################

# (A) STRAVA CONFIG
# Replace with your own Strava client ID, secret, and the same redirect URI set in Strava app settings.
STRAVA_CLIENT_ID = "108350"  #os.getenv("STRAVA_CLIENT_ID", "<YOUR_STRAVA_CLIENT_ID>")
STRAVA_CLIENT_SECRET = "a053ead2d1c3c6f96f4e85452ebb40018cb2a3a9" #os.getenv("STRAVA_CLIENT_SECRET", "<YOUR_STRAVA_CLIENT_SECRET>")
STRAVA_REDIRECT_URI = "http://localhost:8501"  # or your deployed Streamlit URL
STRAVA_SCOPES = "read,activity:read,activity:read_all"  # Adjust scopes as needed

# (B) SUPABASE CONFIG
# Replace with your real Supabase URL and anon (or service) key
SUPABASE_URL = "https://mwivhbuesrdrfhihxjqs.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im13aXZoYnVlc3JkcmZoaWh4anFzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTk4NjE0NzQsImV4cCI6MjAzNTQzNzQ3NH0.cG7N8em6tqc2OWijtqTQg-EkUqHM6Bcf7grg-bPDcDA"

# (C) CREATE SUPABASE CLIENT
@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

supabase = get_supabase_client()

################################################################################
# 2. Build Strava OAuth authorization link
################################################################################

def build_strava_oauth_url():
    """
    Returns a URL to initiate the OAuth flow with Strava. 
    The user will click this link, log in to Strava, and authorize your app.
    Strava will then redirect back to STRAVA_REDIRECT_URI with a `code` query param.
    """
    base = "https://www.strava.com/oauth/authorize"
    params = (
        f"?client_id={STRAVA_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={STRAVA_REDIRECT_URI}"
        f"&scope={STRAVA_SCOPES}"
        f"&approval_prompt=force"  # or 'auto'
    )
    return base + params

################################################################################
# 3. Exchange the OAuth code for an access token
################################################################################

def exchange_code_for_token(code: str):
    """
    Given the 'code' returned by Strava, exchange it for an
    access token, refresh token, and athlete details.
    """
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        st.error(f"Failed to exchange code for token. Error: {response.text}")
        st.stop()

    data = response.json()
    return data  # includes access_token, refresh_token, expires_at, athlete, etc.

################################################################################
# 4. Store the credentials in Supabase
################################################################################

def store_strava_credentials(
    user_key: str,
    athlete_id: int,
    access_token: str,
    refresh_token: str,
    expires_at: str
):
    """
    Insert or update the Strava credentials in your Supabase table.
    Typically you'd do an 'upsert' based on user_id or athlete_id.
    """
    # Convert expires_at to datetime
    dt = datetime.datetime.fromtimestamp(expires_at, tz=datetime.timezone.utc)

    # Convert to ISO 8601 or any standard format
    expires_at = dt.isoformat() 
   
    table_name = "dim_user"
    data = {
        "user_key": user_key,
        "athlete_id": athlete_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
    }
    st.write(data)
    # If you want to upsert based on `user_id` OR `strava_athlete_id`, you can do:
    result = (
        supabase
        .table(table_name)
        .upsert(data, on_conflict="user_key")  # or "strava_athlete_id"
        .execute()
    )


################################################################################
# 5. Main Streamlit logic
################################################################################

def main():
    st.title("Strava OAuth Example")

    # 5A. Check if we came back from Strava with a code
    query_params = st.query_params
    st.write("All query params:", query_params)

    code = query_params.get("code", [])

    if code:
        # We have an OAuth code, so let's exchange it for tokens
        st.write("Exchanging code for tokens...")
        token_data = exchange_code_for_token(code)

        # Extract what we need
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        expires_at = token_data["expires_at"]  # Unix timestamp
        athlete_id = token_data["athlete"]["id"]
        
        # You might have your own user system. For example, 
        # if the user is logged into your Streamlit app, you might track their user_id in session_state.
        # For demo, we’ll just set user_id = athlete_id or something static.
        user_key = str(st.session_state.get("current_user", athlete_id))

        # Store in Supabase
        store_strava_credentials(
            user_key=user_key,
            athlete_id=athlete_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )

        st.write("Credentials saved! You can now use them to fetch Strava data.")
        st.write("Access Token:", access_token)
        st.write("Refresh Token:", refresh_token)
        st.write("Expires At:", time.ctime(expires_at))

    else:
        # 5B. We do NOT have a code yet, so show a button to start the OAuth flow
        st.write("Click below to connect your Strava account:")
        auth_url = build_strava_oauth_url()
        
        # Option 1: Provide a clickable link
        if st.button("Authenticate with Strava"):
            st.markdown(f"[Click here to authorize Strava]({auth_url})")

        # Option 2 (Alternative): Directly open a new tab (some browsers might block it).
        # st.markdown(f"<a href='{auth_url}' target='_self'>Authenticate with Strava</a>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()