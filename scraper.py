import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_amenify():
    print("Scraping Amenify...")
    url = "https://www.amenify.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from main elements
        texts = []
        for tag in ['h1', 'h2', 'h3', 'p', 'li', 'span', 'div']:
            elements = soup.find_all(tag)
            for el in elements:
                text = el.get_text(strip=True)
                if text and len(text) > 20: # Filter out very short strings
                    texts.append(text)
                    
        # Remove duplicates while preserving order
        unique_texts = []
        seen = set()
        for text in texts:
            if text not in seen:
                seen.add(text)
                unique_texts.append(text)
                
        # Save to file
        os.makedirs('data', exist_ok=True)
        with open('data/knowledge_base.txt', 'w', encoding='utf-8') as f:
            for text in unique_texts:
                f.write(text + "\n")
                
        print(f"Successfully extracted {len(unique_texts)} text blocks and saved to data/knowledge_base.txt")
        return True
    except Exception as e:
        print(f"Error scraping website: {e}")
        return False

if __name__ == "__main__":
    scrape_amenify()
