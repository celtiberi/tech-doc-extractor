# Technical Documentation Extractor

A Python tool that extracts and processes technical documentation from websites using Firecrawl.

## Features

- Extracts documentation content from websites
- Preserves code examples and formatting

## Installation

1. Clone the repository:
```bash
git clone https://github.com/celtiberi/tech-doc-extractor.git
cd tech-doc-extractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Firecrawl API key:
```bash
export FIRECRAWL_API_KEY='your-api-key'
```
Or create a `.env` file with:
```
FIRECRAWL_API_KEY=your-api-key
```

## Usage

Basic usage:
```python
from tech_docs_scraper import TechDocScraper

# Initialize scraper
scraper = TechDocScraper()

# Extract documentation
for result in scraper.extract_docs("https://docs.example.com", file_type='md'):
    if result['status'] == 'completed':
        print("\nExtraction complete.")
```

## Output

Documents are saved to the `docs/` directory with filenames that include:
- Domain name
- Path segments
- URL fragments (if any)
- Unique hash to prevent collisions

## Requirements

- Python 3.7+
- Firecrawl API key
- Required packages (see requirements.txt)

## License

MIT 