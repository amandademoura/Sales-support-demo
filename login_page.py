import streamlit as st

from auth import is_admin_login, save_credentials


def show_login_page():
    st.set_page_config(page_title="Login", page_icon="🔐")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "role" not in st.session_state:
        st.session_state.role = "guest"

    header_col, logout_col = st.columns([6, 1])
    with header_col:
        st.title("Login")
    with logout_col:
        if st.session_state.authenticated:
            if st.button("Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.current_user = None
                st.session_state.messages = []
                st.rerun()

    if st.session_state.authenticated:
        st.success("You are already logged in.")
        st.rerun()

    st.write("Add a username and password to log in.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if username and password:
            if is_admin_login(username, password):
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.session_state.role = "admin"
                st.session_state.messages = []
                st.success("Admin login successful.")
                st.rerun()

            save_credentials(username, password)
            st.session_state.authenticated = True
            st.session_state.current_user = username
            st.session_state.role = "guest"
            st.session_state.messages = []
            st.success("You are now logged in.")
            st.rerun()
        else:
            st.warning("Please enter both a username and password.")