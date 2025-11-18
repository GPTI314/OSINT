# OSINT Data Processing Pipeline - User Guide

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Extractors](#extractors)
4. [Enrichment](#enrichment)
5. [Storage](#storage)
6. [Validation](#validation)
7. [Advanced Usage](#advanced-usage)
8. [Best Practices](#best-practices)

## Installation

### Basic Installation

```bash
pip install -r requirements.txt
```

### Optional Dependencies

For full functionality, install optional dependencies:

```bash
# NLP features
pip install nltk spacy textblob langdetect scikit-learn gensim
python -m spacy download en_core_web_sm

# Image processing
pip install pytesseract opencv-python

# PDF processing
pip install PyPDF2 pdfplumber

# Databases
pip install sqlalchemy pymongo
```

## Quick Start

### Basic Pipeline Setup

```python
from osint_pipeline import ETLPipeline
from osint_pipeline.extractors import TextExtractor
from osint_pipeline.enrichment import EntityRecognizer, SentimentAnalyzer

# Create pipeline
pipeline = ETLPipeline()

# Register components
pipeline.register_extractor('text', TextExtractor())
pipeline.register_enricher('entities', EntityRecognizer())
pipeline.register_enricher('sentiment', SentimentAnalyzer())

# Process data
result = pipeline.process(
    source="Your text here",
    extractor_name='text',
    collection='documents'
)

print(result['data_id'])
```

## Extractors

### HTML Extractor

Extract data from web pages and HTML content.

#### Basic Usage

```python
from osint_pipeline.extractors import HTMLExtractor

extractor = HTMLExtractor()
data = extractor.extract('https://example.com')

print(data['title'])
print(data['links'])
print(data['text'])
```

#### CSS Selectors

```python
css_selectors = {
    'title': 'h1.page-title',
    'author': '.author-name',
    'content': '.article-content'
}

data = extractor.extract(html_content, css_selectors=css_selectors)
print(data['custom_data']['css'])
```

#### XPath Queries

```python
xpath_queries = {
    'headings': '//h2/text()',
    'first_paragraph': '//p[1]',
    'all_links': '//a/@href'
}

data = extractor.extract(html_content, xpath_queries=xpath_queries)
print(data['custom_data']['xpath'])
```

#### Regex Patterns

```python
regex_patterns = {
    'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone_numbers': r'\d{3}-\d{3}-\d{4}'
}

data = extractor.extract(html_content, regex_patterns=regex_patterns)
print(data['custom_data']['regex'])
```

### JSON Extractor

Extract and validate JSON data.

#### Basic Usage

```python
from osint_pipeline.extractors import JSONExtractor

extractor = JSONExtractor()
data = extractor.extract(json_string)

print(data['metadata'])
```

#### JSONPath Queries

```python
jsonpath_queries = {
    'all_names': '$.users[*].name',
    'first_email': '$.users[0].email',
    'ids': '$..id'
}

data = extractor.extract(json_data, jsonpath_queries=jsonpath_queries)
print(data['custom_data']['jsonpath'])
```

#### Schema Validation

```python
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"}
    },
    "required": ["name"]
}

data = extractor.extract(json_data, schema=schema)
print(data['schema_validation'])
```

### Text Extractor

Extract structured information from text.

#### Pattern Extraction

```python
from osint_pipeline.extractors import TextExtractor

extractor = TextExtractor()
data = extractor.extract(text)

# Built-in patterns
print(data['patterns']['email'])
print(data['patterns']['url'])
print(data['patterns']['phone_us'])
print(data['patterns']['ip_address'])
```

#### Custom Patterns

```python
custom_patterns = {
    'bitcoin_addresses': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
    'dates': r'\d{4}-\d{2}-\d{2}'
}

data = extractor.extract(text, custom_patterns=custom_patterns)
print(data['custom_data']['patterns'])
```

#### Statistics and Entities

```python
data = extractor.extract(text)

print(data['statistics']['word_count'])
print(data['statistics']['sentence_count'])
print(data['entities']['emails'])
print(data['entities']['hashtags'])
```

### Image Extractor

Extract text and metadata from images.

#### Basic Usage

```python
from osint_pipeline.extractors import ImageExtractor

extractor = ImageExtractor(ocr_lang='eng')
data = extractor.extract('path/to/image.jpg')

print(data['metadata'])
print(data['exif'])
```

#### OCR Text Extraction

```python
data = extractor.extract('image.jpg', extract_ocr=True)
print(data['ocr']['text'])
print(data['ocr']['boxes'])  # Bounding boxes for detected text
```

#### Visual Analysis

```python
data = extractor.extract('image.jpg', extract_visual=True)
print(data['visual']['colors'])  # Dominant colors
print(data['visual']['brightness'])
```

### PDF Extractor

Extract text and structure from PDFs.

#### Basic Usage

```python
from osint_pipeline.extractors import PDFExtractor

extractor = PDFExtractor()
data = extractor.extract('document.pdf')

print(data['text'])
print(data['page_count'])
print(data['metadata'])
```

#### Table Extraction

```python
data = extractor.extract('document.pdf', extract_tables=True)
print(data['tables'])
print(data['table_count'])
```

#### Specific Pages

```python
text_by_page = extractor.extract_text_by_page('document.pdf', [1, 2, 3])
print(text_by_page[1])  # Text from page 1
```

## Enrichment

### Entity Recognition

Identify persons, organizations, locations, and other entities.

```python
from osint_pipeline.enrichment import EntityRecognizer

recognizer = EntityRecognizer(confidence_threshold=0.7)
result = recognizer.analyze(text)

print(result['entity_counts'])  # {'PERSON': 3, 'ORG': 2, 'GPE': 1}

for entity in result['entities']:
    print(f"{entity['text']} - {entity['label']} ({entity['confidence']})")
```

#### Extract Specific Entity Types

```python
persons = recognizer.extract_persons(text)
organizations = recognizer.extract_organizations(text)
locations = recognizer.extract_locations(text)
```

### Sentiment Analysis

Analyze the sentiment and emotion of text.

```python
from osint_pipeline.enrichment import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.analyze(text)

print(result['category'])  # 'positive', 'negative', or 'neutral'
print(result['polarity'])  # -1.0 to 1.0
print(result['subjectivity'])  # 0.0 to 1.0
```

#### Sentence-Level Sentiment

```python
sentences = analyzer.analyze_sentences(text)
for sent in sentences:
    print(f"{sent['sentence']}: {sent['polarity']}")
```

### Language Detection

Detect the language of text content.

```python
from osint_pipeline.enrichment import LanguageDetector

detector = LanguageDetector()
result = detector.detect(text)

print(result['language'])  # 'en', 'es', 'fr', etc.
print(result['languages'])  # All detected languages with probabilities
```

#### Verify Language

```python
is_english = detector.is_language(text, 'en', threshold=0.9)
```

### Keyword Extraction

Extract important keywords and phrases.

```python
from osint_pipeline.enrichment import KeywordExtractor

extractor = KeywordExtractor(top_n=20)
result = extractor.extract(text)

for kw in result['keywords']:
    print(f"{kw['keyword']}: {kw['score']}")
```

#### Extract Phrases

```python
phrases = extractor.extract_phrases(text, max_phrase_length=3)
for phrase in phrases:
    print(f"{phrase['phrase']} ({phrase['frequency']})")
```

### Topic Modeling

Discover topics in text.

```python
from osint_pipeline.enrichment import TopicModeler

modeler = TopicModeler(num_topics=5, num_words=10)
result = modeler.extract_topics(text)

for topic in result['topics']:
    print(f"Topic {topic['topic_id']}: {', '.join(topic['words'])}")
```

### Link Analysis

Analyze relationships and networks.

```python
from osint_pipeline.enrichment import LinkAnalyzer

analyzer = LinkAnalyzer()

# Add relationships
analyzer.add_link('Alice', 'Bob', 'colleague')
analyzer.add_link('Bob', 'Charlie', 'friend')
analyzer.add_link('Alice', 'Charlie', 'friend')

# Calculate metrics
metrics = analyzer.calculate_metrics()
print(f"Network density: {metrics['density']}")
print(f"Central nodes: {metrics['centrality']}")

# Find path
path = analyzer.get_shortest_path('Alice', 'Charlie')
print(f"Path: {' -> '.join(path)}")
```

## Storage

### File Storage

```python
from osint_pipeline.storage import FileStorage

storage = FileStorage({'output_dir': './data'})
storage.connect()

# Store data
data_id = storage.store(data, collection='documents')

# Retrieve data
retrieved = storage.retrieve(data_id, collection='documents')

# Query data
results = storage.query({'field': 'value'}, collection='documents')
```

### SQL Storage

```python
from osint_pipeline.storage import SQLStorage

storage = SQLStorage({
    'connection_string': 'postgresql://user:pass@localhost/osint'
})
storage.connect()

data_id = storage.store(data, collection='documents')
```

### MongoDB Storage

```python
from osint_pipeline.storage import MongoStorage

storage = MongoStorage({
    'host': 'localhost',
    'port': 27017,
    'database': 'osint'
})
storage.connect()

data_id = storage.store(data, collection='documents')
```

## Validation

### Basic Validation

```python
from osint_pipeline.etl.validators import DataValidator, ValidationRule

validator = DataValidator()

# Add required fields
validator.add_required_field('title')
validator.add_required_field('content')

# Add type checks
validator.add_type_check('age', int)
validator.add_type_check('name', str)

# Validate
is_valid, errors = validator.validate(data)
```

### Custom Validation Rules

```python
# Range check
validator.add_range_check('score', min_val=0, max_val=100)

# Regex pattern
validator.add_regex_pattern('email', r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Custom rule
custom_rule = ValidationRule(
    name='positive_number',
    validator=lambda x: isinstance(x, (int, float)) and x > 0,
    error_message='Value must be a positive number'
)
validator.add_rule('amount', custom_rule)
```

### Quality Checks

```python
quality_report = validator.quality_check(data)
print(quality_report['completeness'])
print(quality_report['validity'])
```

## Advanced Usage

### Batch Processing

```python
sources = [url1, url2, url3, url4]

results = pipeline.process_batch(
    sources=sources,
    extractor_name='html',
    collection='web_pages',
    validate_data=True,
    enrich_data=True
)

for result in results:
    if result['success']:
        print(f"Processed: {result['data_id']}")
```

### Custom Transformations

```python
def custom_transform(data):
    # Add custom field
    data['processed_by'] = 'my_pipeline'

    # Modify existing data
    if 'text' in data:
        data['text'] = data['text'].upper()

    return data

pipeline.processor.add_transformation(custom_transform)
```

### Selective Enrichment

```python
# Disable specific enricher
pipeline.enricher.disable_enricher('topics')

# Process with selective enrichment
result = pipeline.process(source, 'text', enrich_data=True)
```

### Pipeline Statistics

```python
stats = pipeline.get_stats()
print(f"Total: {stats['total_processed']}")
print(f"Success: {stats['successful']}")
print(f"Failed: {stats['failed']}")
print(f"Start: {stats['start_time']}")
print(f"End: {stats['end_time']}")

# Reset statistics
pipeline.reset_stats()
```

## Best Practices

### 1. Error Handling

Always check the success status:

```python
result = pipeline.process(source, 'text')
if result['success']:
    data_id = result['data_id']
    # Process successful result
else:
    error = result['error']
    # Handle error
```

### 2. Resource Management

Close connections when done:

```python
storage.connect()
try:
    # Process data
    pass
finally:
    storage.disconnect()
```

### 3. Performance Optimization

Use batch processing for multiple items:

```python
# Good
results = pipeline.process_batch(sources, 'html')

# Less efficient
results = [pipeline.process(s, 'html') for s in sources]
```

### 4. Validation

Always validate critical data:

```python
pipeline.validator.add_required_field('critical_field')
result = pipeline.process(source, 'text', validate_data=True)

if not result['data']['validation']['is_valid']:
    # Handle validation errors
    errors = result['data']['validation']['errors']
```

### 5. Configuration

Use configuration files for environment-specific settings:

```python
from osint_pipeline.utils import load_config

config = load_config('config.yaml')
pipeline = ETLPipeline(config)
```
