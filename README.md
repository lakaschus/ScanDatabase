# Auto Scan Database

This module takes in a set of documents, automatically scans it using the OpenAI api, and then creates a database containing all relevant information for the documents.

I use this for my personal document archive. Because I am very messy and always need to look hours for documents, I want ChatGPT do it for me. These are the steps of my workflow:

1. Get pile of unsorted documents from my messy home
2. For each document: If it's unimportant -> trash; if it's important I'll scan it
3. Take all scans and let ChatGPT categorize them
4. For each scan a informative file name is generated as well as meta file that contains all relevant information
5. A csv / excel is generated for searchability and uploaded to Google drive for backup