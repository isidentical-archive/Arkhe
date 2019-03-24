from pathlib import Path
from setuptools import setup, find_packages

current_dir = Path(__file__).parent.resolve()

with open(current_dir / 'README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="arkhe",
    version="0.2",
    packages=find_packages(),
    author="BTaskaya",
    author_email="batuhanosmantaskaya@gmail.com",
    description = "Experimental Universal Virtual Machine",
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url="https://github.com/BTaskaya/Arkhe"
)
