import streamlit as st
import boto3
import json
from askNJUINava import run_askNJUINava
import watchtower
from datetime import datetime

secret_name = "bedrock_api"
region_name = "us-east-1"

title = "NJ UI Confluence Chat"
st.set_page_config(page_title=title, page_icon=None)
st.sidebar.title(title)

cloudwatch_handler = watchtower.CloudWatchLogHandler(
    boto3_session=boto3.Session(region_name=region_name),
    log_group="nj-ui-ec2-streamlit-bedrock",
    stream_name=f"app-logs-{datetime.now().strftime('%Y%m%d')}",
)


def show_header():
    st.title(title)


def get_secrets(secret, region):
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret)
    password = json.loads(response["SecretString"])["BEDROCK_ACCESS_PASSWORD"]
    knowledge_base_id = json.loads(response["SecretString"])["BEDROCK_KB_ID"]
    return password, knowledge_base_id


def login_page(stored_password):
    st.subheader("Login Page")
    password_input = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if password_input == stored_password:
            st.session_state["logged_in"] = True
            st.rerun()

        else:
            st.error("That is not correct. Please try again.")


def main():
    # Initialize session state variable
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "kb" not in st.session_state:
        st.session_state["kb"] = None

    if not st.session_state["logged_in"]:
        password, kb = get_secrets(secret_name, region_name)
        st.session_state["kb"] = kb
        login_page(password)
    else:
        with st.sidebar:
            if st.button("Logout"):
                st.session_state["logged_in"] = False
                st.rerun()
            if st.button("Clear Session"):
                st.session_state.chat_history.clear()
                st.rerun()
        # User is authenticated, now run Q&A app
        run_askNJUINava(st.session_state["kb"], title, cloudwatch_handler)


if __name__ == "__main__":
    main()
