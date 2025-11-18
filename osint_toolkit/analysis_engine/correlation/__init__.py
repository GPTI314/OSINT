"""
Correlation Engine - Entity linking, relationship mapping, timeline construction, and pattern detection
"""

from osint_toolkit.analysis_engine.correlation.engine import CorrelationEngine
from osint_toolkit.analysis_engine.correlation.entity_linker import EntityLinker
from osint_toolkit.analysis_engine.correlation.relationship_mapper import RelationshipMapper
from osint_toolkit.analysis_engine.correlation.timeline_builder import TimelineBuilder
from osint_toolkit.analysis_engine.correlation.pattern_detector import PatternDetector

__all__ = [
    "CorrelationEngine",
    "EntityLinker",
    "RelationshipMapper",
    "TimelineBuilder",
    "PatternDetector"
]
