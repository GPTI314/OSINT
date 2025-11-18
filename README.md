# OSINT Data Processing Pipeline

Open-Source Intelligence (OSINT) toolkit: modular collectors, enrichment pipeline, link analysis, risk scoring, and investigative workflow automation.

## Features

### 🔍 Data Extraction
- **HTML Extractors**: CSS selectors, XPath, regex pattern matching
- **JSON Extractors**: JSONPath queries, schema validation
- **Text Extractors**: NLP-based extraction, pattern matching, entity detection
- **Image Extractors**: OCR, EXIF metadata, visual analysis, QR code detection
- **PDF Extractors**: Text extraction, table parsing, structure analysis

### 🔄 ETL Pipeline
- **Data Extraction**: Multi-format data extraction with structured output
- **Data Transformation**: Normalization, cleaning, and custom transformations
- **Data Validation**: Quality checks, schema validation, completeness scoring
- **Data Enrichment**: AI-powered analysis and context enhancement
- **Data Storage**: Multi-backend support (File, SQL, MongoDB)

### 🧠 Data Enrichment
- **Entity Recognition**: Identify persons, organizations, locations, dates, money
- **Sentiment Analysis**: Polarity, subjectivity, emotion detection
- **Language Detection**: Multi-language detection with confidence scores
- **Topic Modeling**: Unsupervised topic discovery using LDA
- **Keyword Extraction**: TF-IDF and frequency-based keyword extraction
- **Link Analysis**: Relationship mapping, network metrics, community detection

### 💾 Storage Backends
- **File Storage**: JSON-based local storage
- **SQL Storage**: SQLite, PostgreSQL, MySQL support via SQLAlchemy
- **MongoDB Storage**: NoSQL document storage for flexible schemas

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/OSINT.git
cd OSINT

# Install dependencies
pip install -r requirements.txt

# Optional: Install NLP models
python -m spacy download en_core_web_sm
```

### Basic Usage

```python
from osint_pipeline import ETLPipeline
from osint_pipeline.extractors import TextExtractor
from osint_pipeline.enrichment import EntityRecognizer, SentimentAnalyzer

# Create and configure pipeline
pipeline = ETLPipeline()
pipeline.register_extractor('text', TextExtractor())
pipeline.register_enricher('entities', EntityRecognizer())
pipeline.register_enricher('sentiment', SentimentAnalyzer())

# Process data
text = "Apple Inc. announced a new product launch in San Francisco."
result = pipeline.process(
    source=text,
    extractor_name='text',
    collection='documents'
)

# Access results
if result['success']:
    print(f"Data ID: {result['data_id']}")
    print(f"Entities: {result['data']['enrichment']['results']['entities']}")
    print(f"Sentiment: {result['data']['enrichment']['results']['sentiment']}")
```

## Architecture

```
osint_pipeline/
├── etl/                    # ETL Pipeline Core
│   ├── pipeline.py        # Main pipeline orchestrator
│   ├── processor.py       # Data transformation
│   ├── validators.py      # Data validation
│   └── enricher.py        # Enrichment coordinator
├── extractors/            # Data Extractors
│   ├── html_extractor.py
│   ├── json_extractor.py
│   ├── text_extractor.py
│   ├── image_extractor.py
│   └── pdf_extractor.py
├── enrichment/            # Enrichment Modules
│   ├── entity_recognition.py
│   ├── sentiment_analyzer.py
│   ├── language_detector.py
│   ├── topic_modeler.py
│   ├── keyword_extractor.py
│   └── link_analyzer.py
├── storage/               # Storage Backends
│   ├── file_storage.py
│   ├── sql_storage.py
│   └── mongo_storage.py
└── utils/                 # Utilities
    ├── helpers.py
    └── config.py
```

## Examples

### HTML Extraction

```python
from osint_pipeline.extractors import HTMLExtractor

extractor = HTMLExtractor()

# Extract with CSS selectors
data = extractor.extract(
    'https://example.com',
    css_selectors={
        'title': 'h1.page-title',
        'author': '.author-name'
    }
)

# Extract with XPath
data = extractor.extract(
    html_content,
    xpath_queries={
        'headings': '//h2/text()',
        'links': '//a/@href'
    }
)
```

### Entity Recognition

```python
from osint_pipeline.enrichment import EntityRecognizer

recognizer = EntityRecognizer()
result = recognizer.analyze("John Smith works at Apple Inc. in San Francisco.")

print(result['entities'])
# [
#   {'text': 'John Smith', 'label': 'PERSON', 'confidence': 1.0},
#   {'text': 'Apple Inc.', 'label': 'ORG', 'confidence': 1.0},
#   {'text': 'San Francisco', 'label': 'GPE', 'confidence': 1.0}
# ]
```

### Link Analysis

```python
from osint_pipeline.enrichment import LinkAnalyzer

analyzer = LinkAnalyzer()
analyzer.add_link('Alice', 'Bob', 'colleague')
analyzer.add_link('Bob', 'Charlie', 'friend')
analyzer.add_link('Alice', 'Charlie', 'friend')

metrics = analyzer.calculate_metrics()
print(f"Network density: {metrics['density']}")
print(f"Most central nodes: {metrics['centrality']}")

path = analyzer.get_shortest_path('Alice', 'Charlie')
print(f"Shortest path: {' -> '.join(path)}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and architecture
- [User Guide](docs/USER_GUIDE.md) - Comprehensive usage guide
- [Examples](examples/) - Example scripts and use cases

## Use Cases

### Intelligence Gathering
- Web scraping and data extraction
- Social media monitoring
- News aggregation and analysis
- Document processing and analysis

### Investigative Research
- Entity relationship mapping
- Pattern detection and analysis
- Sentiment tracking over time
- Multi-source data correlation

### Content Analysis
- Topic discovery and tracking
- Language detection and translation prep
- Keyword trend analysis
- Document classification

### Security Analysis
- Threat intelligence collection
- Credential monitoring
- IP and domain analysis
- Dark web monitoring

## Requirements

### Core Dependencies
- Python 3.7+
- requests, beautifulsoup4, lxml, cssselect
- pandas, numpy
- jsonpath-ng, jsonschema

### Optional Dependencies
- **NLP**: nltk, spacy, textblob, langdetect, scikit-learn, gensim
- **Image**: Pillow, pytesseract, opencv-python
- **PDF**: PyPDF2, pdfplumber
- **Database**: sqlalchemy, pymongo
- **Graph**: networkx

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This toolkit is intended for legal and ethical OSINT activities only. Users are responsible for ensuring their use complies with applicable laws and regulations.

## Roadmap

- [ ] Add support for video/audio extraction
- [ ] Implement real-time streaming processing
- [ ] Add advanced ML models for classification
- [ ] Create web UI for pipeline management
- [ ] Add support for distributed processing
- [ ] Implement data visualization dashboard
- [ ] Add export to graph databases (Neo4j)
- [ ] Create plugin system for custom modules

## Support

For questions, issues, or feature requests, please open an issue on GitHub.
