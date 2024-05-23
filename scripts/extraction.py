import pathlib
import os
from newspaper import Article, Config
from newspaper.article import ArticleException
import pandas as pd
from pprint import pprint
from youtube_transcript_api import YouTubeTranscriptApi


def load_data(file: str):

    """
    Load data from a CSV or Excel file into a pandas dataframe.

    Args:
        file (str): The path to the CSV or Excel file.
    
    Returns:
        df (pd.DataFrame): A pandas dataframe containing the data from the file.
    """

    # check extension xlsx or csv
    extension = os.path.splitext(file)[1]
    if extension == '.csv':
        df = pd.read_csv(file)
    elif extension == '.xlsx':
        df = pd.read_excel(file)
    else:
        raise ValueError(
            'File extension not supported. Please provide a CSV or XLSX file.')

    # normalize the column names
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    return df


def get_urls_from_file(df: pd.DataFrame):
    """
    Extracts the URLs from pandas dataframe.

    Args:
        df (pd.DataFrame): A pandas dataframe containing the URLs.

    Returns:
        dict: A dictionary containing two lists of URLs: 'article_urls' and 'youtube_urls'.
    """
    
    # if youtube is in url separate it
    youtube_urls = df[df['url'].str.contains('youtube')]['url'].tolist()
    article_urls = df[~df['url'].str.contains('youtube')]['url'].tolist()

    return {
        'article_urls': article_urls,
        'youtube_urls': youtube_urls
    }




def extract_webpage_content_efficient(url):
    """
    Extracts the main content from a webpage.

    This function uses the Newspaper3k library to download and parse the webpage. 
    It then extracts the main text content from the parsed webpage.

    Args:
        url (str): The URL of the webpage to extract content from.

    Returns:
        str: The main text content of the webpage.
    """
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    print(f"Extracting content from {url}")
    
    try:
        article = Article(url, config=config)
        article.download()
        article.parse()
    except ArticleException as e:
        print(f"Error: {e}")
        return "N/A"

    main_text = article.text
    return main_text


def extract_youtube_transcript(url):
    """
    Extracts the transcript from a YouTube video.

    This function uses the YouTubeTranscriptApi library to extract the transcript of a YouTube video.

    Args:
        url (str): The URL of the YouTube video.

    Returns:
        str: The transcript of the YouTube video.
    """
    print(f"Extracting transcript from {url}")
    video_id  = url.split('=')[1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return transcript

def compile_text_content(urls: dict):
    article_urls = urls['article_urls']
    youtube_urls = urls['youtube_urls']

    content_dict = {}

    for url in article_urls:
        content = extract_webpage_content_efficient(url)
        content_dict[url] = content

    for url in youtube_urls:
        transcript = extract_youtube_transcript(url)
        transcript_text = ' '.join([line['text'] for line in transcript])
        content_dict[url] = transcript_text

    return content_dict

def upload_text_contect(file: str, content: dict):

    df = load_data(file)
    #map urls to content_from_url
    df['content_from_url'] = df['url'].map(content)

    df.to_csv('data/compiled_content.csv', index=False)


    



def main():

    # Load the data from the file
    file = 'data/Template.xlsx'
    df = load_data(file)

    # Extract the URLs from the data
    urls = get_urls_from_file(df)
    print(f"URLs extracted: {len(urls['article_urls'])} article URLs, {len(urls['youtube_urls'])} YouTube URLs.")
    # Extract the content from the URLs
    content = compile_text_content(urls)
    print(f"URL content extracted.")
    # Upload the content back to the file
    upload_text_contect(file, content)

