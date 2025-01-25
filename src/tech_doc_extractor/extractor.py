import os
import logging
from typing import Dict, Any, Optional, Generator, List
from urllib.parse import urlparse, unquote
from pathlib import Path

from firecrawl import FirecrawlApp
from pydantic import BaseModel
from slugify import slugify
from docling.document_converter import DocumentConverter

# Configure Logging
logging.basicConfig(level=logging.INFO)

class DocumentItem(BaseModel):
    title: str
    content: str
    url: str
    filename: Optional[str] = None

class TechDocSchema(BaseModel):
    documentation: List[DocumentItem]

class TechDocExtractor:
    """Extracts technical documentation content using Firecrawl."""
    
    DEFAULT_FILE_TYPE = "txt"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("Firecrawl API key must be provided or set as FIRECRAWL_API_KEY environment variable")
            
        self.firecrawl = FirecrawlApp(api_key=self.api_key)
        self.converter = DocumentConverter()

    @staticmethod
    def _validate_url(url: str) -> None:
        """Validate URL format."""
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL format: {url}")

    def extract_docs(self, domain: str, file_type: str = DEFAULT_FILE_TYPE) -> Generator[Dict[str, Any], None, None]:
        """Extract documentation and optionally save as files."""
        self._validate_url(domain)
        domain_with_wildcard = f"{domain.rstrip('/')}/*"

        extract_params = {
            'prompt': """            
            Extract all documentation pages, capturing the full content, title, and URL 
            of each page. Do not loose content or code examples.
            Do not break pages into multiple documents. Keep the page intact.          
            """,
            'schema': TechDocSchema
        }
        
        try:
            extract_job = self.firecrawl.async_extract([domain_with_wildcard], extract_params)
            job_id = extract_job['id']
            
            while True:
                status = self.firecrawl.get_extract_status(job_id)
                if status.get('status') == 'completed':  # Use `.get()` to avoid KeyError
                    docs = self._process_extracted_docs(status.get('data', {}).get('documentation', []), file_type)
                    yield {'status': 'completed', 'documentation': docs}
                    break
                else:
                    yield status                    
        except (KeyError, AttributeError) as e:
            logging.error(f"Error extracting from {domain}: {e}")
            raise RuntimeError(f"Error extracting from {domain}: {e}")

    def _process_extracted_docs(self, extracted_docs: List[Dict[str, str]], file_type: str) -> List[DocumentItem]:
        """Process extracted documents, optionally saving them."""
        processed_docs = []
        
        for doc in extracted_docs:
            doc_data = doc.copy()  # Avoid modifying the original dictionary
            doc_data["filename"] = url_to_filename(doc_data["url"], file_type)  # Directly modify dictionary
            
            document_item = DocumentItem(**doc_data)  # No explicit filename parameter
            document_item.content = doc_data["url"] + '\n\n' + document_item.content
            save_doc(document_item, doc_data["filename"])
            
            processed_docs.append(document_item)
        
        return processed_docs

# Helper Functions
import hashlib

def url_to_filename(url: str, file_type: str = "txt") -> str:
    """Convert URL to a safe and unique filename, including fragments."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace(".", "_")  # Replace dots for safety
    path = unquote(parsed.path.rstrip('/')) or 'index'
    fragment = unquote(parsed.fragment)  # Include fragment for uniqueness

    # Append fragment if it exists
    if fragment:
        path = f"{path}_{fragment}"  # Ensures fragment is represented in filename

    # Generate a short hash of the full URL (including query+fragment) for uniqueness
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]  # Short 8-char hash

    # Slugify to create a safe filename
    filename = slugify(path, separator='_', max_length=80, word_boundary=True)

    # Combine domain, slugified path, and hash for uniqueness
    return f"{domain}_{filename}_{url_hash}.{file_type}"

def save_doc(doc: DocumentItem, filename: str, output_dir: str = "docs") -> None:
    """Save a document to a file."""
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    filepath = output_path / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with filepath.open('w', encoding='utf-8') as f:
        f.write(f"# {doc.title}\n\n{doc.content}")

    logging.info(f"Saved document to: {filepath}")