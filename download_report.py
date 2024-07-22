import os
import requests
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load the CSV file
df = pd.read_csv('export.csv', sep=';')

print(df.head())

# Function to download a PDF file from a URL
def download_pdf(row):
    url = row['Report URL']
    company_name = row['Company'].replace(' ', '_')  # Replace spaces with underscores
    year = row['Year Published']
    filename = f"reports/{company_name}_{year}.pdf"
    
    # Check if the file already exists
    if os.path.exists(filename):
        return f"File already exists: {filename}"
    
    try:
        # Ensure the directory exists
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        with open(filename, 'wb') as file:
            file.write(response.content)
        return f"Downloaded file to {filename}"
    except requests.RequestException as e:
        return f"Failed to download {url}: {e}"

# Function to iterate over the DataFrame and download the files concurrently
def download_reports_concurrently(df):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_pdf, row) for _, row in df.iterrows()]
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading reports"):
            result = future.result()
            print(result)

# Create the 'reports' directory if it does not exist
if not os.path.exists('reports'):
    os.makedirs('reports')

# Call the function to download the reports concurrently
download_reports_concurrently(df)
