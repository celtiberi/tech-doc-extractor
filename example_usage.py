from dotenv import load_dotenv
from tech_docs_scraper import TechDocScraper, DocumentItem, TechDocSchema
import time

# Load environment variables from .env
load_dotenv()

# Initialize the scraper
scraper = TechDocScraper()

# Start extraction and monitor progress
print("Starting documentation extraction...")
# First extract and save as text
for result in scraper.extract_docs("https://docs.firecrawl.dev/", file_type='md'):
    if result['status'] == 'processing':
        print(f"processing...")
    elif result['status'] == 'completed':
        print("\nExtraction complete.")        
    elif result['status'] == 'failed':
        print(f"\nExtraction failed: {result}")    
    else:
        print(f"\nError: {result}")