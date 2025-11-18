"""
Basic usage example for OSINT Data Processing Pipeline
"""
from osint_pipeline import ETLPipeline
from osint_pipeline.extractors import HTMLExtractor, JSONExtractor, TextExtractor
from osint_pipeline.enrichment import (
    EntityRecognizer, SentimentAnalyzer, LanguageDetector,
    KeywordExtractor, TopicModeler
)
from osint_pipeline.storage import FileStorage


def main():
    # Initialize pipeline
    pipeline = ETLPipeline()

    # Set up storage
    storage = FileStorage({'output_dir': './data/output'})
    pipeline.set_storage(storage)

    # Register extractors
    pipeline.register_extractor('html', HTMLExtractor())
    pipeline.register_extractor('json', JSONExtractor())
    pipeline.register_extractor('text', TextExtractor())

    # Register enrichers
    pipeline.register_enricher('entities', EntityRecognizer())
    pipeline.register_enricher('sentiment', SentimentAnalyzer())
    pipeline.register_enricher('language', LanguageDetector())
    pipeline.register_enricher('keywords', KeywordExtractor())
    pipeline.register_enricher('topics', TopicModeler())

    # Example 1: Process HTML from URL
    print("Example 1: Processing HTML from URL")
    result = pipeline.process(
        source='https://example.com',
        extractor_name='html',
        collection='web_pages'
    )
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Data ID: {result['data_id']}")

    # Example 2: Process text
    print("\nExample 2: Processing text")
    sample_text = """
    John Smith is the CEO of TechCorp Inc., a leading technology company
    based in San Francisco. The company recently announced a new AI product
    that has received positive reviews from industry experts.
    """

    result = pipeline.process(
        source=sample_text,
        extractor_name='text',
        collection='documents',
        validate_data=True,
        enrich_data=True
    )

    if result['success']:
        print(f"Data ID: {result['data_id']}")

        # Display enrichment results
        enrichment = result['data'].get('enrichment', {})
        results = enrichment.get('results', {})

        if 'entities' in results:
            print(f"\nEntities found: {results['entities']['entity_counts']}")

        if 'sentiment' in results:
            sentiment = results['sentiment']
            print(f"\nSentiment: {sentiment.get('category')} (polarity: {sentiment.get('polarity')})")

        if 'language' in results:
            print(f"\nLanguage: {results['language'].get('language')}")

        if 'keywords' in results:
            keywords = results['keywords'].get('keywords', [])[:5]
            print(f"\nTop Keywords: {[k.get('keyword') for k in keywords]}")

    # Get pipeline statistics
    stats = pipeline.get_stats()
    print(f"\nPipeline Statistics:")
    print(f"Total processed: {stats['total_processed']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")


if __name__ == '__main__':
    main()
