# QA Chatbot using Langchain and Streamlit

This is a simple QA chatbot that uses Langchain and Streamlit to answer questions based on the text content consumed from a spreadsheet.

## Installation

Once the repository is cloned, go ahead and create a virtual environment and install the dependencies.

This can be done in 2 ways:

1. Running the following commands in the terminal/command prompt (Both Windows and Mac):

```bash
$ python3 -m venv venv
$ source venv/bin/activate # On Mac
$ venv\Scripts\activate # On Windows
$ pip install -r requirements.txt # On Mac/Linux
$ pip install -r requirements_w.txt # On Windows
```

2. Using the `Makefile` (On mac, linux and WSL):

```bash
$ make
# activate the virtual environment
$ source venv/bin/activate
```

If you are using Windows, you can use the `Makefile` by installing `make` from [here](http://gnuwin32.sourceforge.net/packages/make.htm) and running the command outlined in step 2.

If you have used Step 1, please create a .env file in the root directory:

```bash
$ echo OPENAI_API_KEY= > .env
```

Then add your OpenAI API key to the .env file.


## Usage

Once the virtual environment is installed and activated, you can run the following command to start the Streamlit app:

```bash
$ python -m streamlit run scripts/main.py
```

Starting the app for the first time will open the application in your default browser. After an initial start the data will be extracted if not already done and the app will be ready to use.

If the application did not open in your browser, you can copy the URL from the terminal and paste it in your browser. For reference : http://localhost:8501


