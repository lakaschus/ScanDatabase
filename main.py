"""
Main Script for Document Analysis and Meta Data Generation

This script performs the following steps:
1. Load the scanned document from the specified directory.
2. Analyze the document using the OpenAI GPT model.
3. Generate meta data for the document including type, date, author, recipient,
   title, keywords, summary, entities, language, and page count.
4. Save the meta data as a YAML file in the same directory as the document.
5. Generate an informative file name based on the meta data.
6. Rename the document file with the newly generated informative name.
7. Finally, create a csv and excel file with all the meta data.

Project Structure:
- database/
- documents/
  - <scanned_documents>.pdf
- prompts/
  - analyze_document.txt
  - generate_title.txt
- .env
- .gitignore
- main.py
- README.md

Instructions:
1. Ensure you have the OpenAI API key in the .env file as
   OPENAI_API_KEY=<your_api_key>.
2. Place your scanned documents in the 'documents' directory.
3. Modify the prompts in 'prompts/analyze_document.txt' and
   'prompts/generate_title.txt' as necessary.
4. Run the script: python main.py
"""

import os
import openai
import yaml
import csv
import pandas as pd
from datetime import datetime
import base64
from dotenv import load_dotenv
import re
import shutil
import time

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


# Function to load prompts from files
def load_prompt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Function to analyze the document and extract meta data
def analyze_document(file_path, prompt):
    # create image url
    with open(file_path, "rb") as file:
        image_url = f"data:image/jpeg;base64,{base64.b64encode(file.read()).decode()}"  # noqa: E501

    # error most likely request limit, first wait 5 seconds
    time.sleep(5)

    # then try
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error: {e}")
        # try again
        time.sleep(15)
        return analyze_document(file_path, prompt)


# Function to generate a filename based on meta data
def generate_filename(meta_data):
    # <dokumententyp>_<autor>_<datum>_<titel>.jpg
    # if any of the fields are missing, use "unbekannt"
    string = ""
    string += str(meta_data.get("document_type", "unbekannt")) + "_"
    string += str(meta_data.get("author", "unbekannt")) + "_"
    string += str(meta_data.get("date", "unbekannt")) + "_"
    string += str(meta_data.get("title", "unbekannt"))
    # Make sure that the filename is a valid filename
    string = re.sub(r"[^\w\s-]", "", string)
    return string + ".jpg"


# Function to create meta data file
def create_meta_file(info, original_filename, renamed_filename):
    meta_data = {
        "original_filename": original_filename,
        "renamed_filename": renamed_filename,
        "document_type": info["document_type"],
        "date": info["date"],
        "author": info["author"],
        "recipient": info["recipient"],
        "title": info["title"],
        "keywords": info["keywords"],
        "summary": info["summary"],
        "entities": info["entities"],
        "page": info["page_count"],
        "creation_date": datetime.now().strftime("%Y-%m-%d"),
    }
    return meta_data


# Function to save meta data to a YAML file
def save_meta_file(meta_data, meta_file_path):
    # Save json file as yaml
    with open(meta_file_path, "w", encoding="utf-8") as file:
        yaml.dump(meta_data, file, default_flow_style=False,
                  allow_unicode=True)


# Function to save meta data to CSV and Excel files
def save_meta_data_to_csv_excel(meta_data_list, csv_path, excel_path):
    keys = meta_data_list[0].keys()
    with open(csv_path, "w", newline="", encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(meta_data_list)

    df = pd.DataFrame(meta_data_list)
    df.to_excel(excel_path, index=False)


def preprocess_yaml(yaml_string):
    return re.sub(r'(?<=: )([^"\n]*: [^"\n]*)', r'"\1"', yaml_string)


# Main function to process documents
def process_documents():
    # First, make sure that database/meta_files and database/renamed_files exist but are empty
    if not os.path.exists('database/meta_files'):
        os.makedirs('database/meta_files')
    else:
        for file in os.listdir('database/meta_files'):
            os.remove(os.path.join('database/meta_files', file))
    if not os.path.exists('database/renamed_files'):
        os.makedirs('database/renamed_files')
    else:
        for file in os.listdir('database/renamed_files'):
            os.remove(os.path.join('database/renamed_files', file))

    document_dir = "documents"
    analyze_prompt_path = "prompts/analyze_document.txt"

    analyze_prompt = load_prompt(analyze_prompt_path)

    meta_data_list = []

    for filename in os.listdir(document_dir):
        if (
            filename.endswith(".pdf")
            or filename.endswith(".jpg")
            or filename.endswith(".jpeg")
        ):
            file_path = os.path.join(document_dir, filename)
            print(f"Processing {filename}...")

            # Analyze the document to get meta data
            meta_info = analyze_document(file_path, analyze_prompt)

            # Get content between "```yaml" and "```" to extract meta data
            meta_info = meta_info.split("```yaml")[1].split("```")[0]
            meta_info = preprocess_yaml(meta_info)
            meta_json = yaml.safe_load(meta_info)

            # Generate new file name
            new_filename = generate_filename(meta_json)

            # Rename the document file
            renamed_file_location = os.path.join('database', 'renamed_files',
                                                 new_filename)
            shutil.copy2(file_path, renamed_file_location)

            # Create meta data file
            meta_file_path = os.path.join('database', 'meta_files',
                                          new_filename.split('.')[0] + ".yaml")
            save_meta_file(meta_json, meta_file_path)

            # Add new file name to meta data
            meta_json["renamed_filename"] = new_filename

            meta_data_list.append(meta_json)

            print(f"Processed {filename}, saved meta file as {meta_file_path}")

    # Save all meta data to CSV and Excel files
    csv_path = "database/meta_data.csv"
    excel_path = "database/meta_data.xlsx"
    save_meta_data_to_csv_excel(meta_data_list, csv_path, excel_path)
    print(f"Meta data saved to {csv_path} and {excel_path}")


if __name__ == "__main__":
    process_documents()
