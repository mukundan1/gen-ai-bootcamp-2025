from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class PlayerInfo(BaseModel):
    """Player information."""
    id: str = Field(..., description="Unique player identifier")
    level: str = Field(..., description="Current JLPT level (N5, N4, etc.)")


class ProgressMetrics(BaseModel):
    """Overall progress metrics."""
    total: int = Field(..., description="Total number of items")
    mastered: int = Field(..., description="Number of mastered items")
    learning: int = Field(..., description="Number of items being learned")
    needsReview: int = Field(..., description="Number of items needing review")
    percentComplete: float = Field(..., description="Percentage of items mastered")


class AccuracyRates(BaseModel):
    """Grammar accuracy rates."""
    particles: float = Field(..., description="Accuracy rate for particles")
    verbForms: float = Field(..., description="Accuracy rate for verb forms")
    sentences: float = Field(..., description="Accuracy rate for sentences")


class GrammarProgressMetrics(ProgressMetrics):
    """Grammar progress metrics."""
    accuracyRates: AccuracyRates = Field(..., description="Accuracy rates for different grammar aspects")


class ConversationMetrics(BaseModel):
    """Conversation success metrics."""
    successRate: float = Field(..., description="Rate of successful conversation exchanges")
    completedExchanges: int = Field(..., description="Number of completed conversation exchanges")


class VocabularyItem(BaseModel):
    """Vocabulary item with basic information."""
    word: str = Field(..., description="Japanese word")
    reading: str = Field(..., description="Reading in hiragana")
    meaning: str = Field(..., description="English meaning")


class MasteredVocabularyItem(VocabularyItem):
    """Fully mastered vocabulary item."""
    examples: List[str] = Field(..., description="Example sentences using the word")


class LearningVocabularyItem(VocabularyItem):
    """Vocabulary item being learned."""
    masteryLevel: float = Field(..., description="Mastery level from 0.0 to 1.0")
    lastSeen: str = Field(..., description="ISO timestamp when the word was last encountered")


class ReviewVocabularyItem(VocabularyItem):
    """Vocabulary item needing review."""
    dueForReview: bool = Field(..., description="Whether the item is due for review")


class GrammarPoint(BaseModel):
    """Grammar pattern with basic information."""
    pattern: str = Field(..., description="Grammar pattern")
    explanation: str = Field(..., description="Explanation of the grammar pattern")


class MasteredGrammarPoint(GrammarPoint):
    """Fully mastered grammar pattern."""
    examples: List[str] = Field(..., description="Example sentences using the grammar pattern")


class LearningGrammarPoint(GrammarPoint):
    """Grammar pattern being learned."""
    masteryLevel: float = Field(..., description="Mastery level from 0.0 to 1.0")


class ReviewGrammarPoint(GrammarPoint):
    """Grammar pattern needing review."""
    dueForReview: bool = Field(..., description="Whether the pattern is due for review")


class SkillPentagon(BaseModel):
    """Five language skill metrics."""
    reading: float = Field(..., description="Reading skill level from 0.0 to 1.0")
    writing: float = Field(..., description="Writing skill level from 0.0 to 1.0")
    listening: float = Field(..., description="Listening skill level from 0.0 to 1.0")
    speaking: float = Field(..., description="Speaking skill level from 0.0 to 1.0")
    vocabulary: float = Field(..., description="Vocabulary skill level from 0.0 to 1.0")


class ProgressTimePoint(BaseModel):
    """Historical progress data point."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    vocabularyMastered: int = Field(..., description="Number of vocabulary items mastered on this date")
    grammarMastered: int = Field(..., description="Number of grammar patterns mastered on this date")


class VocabularyProgress(BaseModel):
    """Detailed vocabulary knowledge."""
    mastered: List[MasteredVocabularyItem] = Field(default_factory=list, description="Fully learned vocabulary items")
    learning: List[LearningVocabularyItem] = Field(default_factory=list, description="Vocabulary in progress")
    forReview: List[ReviewVocabularyItem] = Field(default_factory=list, description="Vocabulary needing review")


class GrammarProgress(BaseModel):
    """Detailed grammar knowledge."""
    mastered: List[MasteredGrammarPoint] = Field(default_factory=list, description="Fully learned grammar patterns")
    learning: List[LearningGrammarPoint] = Field(default_factory=list, description="Grammar patterns in progress")
    forReview: List[ReviewGrammarPoint] = Field(default_factory=list, description="Grammar patterns needing review")


class VisualizationData(BaseModel):
    """Data for progress visualizations."""
    skillPentagon: SkillPentagon = Field(..., description="Five language skill metrics")
    progressOverTime: List[ProgressTimePoint] = Field(..., description="Historical progress data")


class PlayerProgressResponse(BaseModel):
    """Response model for the player progress endpoint."""
    player: PlayerInfo = Field(..., description="Basic player information")
    progress: Dict[str, Any] = Field(..., description="Overall progress metrics")
    achievements: List[str] = Field(..., description="List of language-related achievements")
    recommendations: Dict[str, List[str]] = Field(..., description="Personalized learning recommendations")
    vocabulary: VocabularyProgress = Field(..., description="Detailed vocabulary knowledge")
    grammarPoints: GrammarProgress = Field(..., description="Detailed grammar knowledge")
    visualizationData: VisualizationData = Field(..., description="Data for progress visualizations") 