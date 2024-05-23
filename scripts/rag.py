import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from scripts.transloading import retriever
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage
from pprint import pprint

### Statefully manage chat history ###
store = {}
load_dotenv()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""

qa_system_prompt = """You are an assistant for question-answering tasks. \
- Use the following pieces of context to answer the question at the end.
- If you don't know the answer, just say that you don't know, don't try to make up an answer.
- Ensure you provide a detailed and helpful answer.
- Always say "thanks for asking!" at the end of the answer.

{context}"""


llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
# prompt for tracking history - subchain
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
# qa prompt
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Subchain that contextualizes the question with the chat history
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(
    history_aware_retriever, question_answer_chain)

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


def get_answer(question: str, session_id: str = None):
    if session_id is None:
        session_id = "abc123"
    # return conversational_rag_chain.invoke(
    #     {"input": question},
    #     config={
    #         "configurable": {"session_id": session_id}
    #     },  # constructs a key "abc123" in `store`.
    # )["answer"]
    for chunk in conversational_rag_chain.stream(
        {"input": question},
        config={"configurable": {"session_id": session_id}},
    ):
        if 'answer' in chunk:
            yield chunk['answer']
        
# for chunk in get_answer("What is electronic waste?"):
#     print(chunk, end="", flush=True)
# print("\n")
# for chunk in get_answer("How to safely recycle it?"):
#     print(chunk, end="", flush=True)

# pprint(store)


# rag_chain = (
#     {"context": retriever | format_docs, "question": RunnablePassthrough()}
#     | prompt
#     | llm
#     | StrOutputParser()
# )
# for chunk in rag_chain.stream("What is electronic waste?"):
#     print(chunk, end="", flush=True)
