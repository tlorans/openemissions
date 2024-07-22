import os
import json
import re
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
client = OpenAI()

assistant = client.beta.assistants.create(
    name="Sustainability Reporting Assistant",
    instructions="You are an expert sustainability analyst. Use the report to answer questions about carbon emissions.",
    tools=[{"type": "file_search"}],
    model="gpt-4o-mini",
)

def is_pdf_readable(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            if len(reader.pages) > 0:
                return True
    except Exception as e:
        print(f"Cannot read {pdf_path}: {e}")
    return False

def extract_json_from_response(response):
    # Find all JSON objects in the response
    json_matches = re.findall(r'\{.*?\}', response, re.DOTALL)
    if not json_matches:
        print("No JSON found in the response.")
        return None

    # Validate and return the first valid JSON object
    for json_str in json_matches:
        try:
            json_data = json.loads(json_str)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e} for string: {json_str}")
    return None

def process_report(pdf_path, json_dir):
    # Create the JSON filename
    json_filename = os.path.join(json_dir, os.path.basename(pdf_path).replace('.pdf', '.json'))

    # Check if the JSON file already exists
    if os.path.exists(json_filename):
        print(f"Skipping {pdf_path} as {json_filename} already exists.")
        return

    # Check if the PDF file is readable
    if not is_pdf_readable(pdf_path):
        print(f"Skipping {pdf_path} as it cannot be read.")
        return

    message_file = client.files.create(
        file=open(pdf_path, "rb"), purpose="assistants"
    )

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content":
            "I need to determine the company's carbon emissions from the provided report. "
            "Please provide the total carbon emissions differentiated by Scope 1, Scope 2, and Scope 3. "
            "The units should be in tons. If any value is expressed in million tons (Mt), convert it to tons. For example, 1 Mt (megaton) should be written as 1,000,000 tons. "
            "Ensure the response is in the following JSON format without any additional text: "
            "{\"Scope 1\": 1000, \"Scope 2\": 2000, \"Scope 3\": 3000}. "
            "Here is the report to analyze:",
            "attachments": [
                {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
            ],
            }
        ]
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please provide the carbon emissions in JSON format."
    )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        assistant_response = None
        for message in messages.data:
            if message.role == 'assistant':
                assistant_response = message.content[0].text.value
                break

        if assistant_response:
            # Extract JSON content from the assistant's response
            emissions_data = extract_json_from_response(assistant_response)
            if emissions_data:
                # Ensure the JSON directory exists
                if not os.path.exists(json_dir):
                    os.makedirs(json_dir)
                # Save the JSON file
                with open(json_filename, 'w') as json_file:
                    json.dump(emissions_data, json_file, indent=4)
                print(f"Response saved as {json_filename}")
            else:
                print(f"No valid JSON found in the assistant's response for {pdf_path}.")
        else:
            print(f"No response from assistant for {pdf_path}.")
    else:
        print(run.status)

# Directory containing the PDF reports
reports_dir = 'reports'
# Directory to save the JSON files
json_dir = 'json_reports'

# Iterate over the PDF files in the directory and process each one
for pdf_file in tqdm(os.listdir(reports_dir), desc="Processing reports"):
    if pdf_file.endswith('.pdf'):
        pdf_path = os.path.join(reports_dir, pdf_file)
        process_report(pdf_path, json_dir)
