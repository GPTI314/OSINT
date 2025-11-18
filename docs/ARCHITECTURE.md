# OSINT Data Processing Pipeline - Architecture

## Overview

The OSINT Data Processing Pipeline is a comprehensive toolkit for extracting, transforming, enriching, and storing data from various sources. It follows a modular architecture with clear separation of concerns.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ETL Pipeline Core                        │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Extraction │→ │Transformation│→ │   Validation     │   │
│  └────────────┘  └──────────────┘  └──────────────────┘   │
│         ↓               ↓                    ↓              │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Enrichment │→ │   Storage    │→ │   Results        │   │
│  └────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Extractors    │  │  Enrichment     │  │    Storage      │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • HTML          │  │ • Entity Recog  │  │ • File Storage  │
│ • JSON          │  │ • Sentiment     │  │ • SQL Database  │
│ • Text          │  │ • Language Det  │  │ • MongoDB       │
│ • Image (OCR)   │  │ • Keywords      │  │                 │
│ • PDF           │  │ • Topics        │  │                 │
│                 │  │ • Link Analysis │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Core Components

### 1. ETL Pipeline (`osint_pipeline/etl/`)

#### Pipeline (`pipeline.py`)
- Orchestrates the entire data flow
- Manages extractor and enricher registration
- Handles batch processing
- Tracks statistics and metrics

#### Processor (`processor.py`)
- Data transformation and normalization
- Metadata extraction
- Deduplication
- Data merging and filtering

#### Validator (`validators.py`)
- Data quality checks
- Schema validation
- Completeness and consistency checks
- Custom validation rules

#### Enricher (`enricher.py`)
- Coordinates enrichment modules
- Manages enricher lifecycle
- Aggregates enrichment results

### 2. Data Extractors (`osint_pipeline/extractors/`)

#### HTML Extractor
- **Methods**: CSS selectors, XPath, regex
- **Features**:
  - Meta tag extraction
  - Link and image extraction
  - Table and form parsing
  - Open Graph and Twitter Card support

#### JSON Extractor
- **Methods**: JSONPath queries, schema validation
- **Features**:
  - Nested structure flattening
  - Array extraction
  - Schema validation with JSON Schema
  - Data transformation

#### Text Extractor
- **Methods**: Pattern matching, NLP, regex
- **Features**:
  - Entity extraction (emails, URLs, phones, IPs)
  - N-gram generation
  - Word frequency analysis
  - Text statistics

#### Image Extractor
- **Methods**: OCR, metadata extraction, visual analysis
- **Features**:
  - EXIF metadata extraction
  - OCR text extraction (pytesseract)
  - Dominant color detection
  - QR code detection
  - Visual feature analysis

#### PDF Extractor
- **Methods**: Text extraction, metadata parsing, structure analysis
- **Features**:
  - Multi-page text extraction
  - Table extraction (pdfplumber)
  - Link and image detection
  - Document structure analysis

### 3. Data Enrichment (`osint_pipeline/enrichment/`)

#### Entity Recognition
- **Capabilities**: Persons, organizations, locations, dates, money
- **Methods**: spaCy NLP + pattern matching fallback
- **Output**: Entity list with types, positions, and confidence scores

#### Sentiment Analysis
- **Capabilities**: Polarity, subjectivity, emotion detection
- **Methods**: TextBlob + keyword-based fallback
- **Output**: Sentiment category, polarity score (-1 to 1), subjectivity score

#### Language Detection
- **Capabilities**: Multi-language detection with probabilities
- **Methods**: langdetect + character set analysis fallback
- **Output**: Language code, probability distribution

#### Keyword Extraction
- **Capabilities**: Single keywords and key phrases
- **Methods**: TF-IDF + frequency-based fallback
- **Output**: Ranked list of keywords with scores

#### Topic Modeling
- **Capabilities**: Unsupervised topic discovery
- **Methods**: LDA (Latent Dirichlet Allocation) + frequency fallback
- **Output**: Topics with associated words and weights

