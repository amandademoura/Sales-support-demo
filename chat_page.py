import streamlit as st
from agent import remember, run_agent
from auth import load_chat_history, save_chat_history


def show_chat_page():
    st.set_page_config(page_title="Chat", page_icon="💬")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "conversations" not in st.session_state:
        loaded_history = load_chat_history(st.session_state.current_user)
        if isinstance(loaded_history, dict):
            st.session_state.conversations = loaded_history
        elif isinstance(loaded_history, list):
            st.session_state.conversations = {"Conversation 1": loaded_history}
        else:
            st.session_state.conversations = {}
    if "active_conversation" not in st.session_state:
        st.session_state.active_conversation = None

    if not st.session_state.authenticated:
        st.info("Please log in first.")
        return

    header_col, logout_col = st.columns([6, 1])
    with header_col:
        st.title("Chat")
    with logout_col:
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.conversations = {}
            st.session_state.active_conversation = None
            st.rerun()

    st.caption(f"Signed in as: {st.session_state.current_user}")

    with st.sidebar:
        st.subheader("Conversations")
        if st.button("New conversation"):
            existing_numbers = []
            for name in st.session_state.conversations.keys():
                try:
                    existing_numbers.append(int(name.split()[-1]))
                except (ValueError, IndexError):
                    continue
            next_number = 1
            while next_number in existing_numbers:
                next_number += 1
            new_title = f"Conversation {next_number}"
            convs = dict(st.session_state.conversations)
            convs[new_title] = []
            st.session_state.conversations = convs
            st.session_state.active_conversation = new_title

        conversation_names = list(st.session_state.conversations.keys())
        if conversation_names:
            for conversation_name in conversation_names:
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(
                        conversation_name,
                        key=f"select_{conversation_name}",
                        use_container_width=True,
                    ):
                        st.session_state.active_conversation = conversation_name
                with col2:
                    if st.button("🗑", key=f"delete_{conversation_name}", use_container_width=True):
                        convs = dict(st.session_state.conversations)
                        convs.pop(conversation_name, None)
                        st.session_state.conversations = convs
                        if st.session_state.active_conversation == conversation_name:
                            st.session_state.active_conversation = None
                        save_chat_history(st.session_state.current_user, st.session_state.conversations)
                        st.rerun()
        else:
            st.info("No conversations yet. Start a new one.")
            st.session_state.active_conversation = None

    if st.session_state.active_conversation:
        conversation_name = st.session_state.active_conversation
        st.caption(f"Active: {conversation_name}")
        messages = st.session_state.conversations[conversation_name]

        chat_container = st.container(height=500)

        with chat_container:
            for i, message in enumerate(messages):
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    if message["role"] == "assistant":
                        if st.button("💾 Remember this", key=f"remember_{conversation_name}_{i}"):
                            fact = message["content"]
                            if i > 0 and messages[i - 1]["role"] == "user":
                                fact = f"Q: {messages[i - 1]['content']}\nA: {message['content']}"
                            with st.spinner("Storing in memory..."):
                                remember(fact)
                            st.success("Stored in memory.")

        if prompt := st.chat_input("Type a message"):
            messages.append({"role": "user", "content": prompt})

            session_id = f"{st.session_state.current_user}_{conversation_name}"
            with st.spinner("Thinking..."):
                response = run_agent(prompt, session_id)

            messages.append({"role": "assistant", "content": response})
            save_chat_history(st.session_state.current_user, st.session_state.conversations)
            st.rerun()