"""
Data enrichment examples
"""
from osint_pipeline.enrichment import (
    EntityRecognizer, SentimentAnalyzer, LanguageDetector,
    KeywordExtractor, TopicModeler, LinkAnalyzer
)


def example_entity_recognition():
    """Entity recognition example"""
    print("=" * 60)
    print("Example 1: Entity Recognition")
    print("=" * 60)

    text = """
    Apple Inc. is planning to open a new store in New York City next month.
    CEO Tim Cook announced the expansion during a press conference on Monday.
    The company expects to create 500 new jobs in the area.
    """

    recognizer = EntityRecognizer()
    result = recognizer.analyze(text)

    print(f"Entities found: {result['entity_counts']}")
    print("\nDetailed entities:")
    for entity in result['entities'][:10]:
        print(f"  - {entity['text']} ({entity['label']})")


def example_sentiment_analysis():
    """Sentiment analysis example"""
    print("\n" + "=" * 60)
    print("Example 2: Sentiment Analysis")
    print("=" * 60)

    texts = [
        "This is an amazing product! I absolutely love it!",
        "Terrible experience. Would not recommend.",
        "It's okay, nothing special but does the job."
    ]

    analyzer = SentimentAnalyzer()

    for text in texts:
        result = analyzer.analyze(text)
        print(f"\nText: {text}")
        print(f"Sentiment: {result['category']}")
        print(f"Polarity: {result['polarity']}")
        print(f"Subjectivity: {result['subjectivity']}")


def example_language_detection():
    """Language detection example"""
    print("\n" + "=" * 60)
    print("Example 3: Language Detection")
    print("=" * 60)

    texts = {
        'English': "Hello, how are you today?",
        'Spanish': "Hola, ¿cómo estás hoy?",
        'French': "Bonjour, comment allez-vous aujourd'hui?",
        'German': "Hallo, wie geht es dir heute?"
    }

    detector = LanguageDetector()

    for expected_lang, text in texts.items():
        result = detector.detect(text)
        print(f"\nExpected: {expected_lang}")
        print(f"Detected: {result['language']}")


def example_keyword_extraction():
    """Keyword extraction example"""
    print("\n" + "=" * 60)
    print("Example 4: Keyword Extraction")
    print("=" * 60)

    text = """
    Artificial intelligence and machine learning are transforming the technology industry.
    Companies are investing heavily in AI research and development. Deep learning models
    are becoming more sophisticated and can now handle complex tasks like natural language
    processing and computer vision. The future of AI looks promising with advances in
    neural networks and data science.
    """

    extractor = KeywordExtractor(top_n=10)
    result = extractor.extract(text)

    print(f"\nTop keywords (method: {result['method']}):")
    for kw in result['keywords']:
        keyword = kw.get('keyword', kw.get('phrase', 'N/A'))
        score = kw.get('score', kw.get('frequency', 0))
        print(f"  - {keyword}: {score}")


def example_topic_modeling():
    """Topic modeling example"""
    print("\n" + "=" * 60)
    print("Example 5: Topic Modeling")
    print("=" * 60)

    text = """
    The technology sector is experiencing rapid growth. Companies are developing
    new software and hardware solutions. Innovation in cloud computing continues
    to accelerate.

    Healthcare providers are adopting digital solutions. Electronic health records
    are becoming standard. Telemedicine is expanding access to care.

    Climate change remains a critical global challenge. Renewable energy adoption
    is increasing. Governments are implementing new environmental policies.
    """

    modeler = TopicModeler(num_topics=3, num_words=5)
    result = modeler.extract_topics(text)

    print(f"\nTopics found: {result['num_topics']}")
    print(f"Method: {result['method']}")

    for topic in result['topics']:
        topic_id = topic.get('topic_id', 0)
        words = topic.get('words', [])
        print(f"\nTopic {topic_id}: {', '.join(words)}")


def example_link_analysis():
    """Link analysis example"""
    print("\n" + "=" * 60)
    print("Example 6: Link Analysis")
    print("=" * 60)

    analyzer = LinkAnalyzer()

    # Add some relationships
    analyzer.add_link('Alice', 'Bob', 'colleague')
    analyzer.add_link('Bob', 'Charlie', 'friend')
    analyzer.add_link('Alice', 'Charlie', 'friend')
    analyzer.add_link('David', 'Alice', 'manager')
    analyzer.add_link('David', 'Bob', 'manager')

    metrics = analyzer.calculate_metrics()

    print(f"\nNetwork Statistics:")
    print(f"Nodes: {len(analyzer.nodes)}")
    print(f"Edges: {len(analyzer.edges)}")
    print(f"Density: {metrics['density']:.3f}")

    print(f"\nTop Central Nodes:")
    for node, score in list(metrics['centrality'].items())[:5]:
        print(f"  - {node}: {score:.3f}")

    # Find path
    path = analyzer.get_shortest_path('Alice', 'Charlie')
    print(f"\nShortest path from Alice to Charlie: {' -> '.join(path)}")


if __name__ == '__main__':
    example_entity_recognition()
    example_sentiment_analysis()
    example_language_detection()
    example_keyword_extraction()
    example_topic_modeling()
    example_link_analysis()
