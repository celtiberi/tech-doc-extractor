import os
import time
import logging
from typing import Dict, Any, Optional, Generator, List
from urllib.parse import urlparse
from pathlib import Path
import itertools
import hashlib
from urllib.parse import unquote
from slugify import slugify

from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field

# Configure Logging
logging.basicConfig(level=logging.INFO)

class CrawlResult(BaseModel):
    """Single page crawl result.
    
    Attributes:
        title: Page title from metadata
        url: Source URL of the page
        markdown: The page content in markdown format
        html: The page content in HTML format
        description: Page description if available
        language: Content language (e.g., 'en')
        status_code: HTTP status code
        metadata: Additional page metadata
    """
    title: str = Field(..., description="Page title")
    url: str = Field(..., description="Source URL of the page")
    markdown: Optional[str] = Field(None, description="Page content in markdown format")
    html: Optional[str] = Field(None, description="Page content in HTML format")
    description: Optional[str] = Field(None, description="Page description")
    language: str = Field('en', description="Content language")
    status_code: int = Field(200, description="HTTP status code")
    metadata: Dict[str, Any] = Field(..., description="Additional page metadata")

    @classmethod
    def from_crawl_response(cls, page: Dict[str, Any]) -> "CrawlResult":
        """Create CrawlResult from Firecrawl page response."""
        metadata = page.get('metadata', {})
        return cls(
            title=metadata.get('title', ''),
            url=metadata.get('sourceURL', ''),
            markdown=page.get('markdown', ''),
            html=page.get('html', ''),
            description=metadata.get('description'),
            language=metadata.get('language', 'en'),
            status_code=metadata.get('statusCode', 200),
            metadata=metadata
        )

    def save_to_file(self, output_dir: str = "docs") -> Path:
        """Save the document to a file.
        
        Saves as markdown if available, falls back to HTML.
        Raises ValueError if neither format is available.
        """
        if not self.markdown and not self.html:
            raise ValueError("No content available to save")

        # Determine format
        is_markdown = bool(self.markdown)
        extension = "md" if is_markdown else "html"
        content = self.markdown if is_markdown else self.html

        # Create directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Base filename without extension
        base_filename = self._generate_filename(extension).rsplit('.', 1)[0]

        # Generate unique filename with counter
        for counter in itertools.count():
            filename = f"{base_filename}_{counter}.{extension}" if counter else f"{base_filename}.{extension}"
            filepath = output_path / filename
            if not filepath.exists():
                break

        # Write content
        with filepath.open('w', encoding='utf-8') as f:
            f.write(f"# {self.title}\n\n" if is_markdown else f"<h1>{self.title}</h1>\n")
            f.write(f"URL: {self.url}\n\n" if is_markdown else f"<p>URL: {self.url}</p>\n")
            f.write(content or '')

        logging.info(f"Saved document to: {filepath}")
        return filepath

    def _generate_filename(self, extension: str) -> str:
        """Generate a safe filename from title."""
        safe_title = slugify(self.title, separator='_', max_length=80, word_boundary=True)
        return f"{safe_title}.{extension}"

class TechDocCrawler:
    """Crawls technical documentation using Firecrawl."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("Firecrawl API key must be provided or set as FIRECRAWL_API_KEY environment variable")
            
        self.firecrawl = FirecrawlApp(api_key=self.api_key)

    @staticmethod
    def _validate_url(url: str) -> None:
        """Validate URL format."""
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL format: {url}")

    def crawl_docs(
        self, 
        domain: str, 
        limit: int = 100,
        max_depth: int = 1,
        poll_interval: int = 30,
        wait_for: int = 1000,
        only_main_content: bool = True,
        formats: List[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Crawl documentation site and yield results."""
        if formats is None:
            formats = ['markdown']
        try:
            crawl_job = self.firecrawl.crawl_url(
                domain,
                params={
                    'limit': limit,
                    'maxDepth': max_depth,
                    'scrapeOptions': {
                        'formats': formats,
                        'waitFor': wait_for,
                        'onlyMainContent': only_main_content
                    }
                },
                poll_interval=poll_interval
            )
            
            logging.info(f"Crawl job response: {crawl_job}")
            
            # Handle direct completion
            if crawl_job.get('status') == 'completed':
                for page in crawl_job.get('data', []):
                    yield {
                        'status': 'completed',
                        'page': CrawlResult.from_crawl_response(page)
                    }
                return
            
            # Otherwise check job status
            if 'id' not in crawl_job:
                raise ValueError(f"Invalid crawl job response: {crawl_job}")
            
            job_id = crawl_job['id']
            
            while True:
                status = self.firecrawl.check_crawl_status(job_id)
                
                if status.get('status') == 'completed':
                    # Process current chunk
                    for page in status.get('data', []):
                        yield {
                            'status': 'completed',
                            'page': CrawlResult.from_crawl_response(page)
                        }
                    
                    # Handle pagination
                    next_url = status.get('next')
                    while next_url:
                        logging.info(f"Fetching next chunk from: {next_url}")
                        status = self.firecrawl.get(next_url)
                        for page in status.get('data', []):
                            yield {
                                'status': 'completed',
                                'page': CrawlResult.from_crawl_response(page)
                            }
                        next_url = status.get('next')
                    break
                elif status.get('status') == 'failed':
                    yield {'status': 'failed', 'error': status.get('error')}
                    break
                else:
                    yield {
                        'status': status.get('status', 'processing'),
                        'total': status.get('total', 0),
                        'completed': status.get('completed', 0),
                        'credits_used': status.get('creditsUsed', 0)
                    }
                    time.sleep(poll_interval)
                    
        except Exception as e:
            logging.error(f"Error crawling {domain}: {e}")
            raise RuntimeError(f"Error crawling {domain}: {e}")
