import streamlit as st
from src.chatbot import get_chat_engine

st.set_page_config(page_title="PickMe AI Assistant", page_icon="🤖")

st.title("PickMe AI Assistant")
st.info("You can ask any questions on PickMe")

@st.cache_resource
def init_chat_engine():
    """Initializes the chat engine and caches it."""
    with st.spinner("Initializing chat engine..."):
        return get_chat_engine()

chat_engine = init_chat_engine()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.stream_chat(prompt)
            response_str = ""
            response_container = st.empty()
            for token in response.response_gen:
                response_str += token
                response_container.markdown(response_str)
            
            st.session_state.messages.append(
                {"role": "assistant", "content": response_str}
            )


