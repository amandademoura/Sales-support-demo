import streamlit as st

from admin_page import show_admin_page
from chat_page import show_chat_page
from login_page import show_login_page
from upload_page import show_upload_page

if "admin_view" not in st.session_state:
    st.session_state.admin_view = "admin"

if not st.session_state.get("authenticated"):
    show_login_page()
elif st.session_state.get("role") == "admin":
    if st.session_state.admin_view == "upload":
        show_upload_page()
    else:
        show_admin_page()
else:
    show_chat_page()