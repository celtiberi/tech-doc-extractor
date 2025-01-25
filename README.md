# Tech Doc Extractor

A Python tool for crawling and extracting technical documentation using Firecrawl API.

## Features

- Crawls technical documentation sites
- Converts pages to clean markdown format
- Handles pagination and depth control
- (Attempts to) Saves documents with meaningful filenames

## Installation

1. Clone the repository:
```bash
git clone https://github.com/celtiberi/tech-doc-extractor.git
cd tech-doc-extractor
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
```

## Configuration

Set your Firecrawl API key in a `.env` file:
```
FIRECRAWL_API_KEY=your_api_key_here
```

## Usage

Basic usage example:
```python
from tech_doc_extractor import TechDocCrawler

# Initialize crawler
crawler = TechDocCrawler()

# Configuration
config = {
    'limit': 30,                # Maximum pages to crawl
    'max_depth': 10,            # Maximum link depth
    'wait_for': 1000,          # Wait time for JS content (ms)
    'only_main_content': True,  # Skip headers/footers
    'formats': ['markdown']     # Output format
}

# Start crawling
for result in crawler.crawl_docs("https://docs.example.com", **config):
    if result['status'] == 'completed':
        page = result['page']
        print(f"Found: {page.title}")
        filepath = page.save_to_file()
        print(f"Saved to: {filepath}")
```

Documents are saved to the `docs/` directory by default.

## TODO

 - Add support for GitHub repositories and GitHub Pages
 - Need better path filtering
 - Smarter link following rules
 - Domain/subdomain restrictions
 - Content relevance detection
 - Post processing with AI to remove irrelevant content (md-summarizer could work for this)

## Testing

Run tests with pytest:
```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
