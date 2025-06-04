# OpenAI Model Scraper

A collection of Python scripts for scraping and analyzing OpenAI model information and pricing data.

## Project Structure

```
.
├── README.md
├── requirements.txt
├── src/
│   ├── modelScrapeHTML.py    # HTML scraping for model information
│   ├── priceScrape.py        # Price data scraping
└── data/                     # Directory for scraped data
    └── model_html/           # Scraped html data + run_metadata file
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/openai-model-scraper.git
cd openai-model-scraper
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Scraping Model Information
```bash
python src/modelScrapeHTML.py
```

### Scraping Price Information
```bash
python src/priceScrape.py
```

## Features

- Scrapes OpenAI model information and pricing data
- Handles dynamic content loading
- Processes and parses HTML content
- Stores data in structured format

## Requirements

- Python 3.8+
- Playwright
- Other dependencies listed in requirements.txt

## License

MIT License 