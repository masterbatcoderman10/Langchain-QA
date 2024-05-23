import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from scripts.transloading import retriever
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

template = """
- Use the following pieces of context to answer the question at the end.
- If you don't know the answer, just say that you don't know, don't try to make up an answer.
- Ensure you provide a detailed and helpful answer.
- Always say "thanks for asking!" at the end of the answer.

{context}

Question: {question}

Helpful Answer:"""

prompt = PromptTemplate.from_template(template)

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

for chunk in rag_chain.stream("What is electronic waste?"):
    print(chunk, end="", flush=True)