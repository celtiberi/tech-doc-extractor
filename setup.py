from setuptools import setup, find_packages

setup(
    name="tech-doc-extractor",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "firecrawl",
        "python-slugify",
        "python-dotenv",
        "pydantic"
    ],
    python_requires=">=3.7",
) 