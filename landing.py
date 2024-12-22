import streamlit as st

raw_url = "https://github.com/fsanchezmonge/training-kpis/blob/oauth-flow/background_img.png"
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background-image: url("https://github.com/fsanchezmonge/training-kpis/blob/oauth-flow/background_img.png?raw=true");
background-size: cover;
;
}
[data-testid="stHeader"]{
background-color: rgba(0,0,0,0);
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

with st.container():
    # Create the signup form using Streamlit's form
    with st.form("signup_form"):
        name = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button()
        if submitted:
            st.success(f"Thank you for signing up, {name}!")
