import pytest
from tech_doc_extractor import CrawlResult
import pickle
from pathlib import Path

@pytest.fixture
def result() -> CrawlResult:
    """Load the pickled CrawlResult for testing.
    
    Returns:
        CrawlResult: The loaded crawl result object
    """
    test_dir = Path(__file__).parent
    pkl_path = test_dir.parent / "pickled" / "*.pkl"
    
    # Get most recent pickle file
    pkl_files = sorted(Path().glob(str(pkl_path)), key=lambda p: p.stat().st_mtime)
    if not pkl_files:
        raise FileNotFoundError("No pickle files found in pickled directory")
        
    with open(pkl_files[-1], "rb") as file:
        result = pickle.load(file)
        if not isinstance(result, CrawlResult):
            raise TypeError(f"Pickled object is {type(result)}, expected CrawlResult")
        return result


def test_generate_filename_basic(result: CrawlResult):
    """Test basic filename generation."""
    filename = result._generate_filename("md")
    assert isinstance(filename, str)
    assert filename.endswith(".md")
    assert result.title.lower().replace(' ', '_') in filename

def test_generate_filename_components(result: CrawlResult):
    """Test filename contains expected components."""
    filename = result._generate_filename("md")
    parts = filename.split("_")
    
    # Should have slugified title and hash
    assert len(parts) >= 2
    assert parts[-1].endswith(".md")
    assert len(parts[-2]) == 8  # MD5 hash length 