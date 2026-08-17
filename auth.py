import json
from pathlib import Path

CREDENTIALS_FILE = Path(__file__).with_name("credentials.json")
CHAT_HISTORY_FILE = Path(__file__).with_name("chat_history.json")


def load_credentials():
    if not CREDENTIALS_FILE.exists():
        return {}

    try:
        return json.loads(CREDENTIALS_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def save_credentials(username, password):
    credentials = load_credentials()
    credentials[username] = password
    CREDENTIALS_FILE.write_text(json.dumps(credentials, indent=2))
    return credentials


def is_admin_login(username, password):
    return username == "admin" and password == "admin123"


def add_user(username, password):
    credentials = load_credentials()
    credentials[username] = password
    CREDENTIALS_FILE.write_text(json.dumps(credentials, indent=2))
    return credentials


def delete_user(username):
    credentials = load_credentials()
    if username in credentials:
        del credentials[username]
        CREDENTIALS_FILE.write_text(json.dumps(credentials, indent=2))
    return credentials


def load_chat_history(username):
    if not CHAT_HISTORY_FILE.exists():
        return {}

    try:
        history = json.loads(CHAT_HISTORY_FILE.read_text())
    except json.JSONDecodeError:
        return {}

    if isinstance(history, list):
        return {"Conversation 1": history}

    if isinstance(history, dict):
        user_history = history.get(username, {})
        if isinstance(user_history, list):
            return {"Conversation 1": user_history}
        if isinstance(user_history, dict):
            return user_history

    return {}


def save_chat_history(username, conversations):
    history = {}
    if CHAT_HISTORY_FILE.exists():
        try:
            history = json.loads(CHAT_HISTORY_FILE.read_text())
        except json.JSONDecodeError:
            history = {}

    history[username] = conversations
    CHAT_HISTORY_FILE.write_text(json.dumps(history, indent=2))
    return history