#### Link Analysis
- **Capabilities**: Relationship mapping, network analysis
- **Methods**: Graph analysis, community detection
- **Output**: Network metrics, centrality scores, shortest paths

### 4. Storage Backends (`osint_pipeline/storage/`)

#### File Storage
- JSON file-based storage
- Directory-based collections
- Simple and reliable

#### SQL Storage
- SQLAlchemy-based
- Support for SQLite, PostgreSQL, MySQL
- ACID compliance

#### MongoDB Storage
- NoSQL document storage
- Flexible schema
- High scalability

### 5. Utilities (`osint_pipeline/utils/`)

#### Helpers
- Text normalization and sanitization
- URL, email, phone extraction
- Hash calculation
- Timestamp handling

#### Configuration
- YAML-based configuration
- Default settings
- Environment-specific configs

## Data Flow

1. **Extraction Phase**
   - Source → Extractor → Raw Data
   - Metadata added (timestamp, source info)

2. **Transformation Phase**
   - Raw Data → Processor → Normalized Data
   - Custom transformations applied
   - Metadata extracted

3. **Validation Phase**
   - Normalized Data → Validator → Validation Report
   - Quality checks performed
   - Errors collected

4. **Enrichment Phase**
   - Validated Data → Enrichers → Enriched Data
   - Multiple enrichers run in parallel
   - Results aggregated

5. **Storage Phase**
   - Enriched Data → Storage Backend → Persisted Data
   - ID assigned
   - Storage metadata added

## Design Principles

### Modularity
- Each component is independent and reusable
- Clear interfaces between components
- Easy to extend with new extractors/enrichers

### Flexibility
- Multiple storage backends
- Configurable validation rules
- Custom transformations support
- Optional enrichment steps

### Robustness
- Graceful fallbacks for missing dependencies
- Error handling at each stage
- Detailed error reporting
- Transaction support where applicable

### Performance
- Batch processing support
- Lazy loading of heavy dependencies
- Efficient data structures
- Parallel enrichment processing

## Extension Points

### Adding New Extractors
```python
from osint_pipeline.extractors.base import BaseExtractor

class CustomExtractor(BaseExtractor):
    def extract(self, source, **kwargs):
        # Implementation
        return extracted_data

pipeline.register_extractor('custom', CustomExtractor())
```

### Adding New Enrichers
```python
class CustomEnricher:
    def enrich(self, data, fields=None):
        # Implementation
        return enriched_results

pipeline.register_enricher('custom', CustomEnricher())
```

### Adding New Storage Backends
```python
from osint_pipeline.storage.base import StorageBackend

class CustomStorage(StorageBackend):
    def store(self, data, collection='default'):
        # Implementation
        return data_id

pipeline.set_storage(CustomStorage())
```

## Configuration

Configuration can be provided via YAML file or dictionary:

```yaml
etl:
  batch_size: 100
  max_retries: 3
  strict_validation: false

extractors:
  html:
    parser: lxml
    timeout: 10

enrichment:
  entity_recognition:
    model: en_core_web_sm
    confidence_threshold: 0.7

storage:
  default_backend: file
  file:
    output_dir: ./output
```

## Dependencies

### Core Dependencies
- Python 3.7+
- requests, beautifulsoup4, lxml
- pandas, numpy
- jsonpath-ng, jsonschema

### Optional Dependencies
- **NLP**: nltk, spacy, textblob, langdetect, scikit-learn, gensim
- **Image**: Pillow, pytesseract, opencv-python
- **PDF**: PyPDF2, pdfplumber
- **Database**: sqlalchemy, pymongo
- **Graph**: networkx

## Performance Considerations

### Memory
- Streaming processing for large files
- Batch processing for multiple items
- Configurable batch sizes

### Speed
- Parallel enrichment processing
- Lazy loading of models
- Caching of compiled patterns

### Scalability
- Stateless design
- Horizontal scaling support
- Database connection pooling
