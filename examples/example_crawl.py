from dotenv import load_dotenv
import time
from tech_doc_extractor import TechDocCrawler, CrawlResult
# import pickle
from pathlib import Path
# Load environment variables from .env
load_dotenv()

# Initialize the crawler
crawler = TechDocCrawler()

# Configuration - limit to just one page
domain = "https://docs.firecrawl.dev"
config = {
    'limit': 30,                # Only get one page
    'max_depth': 10,            # Don't follow any links
    'wait_for': 1000,          # Wait 1000ms for content to load
    'only_main_content': True, # Skip headers/footers
    'formats': ['markdown']    # Request markdown format
}

print(f"\nStarting crawl of {domain}")
print("=" * 50)

# Create pickled directory
# pickle_dir = Path("pickled")
# pickle_dir.mkdir(exist_ok=True)

try:
    for result in crawler.crawl_docs(domain, **config):
        if result['status'] == 'processing':
            print(f"\rProcessing...", end='')
        elif result['status'] == 'completed':
            page: CrawlResult = result['page']
            # pickle_name = pickle_dir / page._generate_filename("pkl")
            # with open(pickle_name, "wb") as file:
            #     pickle.dump(page, file)
            print(f"\nFound: {page.title}")
            filepath = page.save_to_file()
            print(f"Saved to: {filepath}")
        elif result['status'] == 'failed':
            print(f"\nError: {result.get('error')}")
            break

except Exception as e:
    print(f"\nCrawl failed: {str(e)}") 