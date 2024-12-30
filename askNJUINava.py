# askNJUINava.py

import boto3
import streamlit as st

bedrockClient = boto3.client("bedrock-agent-runtime", "us-east-1")


def get_answers(questions, knowledge_base_id):
    try:
        knowledge_base_response = bedrockClient.retrieve_and_generate(
            input={"text": questions},
            retrieveAndGenerateConfiguration={
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": knowledge_base_id,
                    "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
                },
                "type": "KNOWLEDGE_BASE",
            },
        )
        return knowledge_base_response
    except bedrockClient.exceptions.ThrottlingException:
        st.error("We’re receiving too many requests. Please try again later.")
        return {}
    except Exception as e:
        st.error(f"Error retrieving answer: {str(e)}")
        return {}


def run_askNJUINava(knowledge_base_id):
    """
    This function runs the main app to interact with the Bedrock RAG.
    Call it from `main.py` after the user is authenticated.
    """
    st.subheader("NJ UI RAG using Amazon Bedrock", divider="blue")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display all previous queries
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["text"], unsafe_allow_html=True)

    # get a new question
    questions = st.chat_input("What can I try to answer?")
    if questions:
        # Show user's query
        with st.chat_message("user"):
            st.markdown(questions)
        st.session_state.chat_history.append({"role": "user", "text": questions})

        # Retrieve answer
        response = get_answers(questions, knowledge_base_id)
        if response:
            answer = response["output"]["text"]

            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "text": answer})

            # Display citations (if any)
            if (
                "citations" in response
                and response["citations"]
                and "retrievedReferences" in response["citations"][0]
            ):
                references = response["citations"][0].get("retrievedReferences", [])
                for ref in references:
                    # context = ref['content']['text']
                    doc_url = ref["location"]["confluenceLocation"]["url"]

                    # st.markdown(f"<span style='color:#FFDA33'>Context used: </span>{context}", unsafe_allow_html=True)
                    st.markdown(
                        f"<span style='color:#FFDA33'>Source Document: </span>{doc_url}",
                        unsafe_allow_html=True,
                    )
                    # st.session_state.chat_history.append({"role": 'assistant', "text": context})
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "text": f"<span style='color:#FFDA33'>Source Document: </span>{doc_url}",
                        }
                    )
            else:
                st.markdown(
                    f"<span style='color:red'>No Context</span>", unsafe_allow_html=True
                )
