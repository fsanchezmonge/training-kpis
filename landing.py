import streamlit as st

def main():
    page_bg_img = """
    <style>
    /* Override the default body background */
    body {
        background-image: url("https://images.unsplash.com/photo-1612831455549-43e4f05e4f9a");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    """
    # Create a centered container for the sign-up form
    with st.container():
        # Create the signup form using Streamlit's form
        with st.form("signup_form"):
            name = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button()
            if submitted:
                st.success(f"Thank you for signing up, {name}!")

if __name__ == "__main__":
    main()