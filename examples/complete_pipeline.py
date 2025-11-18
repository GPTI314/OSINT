"""
Complete pipeline example demonstrating all features
"""
from osint_pipeline import ETLPipeline, DataProcessor
from osint_pipeline.extractors import (
    HTMLExtractor, JSONExtractor, TextExtractor,
    ImageExtractor, PDFExtractor
)
from osint_pipeline.enrichment import (
    EntityRecognizer, SentimentAnalyzer, LanguageDetector,
    KeywordExtractor, TopicModeler, LinkAnalyzer
)
from osint_pipeline.storage import FileStorage
from osint_pipeline.etl.validators import DataValidator, ValidationRule


def setup_pipeline():
    """Set up a complete pipeline with all components"""
    # Initialize pipeline
    pipeline = ETLPipeline({
        'strict_validation': False,
        'batch_size': 100
    })

    # Configure storage
    storage = FileStorage({'output_dir': './data/output'})
    pipeline.set_storage(storage)

    # Register all extractors
    pipeline.register_extractor('html', HTMLExtractor())
    pipeline.register_extractor('json', JSONExtractor())
    pipeline.register_extractor('text', TextExtractor())
    pipeline.register_extractor('image', ImageExtractor())
    pipeline.register_extractor('pdf', PDFExtractor())

    # Register all enrichers
    pipeline.register_enricher('entities', EntityRecognizer())
    pipeline.register_enricher('sentiment', SentimentAnalyzer())
    pipeline.register_enricher('language', LanguageDetector())
    pipeline.register_enricher('keywords', KeywordExtractor(top_n=15))
    pipeline.register_enricher('topics', TopicModeler(num_topics=5))
    pipeline.register_enricher('links', LinkAnalyzer())

    # Configure validation rules
    validator = pipeline.validator
    validator.add_required_field('text')
    validator.add_type_check('text', str)

    # Add custom transformation
    def add_timestamp_transform(data):
        from datetime import datetime
        data['processed_timestamp'] = datetime.utcnow().isoformat()
        return data

    pipeline.processor.add_transformation(add_timestamp_transform)

    return pipeline


def process_sample_data():
    """Process various types of sample data"""
    pipeline = setup_pipeline()

    print("=" * 70)
    print("OSINT Data Processing Pipeline - Complete Demo")
    print("=" * 70)

    # Sample data sources
    samples = [
        {
            'name': 'News Article',
            'type': 'text',
            'data': """
            Breaking News: Tech Giant Announces Major AI Breakthrough

            SAN FRANCISCO - TechCorp Inc., led by CEO Sarah Johnson, announced today
            a significant advancement in artificial intelligence technology. The new
            system, called "SmartAI", demonstrates unprecedented capabilities in
            natural language understanding and generation.

            The announcement was made at the company's headquarters in San Francisco,
            California. Industry experts are calling this a game-changing development
            that could revolutionize how we interact with technology.

            Dr. Michael Chen, Chief AI Scientist at TechCorp, explained that the
            breakthrough came after years of research and development. "This represents
            a new era in AI," Dr. Chen stated during the press conference.

            Investors responded positively to the news, with TechCorp's stock price
            rising 15% in after-hours trading. The company plans to release the
            technology to the public next quarter.

            Contact: press@techcorp.com | Phone: 555-123-4567
            """
        },
        {
            'name': 'Social Media Post',
            'type': 'text',
            'data': """
            Just had the most amazing experience at @TechCorp's new product launch!
            The #AI technology is absolutely mind-blowing! 🤖✨
            Can't wait to see how this transforms the industry.
            Huge congratulations to the team! #Innovation #Technology
            """
        },
        {
            'name': 'Research Abstract',
            'type': 'text',
            'data': """
            Abstract: This study investigates the application of machine learning
            algorithms in cybersecurity threat detection. We propose a novel approach
            combining deep neural networks with traditional signature-based methods.
            Our experimental results demonstrate a 94% accuracy rate in identifying
            zero-day exploits, significantly outperforming existing solutions.
            The research was conducted at MIT in collaboration with industry partners.
            """
        }
    ]

    # Process each sample
    results = []
    for sample in samples:
        print(f"\n{'=' * 70}")
        print(f"Processing: {sample['name']}")
        print(f"{'=' * 70}")

        result = pipeline.process(
            source=sample['data'],
            extractor_name=sample['type'],
            collection='osint_data',
            validate_data=True,
            enrich_data=True
        )

        if result['success']:
            results.append(result)
            print(f"✓ Successfully processed and stored with ID: {result['data_id']}")

            # Display enrichment insights
            display_insights(result['data'])
        else:
            print(f"✗ Processing failed: {result.get('error')}")

    # Display pipeline statistics
    print(f"\n{'=' * 70}")
    print("Pipeline Statistics")
    print(f"{'=' * 70}")

    stats = pipeline.get_stats()
    print(f"Total documents processed: {stats['total_processed']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Success rate: {(stats['successful']/stats['total_processed']*100):.1f}%")


def display_insights(data):
    """Display enrichment insights from processed data"""
    enrichment = data.get('enrichment', {})
    results = enrichment.get('results', {})

    # Entity recognition
    if 'entities' in results:
        entities = results['entities']
        counts = entities.get('entity_counts', {})
        print(f"\n  Entities Detected: {dict(counts)}")

        entity_list = entities.get('entities', [])
        if entity_list:
            print(f"  Sample entities:")
            for entity in entity_list[:5]:
                print(f"    - {entity['text']} ({entity['label']})")

    # Sentiment analysis
    if 'sentiment' in results:
        sentiment = results['sentiment']
        print(f"\n  Sentiment: {sentiment.get('category', 'N/A').upper()}")
        print(f"  Polarity: {sentiment.get('polarity', 0):.3f}")
        print(f"  Subjectivity: {sentiment.get('subjectivity', 0):.3f}")

    # Language detection
    if 'language' in results:
        language = results['language']
        print(f"\n  Language: {language.get('language', 'N/A').upper()}")

    # Keywords
    if 'keywords' in results:
        keywords = results['keywords']
        kw_list = keywords.get('keywords', [])
        if kw_list:
            top_kw = [k.get('keyword', 'N/A') for k in kw_list[:5]]
            print(f"\n  Top Keywords: {', '.join(top_kw)}")

    # Topics
    if 'topics' in results:
        topics = results['topics']
        topic_list = topics.get('topics', [])
        if topic_list:
            print(f"\n  Topics ({topics.get('method', 'N/A')}):")
            for topic in topic_list[:3]:
                words = topic.get('words', [])[:5]
                print(f"    - {', '.join(words)}")

    # Validation
    if 'validation' in data:
        validation = data['validation']
        print(f"\n  Validation: {'✓ PASSED' if validation['is_valid'] else '✗ FAILED'}")
        if not validation['is_valid']:
            print(f"  Errors: {len(validation['errors'])}")


if __name__ == '__main__':
    process_sample_data()
