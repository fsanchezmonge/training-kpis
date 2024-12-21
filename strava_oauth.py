from urllib.parse import urlencode
import json
import requests
import streamlit as st

# Constants for the Strava API
CLIENT_ID = '95885'
CLIENT_SECRET = '9bd58f9a50e4a12d165a373bec9afe40754f4962'
REDIRECT_URI = "http://localhost:8501/"  # Update to your deployed URL
AUTH_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"

# Function to generate Strava Authorization URL
def generate_auth_url(client_id, redirect_uri):
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "approval_prompt": "auto",
        "scope": "read,activity:read_all"
    }
    return f"{AUTH_URL}?{urlencode(params)}"

# Function to exchange authorization code for access token
def exchange_token(client_id, client_secret, code):
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code"
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error exchanging token: " + response.content.decode())
        return None



# Check if a code is provided by the Strava redirect
# Main app flow
st.title("Training Data Monitor - Strava Integration")

# Check if a code is provided by the Strava redirect
code = st.query_params.get("code")
st.write(code)
# Make sure the code is properly retrieved and is not just 'a'
if code is not None and len(code) > 0:
    code = code[0]
    if code == None:
        st.error("Invalid authorization code received: None. Please try again.")
    else:
        # Exchange the authorization code for an access token
        token_response = exchange_token(CLIENT_ID, CLIENT_SECRET, code)
        if token_response:
            # Extract and store the token (you might save it to your database here)
            access_token = token_response['access_token']
            st.success("Strava account connected successfully!")
            st.write("Access Token:", access_token)
            # Optionally, save user information or other details
            user_info = {
                "access_token": access_token,
                "refresh_token": token_response['refresh_token'],
                "expires_at": token_response['expires_at']
            }
            # Here you can add your logic to save the user info into your database
            st.write("User Info:", json.dumps(user_info, indent=4))
else:
    # No authorization code, show button for user to connect their Strava account
    auth_url = generate_auth_url(CLIENT_ID, REDIRECT_URI)
    st.write("### Connect your Strava Account")
    st.markdown(f"[Connect to Strava]({auth_url})", unsafe_allow_html=True)

