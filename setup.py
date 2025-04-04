from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.2.0'
DESCRIPTION = 'A PDF chunking Library to Smartly Chunk PDF files'
LONG_DESCRIPTION = 'A PDF chunking Library to Smartly Chunk PDF files with respect to Headers and Sections of text aka Mindful Chunkiing'

# Setting up
setup(
    name="smartchunk",
    version=VERSION,
    author="Bishal Bose",
    author_email="bishalbose294@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['PyMuPDF', 'numpy', 'pandas', 'Unidecode'],
    keywords=['python', 'llm', 'pdf', 'text chunking', 'semantic chunking', 'chunks'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)