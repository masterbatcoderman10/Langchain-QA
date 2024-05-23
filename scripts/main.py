import streamlit as st
from scripts.rag import get_answer, store
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
import uuid
from pprint import pprint

with st.sidebar:
    api_key = st.text_input("OpenAI API Key", type="password")

if not api_key:
    st.warning("Please enter your OpenAI API key in the sidebar.")
    st.stop()

st.title('QA With ChatGPT')

#New conversation
session_id = "123456789"
if "store" not in st.session_state:
    #Agent's history is stored in the session state this is to contextualize the conversation
    st.session_state.store = {
        session_id: InMemoryChatMessageHistory()
    }

    pprint(st.session_state.store)

#Add old messages
for message in st.session_state.store[session_id].messages:
    
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    
    if isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

#Get user input
if prompt := st.chat_input("Type a message!"):
    
    #Paint user message on the screen
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        respnse = st.write_stream(get_answer(prompt, session_id=session_id))
    
    st.session_state.store[session_id] = store[session_id]

