# get-papers-list

Fetch PubMed research papers with at least one author affiliated with a pharmaceutical or biotech company, and output results as a CSV file.

## Features
- Fetches papers from PubMed using the official API (supports full PubMed query syntax)
- Filters for papers with at least one non-academic (pharma/biotech) author using heuristics
- Outputs results as a CSV file or prints to the console
- Command-line interface with options for query, debug, and output file
- Typed Python, modular code, robust error handling

## Code Organization
- `src/get_papers_list/papers.py`: Core module for fetching, filtering, and saving papers
- `src/get_papers_list/__main__.py`: CLI entrypoint using Typer
- `pyproject.toml`: Poetry configuration and CLI script registration
- `tests/`: (empty, for future tests)

## Installation

1. **Clone the repository** (if on GitHub):
   ```sh
   git clone <your-repo-url>
   cd get_papers_list
   ```
2. **Install dependencies with Poetry:**
   ```sh
   poetry install
   ```

## Usage

### Run the CLI

- **Basic usage:**
  ```sh
  poetry run get-papers-list "your pubmed query"
  ```
- **Save results to a CSV file:**
  ```sh
  poetry run get-papers-list "your pubmed query" -f results.csv
  ```
- **Show debug information:**
  ```sh
  poetry run get-papers-list "your pubmed query" --debug
  ```
- **Use CLI alias:**
  ```sh
  poetry run papers-list "your pubmed query"
  ```

### Example
```sh
poetry run get-papers-list "cancer immunotherapy" -f results.csv
```

### Output Columns
- PubmedID
- Title
- Publication Date
- Non-academicAuthor(s)
- CompanyAffiliation(s)
- Corresponding Author Email

## Heuristics for Non-Academic Authors
- Affiliations are checked for keywords (e.g., pharma, biotech, Inc, Ltd, etc.)
- Academic institutions (university, hospital, etc.) are excluded
- Email addresses are extracted if present

## Dependencies & Tools
- [Poetry](https://python-poetry.org/) for dependency management
- [Typer](https://typer.tiangolo.com/) for CLI
- [Requests](https://docs.python-requests.org/) for HTTP requests
- Python standard library: `csv`, `re`, `xml.etree.ElementTree`

## Development
- All code is typed and modular
- Error handling for API failures and missing data
- To add more CLI aliases, edit the `[tool.poetry.scripts]` section in `pyproject.toml`


## Author
Fariha Jeelani Tambitkar
