import streamlit as st
from auth import add_user, delete_user, load_credentials


def show_admin_page():
    st.set_page_config(page_title="Admin", page_icon="🛡️")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    if "role" not in st.session_state:
        st.session_state.role = "guest"

    if not st.session_state.authenticated or st.session_state.role != "admin":
        st.info("Access denied.")
        return

    header_col, logout_col = st.columns([6, 1])
    with header_col:
        st.title("Admin Interface")
    with logout_col:
        if st.button("Logout", use_container_width=True, key="admin_logout_button"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.role = "guest"
            st.rerun()

    st.success("You are logged in as admin.")

    st.subheader("Upload documents")
    if st.button("Upload", key="admin_upload_nav"):
        st.session_state.admin_view = "upload"
        st.rerun()

    st.subheader("Stored users")
    users = load_credentials()
    if users:
        for username in list(users.keys()):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(username)
            with col2:
                if st.button("Delete", key=f"delete_{username}"):
                    delete_user(username)
                    st.success(f"User '{username}' deleted.")
                    st.rerun()
    else:
        st.info("No saved users yet.")
