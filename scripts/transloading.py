import os
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pprint import pprint
import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from scripts.extraction import main


load_dotenv()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200, chunk_overlap=20, add_start_index=True
)


def load_data():

    loader = CSVLoader(file_path='data/compiled_content.csv', source_column='url')
    print("Data loaded from CSV")
    data = loader.load()
    splits = text_splitter.split_documents(data)
    print("Data split into chunks")

    return splits

def setup_db():
    
    
    if not os.path.exists('data/compiled_content.csv'):
        print("No data found. Running the extraction script first.")
        main()
    
    if not os.path.exists('data/chroma_db'):
        print("Creating new database")
        splits = load_data()
        vdb = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(), persist_directory='data/chroma_db', collection_name='compiled_content')
        print("Database created")
    else:
        print("Database already exists")
        persistent_client = chromadb.PersistentClient(path='data/chroma_db')
        vdb = Chroma(
            client=persistent_client,
            embedding_function=OpenAIEmbeddings(), 
            collection_name='compiled_content'
        )
        print("Database loaded")

        # Get the Chroma collection and count documents
        chroma_collection = persistent_client.get_collection("compiled_content")
        num_docs = chroma_collection.count()
        print(f"Number of documents in the database: {num_docs}")

    return vdb



vdb = setup_db()
retriever = vdb.as_retriever(search_type="similarity", search_kwargs={'k' : 5})

    