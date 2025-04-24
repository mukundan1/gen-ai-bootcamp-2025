import uuid
from typing import Dict, List, Any, Optional

from backend.api.adapters.base import RequestAdapter, ResponseAdapter
from backend.api.models.player_progress import (
    PlayerInfo, ProgressMetrics, AccuracyRates, GrammarProgressMetrics,
    ConversationMetrics, MasteredVocabularyItem, LearningVocabularyItem,
    ReviewVocabularyItem, MasteredGrammarPoint, LearningGrammarPoint,
    ReviewGrammarPoint, SkillPentagon, ProgressTimePoint, VocabularyProgress,
    GrammarProgress, VisualizationData, PlayerProgressResponse
)


class InvalidPlayerIdError(Exception):
    """Exception raised when a player ID is invalid."""
    pass


class PlayerNotFoundError(Exception):
    """Exception raised when a player is not found."""
    pass


# Internal models (placeholders for now)
class InternalPlayerProgressRequest:
    """Internal representation of a player progress request."""
    
    def __init__(self, player_id: str, request_id: str):
        self.player_id = player_id
        self.request_id = request_id


class InternalPlayerProgressResponse:
    """Internal representation of a player progress response."""
    
    def __init__(
        self,
        request_id: str,
        player: Dict[str, Any],
        vocabulary_progress: Dict[str, Any],
        grammar_progress: Dict[str, Any],
        conversation_metrics: Dict[str, Any],
        achievements: List[str],
        recommendations: Dict[str, List[str]],
        visualization_data: Dict[str, Any]
    ):
        self.request_id = request_id
        self.player = player
        self.vocabulary_progress = vocabulary_progress
        self.grammar_progress = grammar_progress
        self.conversation_metrics = conversation_metrics
        self.achievements = achievements
        self.recommendations = recommendations
        self.visualization_data = visualization_data


class PlayerProgressRequestAdapter(RequestAdapter):
    """Adapter for player progress requests."""
    
    def adapt(self, player_id: str) -> InternalPlayerProgressRequest:
        """
        Transform an API request to the internal format.
        
        Args:
            player_id: The player ID from the request
            
        Returns:
            The internal request
        """
        # Validate player ID format
        if not self._is_valid_player_id(player_id):
            raise InvalidPlayerIdError(f"Invalid player ID format: {player_id}")
        
        # Create the internal request
        internal_request = InternalPlayerProgressRequest(
            player_id=player_id,
            request_id=str(uuid.uuid4())
        )
        
        return internal_request
    
    def _is_valid_player_id(self, player_id: str) -> bool:
        """
        Validate the player ID format.
        
        Args:
            player_id: The player ID to validate
            
        Returns:
            True if the player ID is valid, False otherwise
        """
        # Simple validation for now - can be enhanced later
        return bool(player_id) and len(player_id) >= 3


class PlayerProgressResponseAdapter(ResponseAdapter):
    """Adapter for player progress responses."""
    
    def adapt(self, internal_response: InternalPlayerProgressResponse) -> PlayerProgressResponse:
        """
        Transform an internal response to the API format.
        
        Args:
            internal_response: The internal response
            
        Returns:
            The API response
        """
        # Transform player info
        player_info = PlayerInfo(
            id=internal_response.player["id"],
            level=internal_response.player["level"]
        )
        
        # Transform progress metrics
        progress = self._create_progress_metrics(
            internal_response.vocabulary_progress,
            internal_response.grammar_progress,
            internal_response.conversation_metrics
        )
        
        # Transform vocabulary progress
        vocabulary_progress = self._create_vocabulary_progress(internal_response.vocabulary_progress)
        
        # Transform grammar progress
        grammar_progress = self._create_grammar_progress(internal_response.grammar_progress)
        
        # Transform visualization data
        visualization_data = self._create_visualization_data(internal_response.visualization_data)
        
        # Create the API response
        api_response = PlayerProgressResponse(
            player=player_info,
            progress=progress,
            achievements=internal_response.achievements,
            recommendations=internal_response.recommendations,
            vocabulary=vocabulary_progress,
            grammarPoints=grammar_progress,
            visualizationData=visualization_data
        )
        
        return api_response
    
    def _create_progress_metrics(
        self,
        vocabulary_progress: Dict[str, Any],
        grammar_progress: Dict[str, Any],
        conversation_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create progress metrics from internal data.
        
        Args:
            vocabulary_progress: Internal vocabulary progress data
            grammar_progress: Internal grammar progress data
            conversation_metrics: Internal conversation metrics data
            
        Returns:
            Progress metrics in API format
        """
        # Create vocabulary metrics
        vocabulary_metrics = ProgressMetrics(
            total=vocabulary_progress["total"],
            mastered=vocabulary_progress["mastered_count"],
            learning=vocabulary_progress["learning_count"],
            needsReview=vocabulary_progress["needs_review"],
            percentComplete=vocabulary_progress["percent_complete"]
        )
        
        # Create grammar metrics
        accuracy_rates = AccuracyRates(
            particles=grammar_progress["accuracy_rates"]["particles"],
            verbForms=grammar_progress["accuracy_rates"]["verb_forms"],
            sentences=grammar_progress["accuracy_rates"]["sentences"]
        )
        
        grammar_metrics = GrammarProgressMetrics(
            total=grammar_progress["total"],
            mastered=grammar_progress["mastered_count"],
            learning=grammar_progress["learning_count"],
            needsReview=grammar_progress["needs_review"],
            percentComplete=grammar_progress["percent_complete"],
            accuracyRates=accuracy_rates
        )
        
        # Create conversation metrics
        conversation = ConversationMetrics(
            successRate=conversation_metrics["success_rate"],
            completedExchanges=conversation_metrics["completed_exchanges"]
        )
        
        # Combine all metrics
        return {
            "vocabulary": vocabulary_metrics,
            "grammar": grammar_metrics,
            "conversation": conversation
        }
    
    def _create_vocabulary_progress(self, vocabulary_progress: Dict[str, Any]) -> VocabularyProgress:
        """
        Create vocabulary progress from internal data.
        
        Args:
            vocabulary_progress: Internal vocabulary progress data
            
        Returns:
            Vocabulary progress in API format
        """
        # Create mastered vocabulary items
        mastered_items = [
            MasteredVocabularyItem(
                word=item["word"],
                reading=item["reading"],
                meaning=item["meaning"],
                examples=item["examples"]
            )
            for item in vocabulary_progress.get("mastered", [])
        ]
        
        # Create learning vocabulary items
        learning_items = [
            LearningVocabularyItem(
                word=item["word"],
                reading=item["reading"],
                meaning=item["meaning"],
                masteryLevel=item["mastery_level"],
                lastSeen=item["last_seen"]
            )
            for item in vocabulary_progress.get("learning", [])
        ]
        
        # Create review vocabulary items
        review_items = [
            ReviewVocabularyItem(
                word=item["word"],
                reading=item["reading"],
                meaning=item["meaning"],
                dueForReview=item["due_for_review"]
            )
            for item in vocabulary_progress.get("for_review", [])
        ]
        
        # Create vocabulary progress
        return VocabularyProgress(
            mastered=mastered_items,
            learning=learning_items,
            forReview=review_items
        )
    
    def _create_grammar_progress(self, grammar_progress: Dict[str, Any]) -> GrammarProgress:
        """
        Create grammar progress from internal data.
        
        Args:
            grammar_progress: Internal grammar progress data
            
        Returns:
            Grammar progress in API format
        """
        # Create mastered grammar points
        mastered_points = [
            MasteredGrammarPoint(
                pattern=item["pattern"],
                explanation=item["explanation"],
                examples=item["examples"]
            )
            for item in grammar_progress.get("mastered", [])
        ]
        
        # Create learning grammar points
        learning_points = [
            LearningGrammarPoint(
                pattern=item["pattern"],
                explanation=item["explanation"],
                masteryLevel=item["mastery_level"]
            )
            for item in grammar_progress.get("learning", [])
        ]
        
        # Create review grammar points
        review_points = [
            ReviewGrammarPoint(
                pattern=item["pattern"],
                explanation=item["explanation"],
                dueForReview=item["due_for_review"]
            )
            for item in grammar_progress.get("for_review", [])
        ]
        
        # Create grammar progress
        return GrammarProgress(
            mastered=mastered_points,
            learning=learning_points,
            forReview=review_points
        )
    
    def _create_visualization_data(self, visualization_data: Dict[str, Any]) -> VisualizationData:
        """
        Create visualization data from internal data.
        
        Args:
            visualization_data: Internal visualization data
            
        Returns:
            Visualization data in API format
        """
        # Create skill pentagon
        skill_pentagon = SkillPentagon(
            reading=visualization_data["skill_pentagon"]["reading"],
            writing=visualization_data["skill_pentagon"]["writing"],
            listening=visualization_data["skill_pentagon"]["listening"],
            speaking=visualization_data["skill_pentagon"]["speaking"],
            vocabulary=visualization_data["skill_pentagon"]["vocabulary"]
        )
        
        # Create progress over time
        progress_over_time = [
            ProgressTimePoint(
                date=point["date"],
                vocabularyMastered=point["vocabulary_mastered"],
                grammarMastered=point["grammar_mastered"]
            )
            for point in visualization_data.get("progress_over_time", [])
        ]
        
        # Create visualization data
        return VisualizationData(
            skillPentagon=skill_pentagon,
            progressOverTime=progress_over_time
        ) 