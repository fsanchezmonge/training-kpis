import streamlit as st
from utils.logic import is_valid_email, insert_user, hash_password, login_user

if "user" not in st.session_state:
    st.session_state.user = None

options = ["Login", "Signup"]
selection = st.selectbox("", options,label_visibility="hidden")

if selection == "Signup":
    with st.container():
        # Create the signup form using Streamlit's form
        with st.form("signup_form"):
            email = st.text_input("Email")
            if not is_valid_email(email) and len(email)>0:
                st.error("Please enter a valid email address.")
            
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button("Register")
            if submitted:
                insert_user(email,hash_password(password))
                st.success(f"Your account has been created!")
                st.session_state.login_email = ""  # Clear email
                st.session_state.login_password = ""  # Clear password

else:
    with st.container():
        # Create the signup form using Streamlit's form
        with st.form("login_form"):
            email = st.text_input("Email")
            if not is_valid_email(email) and len(email)>0:
                st.error("Please enter a valid email address.")
            
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button("Login")
            if submitted:
                response = login_user(email,hash_password(password))
                if response:
                    st.success("logged in")
                    st.session_state.user=email
                else:
                    st.error("Incorrect email or password")