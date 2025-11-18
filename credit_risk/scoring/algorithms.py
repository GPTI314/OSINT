"""Credit Scoring Algorithms.

Provides various scoring methodologies including weighted scoring,
ML-based scoring, ensemble methods, rule-based scoring, and hybrid approaches.
"""

import logging
from typing import Dict, Any, List
import numpy as np

logger = logging.getLogger(__name__)


class ScoringAlgorithms:
    """Credit scoring algorithms."""

    def weighted_score(
        self,
        factors: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """
        Calculate weighted risk score.

        Args:
            factors: Dictionary of factor scores
            weights: Dictionary of factor weights

        Returns:
            Weighted score
        """
        try:
            if not factors or not weights:
                return 0.0

            total_weight = sum(weights.values())
            if total_weight == 0:
                return 0.0

            weighted_sum = sum(
                factors.get(key, 0) * weight
                for key, weight in weights.items()
            )

            return weighted_sum / total_weight

        except Exception as e:
            logger.error(f"Error calculating weighted score: {str(e)}")
            return 0.0

    def ml_score(
        self,
        features: Dict[str, Any],
        model: Any
    ) -> float:
        """
        Calculate ML-based risk score.

        Args:
            features: Feature dictionary
            model: Trained ML model

        Returns:
            ML-based score
        """
        try:
            # Convert features to array
            feature_array = self._features_to_array(features)

            # Predict using model
            score = model.predict(feature_array)[0]

            return float(score)

        except Exception as e:
            logger.error(f"Error calculating ML score: {str(e)}")
            return 0.0

    def ensemble_score(
        self,
        scores: List[float],
        weights: Optional[List[float]] = None
    ) -> float:
        """
        Calculate ensemble risk score from multiple scores.

        Args:
            scores: List of scores from different models
            weights: Optional weights for each score

        Returns:
            Ensemble score
        """
        try:
            if not scores:
                return 0.0

            if weights is None:
                # Equal weights
                return float(np.mean(scores))
            else:
                # Weighted average
                if len(scores) != len(weights):
                    logger.warning("Scores and weights length mismatch, using equal weights")
                    return float(np.mean(scores))

                total_weight = sum(weights)
                if total_weight == 0:
                    return 0.0

                weighted_sum = sum(s * w for s, w in zip(scores, weights))
                return weighted_sum / total_weight

        except Exception as e:
            logger.error(f"Error calculating ensemble score: {str(e)}")
            return 0.0

    def rule_based_score(
        self,
        rules: List[Dict[str, Any]],
        data: Dict[str, Any]
    ) -> float:
        """
        Calculate rule-based risk score.

        Args:
            rules: List of scoring rules
            data: Data to evaluate

        Returns:
            Rule-based score
        """
        try:
            score = 0.0
            total_weight = 0.0

            for rule in rules:
                condition = rule.get('condition')
                points = rule.get('points', 0)
                weight = rule.get('weight', 1.0)

                if self._evaluate_condition(condition, data):
                    score += points * weight
                    total_weight += weight

            if total_weight == 0:
                return 0.0

            return score / total_weight

        except Exception as e:
            logger.error(f"Error calculating rule-based score: {str(e)}")
            return 0.0

    def hybrid_score(
        self,
        ml_score: float,
        rule_score: float,
        ml_weight: float = 0.7
    ) -> float:
        """
        Calculate hybrid score combining ML and rule-based approaches.

        Args:
            ml_score: ML-based score
            rule_score: Rule-based score
            ml_weight: Weight for ML score (0-1)

        Returns:
            Hybrid score
        """
        try:
            rule_weight = 1 - ml_weight
            return ml_score * ml_weight + rule_score * rule_weight

        except Exception as e:
            logger.error(f"Error calculating hybrid score: {str(e)}")
            return 0.0

    # Helper methods

    def _features_to_array(self, features: Dict[str, Any]) -> np.ndarray:
        """Convert feature dictionary to numpy array."""
        # Placeholder implementation
        return np.array([list(features.values())])

    def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        data: Dict[str, Any]
    ) -> bool:
        """Evaluate a rule condition."""
        try:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')

            data_value = data.get(field)

            if operator == 'gt':
                return data_value > value
            elif operator == 'gte':
                return data_value >= value
            elif operator == 'lt':
                return data_value < value
            elif operator == 'lte':
                return data_value <= value
            elif operator == 'eq':
                return data_value == value
            elif operator == 'neq':
                return data_value != value
            elif operator == 'in':
                return data_value in value
            elif operator == 'not_in':
                return data_value not in value
            else:
                return False

        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return False
