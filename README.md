# Auto Scan Database

This module takes in a set of documents, automatically scans it using the OpenAI api, and then creates a database containing all relevant information for the documents.

I use this for my personal document archive. Because I am very messy and always need to look hours for documents, I want ChatGPT do it for me. These are the steps of my workflow:

1. Get pile of unsorted documents from my messy home
2. For each document: If it's unimportant -> trash; if it's important I'll scan it
3. Take all scans and let ChatGPT categorize them
4. For each scan a informative file name is generated as well as meta file that contains all relevant information
5. A csv / excel is generated for searchability and uploaded to Google drive for backup

Note: Since my documents are almost entirely in German the prompts I've designed are also German

## How to run

To run this code, follow these steps:

0. `conda env create -f environment.yaml` and then `conda activate <env_name>`
1. Ensure you have the OpenAI API key. Add it to the .env file as `OPENAI_API_KEY=<your_api_key>`. You can use the example.env file as a template.
2. Place your scanned documents in the documents directory.
3. If necessary, modify the prompt in prompts/analyze_document.txt.
4. Run the script using Python. In your terminal, navigate to the directory containing main.py and run the command: