import streamlit as st
from scripts.rag import get_answer, store
import uuid

st.title('QA With ChatGPT')

#New conversation
if "store" not in st.session_state:
    #Agent's history is stored in the session state this is to contextualize the conversation
    st.session_state.store = {}

#Get user input
if prompt := st.chat_input("Type a message!"):
    
    #Paint user message on the screen
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        respnse = st.write_stream(get_answer(prompt, session_id=uuid.uuid4().hex))
    
    print(store)
