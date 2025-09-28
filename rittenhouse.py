import os
import re
from textblob import TextBlob
from collections import Counter
import secDBFetch
import logging
import json
from datetime import datetime, timedelta

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Define keyword categories
strategic_keywords = ['growth', 'innovation', 'vision', 'strategy', 'expansion', 'development', 'future', 'opportunity', 'direction', 'goals']
financial_keywords = ['revenue', 'profit', 'loss', 'investment', 'performance', 'earnings', 'margin', 'cost', 'budget', 'capital', 'assets', 'liabilities','inflation']
leadership_keywords = ['leadership', 'management', 'team', 'culture', 'development', 'strategy', 'efficiency', 'talent', 'motivation', 'governance']
risk_management_keywords = ['tariffs','risk', 'compliance', 'challenges', 'mitigation', 'uncertainty', 'contingency', 'safeguard', 'threat', 'lawsuit','litigation']
operational_excellence_keywords = ['efficiency', 'process', 'improvement', 'quality', 'productivity', 'benchmark', 'optimization', 'execution', 'operations', 'systems']
customer_market_keywords = ['customer', 'market', 'demand', 'engagement', 'satisfaction', 'segmentation', 'trends', 'positioning', 'brand', 'service']
technology_innovation_keywords = ['technology', 'digital', 'innovation', 'disruption', 'tools', 'platforms', 'automation', 'advancement', 'research', 'development',' AI ','gpt']

#define the form types to fetch the files if needed
form_types = ['10-K', '10-Q', '8-K', 'DEF 14A','20-F','6-K'] 

# Function to load and preprocess text files
def load_and_preprocess(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        
    # Remove unwanted characters, HTML tags, and excessive whitespace
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with a single space
    text = re.sub(r'[\r\n]+', ' ', text)  # Remove newlines
    return text

# Function to perform sentiment analysis using TextBlob
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity,2)  # Ranges from -1 (negative) to 1 (positive)
    subjectivity = round(blob.sentiment.subjectivity, 2)  # Ranges from 0 (objective) to 1 (subjective)
    return polarity, subjectivity

# Function to perform keyword analysis across multiple categories
def analyze_keywords(text):
    categories = {
        'Strategic': strategic_keywords,
        'Financial': financial_keywords,
        'Leadership': leadership_keywords,
        'Risk Management': risk_management_keywords,
        'Operational Excellence': operational_excellence_keywords,
        'Customer & Market': customer_market_keywords,
        'Technology & Innovation': technology_innovation_keywords
    }
    
    text = text.lower()  # Convert to lowercase for uniformity
    words = re.findall(r'\b\w+\b', text)
    word_counts = Counter(words)
    
    keyword_counts = {}
    for category, keywords in categories.items():
        keyword_counts[category] = {keyword: word_counts[keyword] for keyword in keywords}
    
    return keyword_counts

# Function to generate Rittenhouse framework analysis report for a single file
def rittenhouse_analysis(file_path):
    print(f"Analyzing file: {file_path}")
    
    # Load and preprocess the text
    text = load_and_preprocess(file_path)
    
    # Perform sentiment analysis
    polarity, subjectivity = analyze_sentiment(text)
    
    # Perform keyword analysis
    keyword_counts = analyze_keywords(text)
    
    # Generate report for the individual file
    report = {
        'File': file_path,
        'Sentiment Polarity': polarity,
        'Sentiment Subjectivity': subjectivity,
        'Keyword Counts': keyword_counts
    }
    
    return report

# Function to save the analysis report
def save_analysis_report(ticker_dir, ticker, report):
    today = datetime.today().strftime('%Y-%m-%d')
    report_file = os.path.join(ticker_dir, f"{ticker.capitalize()}_analysis_{today}.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)

# Function to check if a new analysis is needed and return the most recent analysis if not
def is_new_analysis_needed(ticker_dir):
    three_months_ago = datetime.now() - timedelta(days=90)
    most_recent_report = None
    for file_name in os.listdir(ticker_dir):
        if file_name.endswith('.json'):
            file_date_str = re.findall(r'\d{4}-\d{2}-\d{2}', file_name)
            if file_date_str:
                file_date = datetime.strptime(file_date_str[0], '%Y-%m-%d')
                if file_date > three_months_ago:
                    # Load the most recent analysis report
                    with open(os.path.join(ticker_dir, file_name), 'r', encoding='utf-8') as f:
                        most_recent_report = json.load(f)
                    return False, most_recent_report
    return True, None

# Function to analyze all text files for a specific ticker
def analyze_ticker(directory, ticker):
    reports = []
    ticker_dir = os.path.join(directory, ticker.capitalize())
    
    if not os.path.exists(ticker_dir):
        logging.warning(f"Directory for ticker '{ticker}' not found. Creating folder...")
        os.makedirs(ticker_dir)
        secDBFetch.get_sec_filings(ticker=ticker, form_types=form_types)
    
    # Check if any .txt files are older than 3 months and delete them
    three_months_ago = datetime.now() - timedelta(days=90)
    txt_files_exist = False
    
    for file_name in os.listdir(ticker_dir):
        if file_name.endswith('.txt'):
            file_path = os.path.join(ticker_dir, file_name)
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mod_time < three_months_ago:
                logging.info(f"Deleting outdated file: {file_name}")
                os.remove(file_path)
            else:
                txt_files_exist = True
    
    # Fetch new data if no recent .txt files are left
    if not txt_files_exist or not os.listdir(ticker_dir):
        logging.warning(f"No recent files for '{ticker}' found. Fetching data...")
        secDBFetch.get_sec_filings(ticker=ticker, form_types=form_types)
    
    needs_analysis, existing_report = is_new_analysis_needed(ticker_dir)
    
    if not needs_analysis:
        logging.info(f"Analysis for ticker '{ticker}' is up to date.")
        return existing_report  # Return the most recent analysis if no new analysis is needed
    
    for file_name in os.listdir(ticker_dir):
        if file_name.endswith('.txt'):
            file_path = os.path.join(ticker_dir, file_name)
            report = rittenhouse_analysis(file_path)
            reports.append(report)
    
    if reports:
        save_analysis_report(ticker_dir, ticker, reports)
        print(f"Saved analysis report for ticker {ticker}\n")
    
    return reports

# Example function call
if __name__ == "__main__":
    directory = 'sec_filings'  # Root directory where ticker folders are stored
    ticker = 'pltr'  # Example ticker

    reports = analyze_ticker(directory, ticker.capitalize())
    
    # Display the analysis results
    if isinstance(reports, list):
        for report in reports:
            print(f"\nAnalysis Report for {report['File']}:\n")
            print(f"Sentiment Polarity: {report['Sentiment Polarity']:.2f}")
            print(f"Sentiment Subjectivity: {report['Sentiment Subjectivity']:.2f}")
            print("Keyword Counts by Category:")
            for category, keywords in report['Keyword Counts'].items():
                print(f"  {category}:")
                for keyword, count in keywords.items():
                    print(f"    {keyword.strip()}: {count}")
    else:
        print(f"\nUsing Existing Report:\n")
        for report in reports:
            print(f"\nAnalysis Report for {report['File']}:\n")
            print(f"Sentiment Polarity: {report['Sentiment Polarity']:.2f}")
            print(f"Sentiment Subjectivity: {report['Sentiment Subjectivity']:.2f}")
            print("Keyword Counts by Category:")
            for category, keywords in report['Keyword Counts'].items():
                print(f"  {category}:")
                for keyword, count in keywords.items():
                    print(f"    {keyword.strip()}: {count}")