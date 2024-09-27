<<<<<<< HEAD
import os
import requests
from bs4 import BeautifulSoup

# Base directory where all SEC filings will be stored
BASE_DIR = 'sec_filings'

# Ensure the base directory exists
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Function to fetch SEC filings and save them in the appropriate directory structure
def get_sec_filings(ticker, form_types):
    base_url = "https://www.sec.gov"
    headers = {
        'User-Agent': 'jjmr86@live.com.mx',
        'Accept-Encoding': 'gzip, deflate',
        'host': 'www.sec.gov'
    }

    # Directory for this ticker's filings
    ticker_dir = os.path.join(BASE_DIR, ticker.capitalize())

    # Ensure the ticker directory exists
    if not os.path.exists(ticker_dir):
        os.makedirs(ticker_dir)

    filings = {}

    for form_type in form_types:
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type={form_type}&count=10&output=atom"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'xml')
            entry = soup.find('entry')  # Find the latest entry

            if entry:
                filing_url = entry.find('link')['href']
                filing_date = entry.find('filing-date').text
                filing_title = entry.find('title').text

                # Access the filing document page
                filing_response = requests.get(filing_url, headers=headers)

                if filing_response.status_code == 200:
                    filing_page_soup = BeautifulSoup(filing_response.text, 'html.parser')
                    document_table = filing_page_soup.find('table', class_='tableFile')

                    if document_table:
                        # Look for the "Complete submission text file" link
                        for row in document_table.find_all('tr'):
                            cells = row.find_all('td')
                            if len(cells) > 2:
                                description = cells[1].text.strip()
                                document_link = cells[2].find('a')['href']

                                if "Complete submission text file" in description:
                                    # Build the full URL
                                    full_document_url = base_url + document_link

                                    # Download the document
                                    document_response = requests.get(full_document_url, headers=headers)

                                    if document_response.status_code == 200:
                                        # Save the file in the ticker's directory
                                        file_name = f"{ticker}_{form_type}_{filing_date}_complete_submission.txt"
                                        file_path = os.path.join(ticker_dir, file_name)

                                        with open(file_path, 'wb') as file:
                                            file.write(document_response.content)

                                        filings[form_type] = file_path
                                        print(f"Downloaded {form_type} to {file_path}")
                                    else:
                                        print(f"Failed to download the document {form_type}. Status code: {document_response.status_code}")
                                    break  # Stop after downloading the complete submission text file
                    else:
                        print(f"Document table not found for {form_type}.")
                else:
                    print(f"Failed to access filing page for {form_type}. Status code: {filing_response.status_code}")
            else:
                print(f"No filings found for {form_type}.")
        else:
            print(f"Failed to fetch data from SEC for {form_type}. Status code: {response.status_code}")

    return filings

# Example Usage:
if __name__ == "__main__":
    ticker = 'eric'  # Example ticker
    form_types = ['10-K', '10-Q', '8-K', 'DEF 14A','20-F','6-K']  # Forms to fetch

    get_sec_filings(ticker, form_types)
=======
import os
import requests
from bs4 import BeautifulSoup

# Base directory where all SEC filings will be stored
BASE_DIR = 'sec_filings'

# Ensure the base directory exists
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Function to fetch SEC filings and save them in the appropriate directory structure
def get_sec_filings(ticker, form_types):
    base_url = "https://www.sec.gov"
    headers = {
        'User-Agent': 'jjmr86@live.com.mx',
        'Accept-Encoding': 'gzip, deflate',
        'host': 'www.sec.gov'
    }

    # Directory for this ticker's filings
    ticker_dir = os.path.join(BASE_DIR, ticker.capitalize())

    # Ensure the ticker directory exists
    if not os.path.exists(ticker_dir):
        os.makedirs(ticker_dir)

    filings = {}

    for form_type in form_types:
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type={form_type}&count=10&output=atom"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'xml')
            entry = soup.find('entry')  # Find the latest entry

            if entry:
                filing_url = entry.find('link')['href']
                filing_date = entry.find('filing-date').text
                filing_title = entry.find('title').text

                # Access the filing document page
                filing_response = requests.get(filing_url, headers=headers)

                if filing_response.status_code == 200:
                    filing_page_soup = BeautifulSoup(filing_response.text, 'html.parser')
                    document_table = filing_page_soup.find('table', class_='tableFile')

                    if document_table:
                        # Look for the "Complete submission text file" link
                        for row in document_table.find_all('tr'):
                            cells = row.find_all('td')
                            if len(cells) > 2:
                                description = cells[1].text.strip()
                                document_link = cells[2].find('a')['href']

                                if "Complete submission text file" in description:
                                    # Build the full URL
                                    full_document_url = base_url + document_link

                                    # Download the document
                                    document_response = requests.get(full_document_url, headers=headers)

                                    if document_response.status_code == 200:
                                        # Save the file in the ticker's directory
                                        file_name = f"{ticker}_{form_type}_{filing_date}_complete_submission.txt"
                                        file_path = os.path.join(ticker_dir, file_name)

                                        with open(file_path, 'wb') as file:
                                            file.write(document_response.content)

                                        filings[form_type] = file_path
                                        print(f"Downloaded {form_type} to {file_path}")
                                    else:
                                        print(f"Failed to download the document {form_type}. Status code: {document_response.status_code}")
                                    break  # Stop after downloading the complete submission text file
                    else:
                        print(f"Document table not found for {form_type}.")
                else:
                    print(f"Failed to access filing page for {form_type}. Status code: {filing_response.status_code}")
            else:
                print(f"No filings found for {form_type}.")
        else:
            print(f"Failed to fetch data from SEC for {form_type}. Status code: {response.status_code}")

    return filings

# Example Usage:
if __name__ == "__main__":
    ticker = 'eric'  # Example ticker
    form_types = ['10-K', '10-Q', '8-K', 'DEF 14A','20-F','6-K']  # Forms to fetch

    get_sec_filings(ticker, form_types)
>>>>>>> dbb4482 (first commit)
