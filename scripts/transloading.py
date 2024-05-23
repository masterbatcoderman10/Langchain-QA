import os
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pprint import pprint
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv


load_dotenv()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200, chunk_overlap=20, add_start_index=True
)


def load_data():

    loader = CSVLoader(file_path='data/compiled_content.csv')
    print("Data loaded from CSV")
    data = loader.load()
    splits = text_splitter.split_documents(data)
    print("Data split into chunks")

    return splits

def setup_db():
    
    if not os.path.exists('data/compiled_content.csv'):
        print("No data found. Please run the extraction script first.")
        return
    elif not os.path.exists('data/chroma_db'):
        print("Creating new database")
        splits = load_data()
        vdb = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(), persist_directory='data/chroma_db')
        print("Database created")
    else:
        print("Database already exists")
        vdb = Chroma(persist_directory='data/chroma_db', embedding=OpenAIEmbeddings())
        print("Database loaded")

    return vdb


if __name__ == '__main__':
    pass

    