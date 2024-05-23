import os
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pprint import pprint
import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from scripts.extraction import *
import pandas as pd

load_dotenv()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200, chunk_overlap=20, add_start_index=True
)


def load_splits(file_path: str = 'data/compiled_content.csv'):

    loader = CSVLoader(file_path=file_path, source_column='url')
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
        splits = load_splits()
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

def post_setup(vdb: Chroma):

    #load template file
    file = 'data/Template.xlsx'
    template = load_data(file)

    #load content file
    content_file = 'data/compiled_content.csv'
    content = load_data(content_file)

    #check if both files have same number of rows
    if len(template) > len(content):
        print("Template and content files do not have the same number of rows - You must have added new URLs to the template file")
        #extract content for new URLs
        extra_subset  = template.loc[~template['url'].isin(content['url'])]
        # Extract the URLs from the data
        urls = get_urls_from_file(extra_subset)
        print(f"URLs extracted: {len(urls['article_urls'])} article URLs, {len(urls['youtube_urls'])} YouTube URLs.")
        # Extract the content from the URLs
        new_content = compile_text_content(urls)
        print(f"URL content extracted.")

        extra_subset['content_from_url'] = extra_subset['url'].map(new_content)
        #append new content to the content file
        content = pd.concat([content, extra_subset])

        content.to_csv('data/compiled_content.csv', index=False)

        extra_subset.to_csv('data/temp.csv', index=False)
        new_splits = load_splits('data/temp.csv')

        vdb.add_documents(new_splits)
        print("New content added to the database")
        os.remove('data/temp.csv')
    else:
        print("Template and content files have the same number of rows")
        print("No new content to add to the database")





vdb = setup_db()
post_setup(vdb)
retriever = vdb.as_retriever(search_type="similarity", search_kwargs={'k' : 5})

    