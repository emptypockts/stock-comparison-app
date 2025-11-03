from bs4 import BeautifulSoup
from lxml import etree
import re 

def clean_edgar_text(content: str) -> str:
    """
    Extracts and cleans the text from only the first document (<DOCUMENT>...</DOCUMENT>)
    in an SEC submission file, excluding embedded image/base64 content.
    """
    
    match = re.search(r"<DOCUMENT>(.*?)</DOCUMENT>", content, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("No <DOCUMENT> section found.")
    first_doc = match.group(1)

    
    first_doc = re.sub(r"begin [\s\S]+?end", "", first_doc, flags=re.IGNORECASE)

    
    soup = BeautifulSoup(first_doc, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    
    text = re.sub(r"\s+", " ", text)

    return text.strip()