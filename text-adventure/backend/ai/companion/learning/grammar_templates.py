"""
Grammar Template Manager for the Companion AI.

This module contains the GrammarTemplateManager class, which is responsible for
managing grammar explanation templates and tracking player interactions with
grammar points.
"""

import logging
import json
import os
import time
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Default grammar templates for common JLPT N5 grammar points
DEFAULT_GRAMMAR_TEMPLATES = {
    "は vs が": {
        "explanation": """
は (wa) and が (ga) are both subject markers in Japanese, but they are used differently:

は (wa) is the topic marker. It introduces the topic of the sentence, which is what the sentence is about.
が (ga) is the subject marker. It identifies the subject that performs the action.

Key differences:
- は (wa) often indicates information that is already known or has been mentioned.
- が (ga) often introduces new information or emphasizes the subject.
- は (wa) can mark the topic, which might not be the grammatical subject.
- が (ga) specifically marks the grammatical subject of the action.
        """,
        "examples": [
            {
                "japanese": "私は学生です。",
                "romaji": "Watashi wa gakusei desu.",
                "english": "I am a student. (Establishing 'I' as the topic)"
            },
            {
                "japanese": "私が学生です。",
                "romaji": "Watashi ga gakusei desu.",
                "english": "I am a student. (Emphasizing that it's ME who is a student, not someone else)"
            },
            {
                "japanese": "富士山は高いです。",
                "romaji": "Fujisan wa takai desu.",
                "english": "Mt. Fuji is tall. (Mt. Fuji as a topic)"
            },
            {
                "japanese": "誰が来ましたか？",
                "romaji": "Dare ga kimashita ka?",
                "english": "Who came? (Asking for the subject)"
            }
        ],
        "common_mistakes": [
            "Using は when asking 'who' questions (should use が)",
            "Using が for general statements about a topic (should use は)",
            "Not recognizing that the same sentence with は vs が can have different nuances"
        ],
        "practice_suggestions": [
            "Try making simple sentences about yourself using は",
            "Practice asking questions with が",
            "Try describing the same thing using both は and が and notice the difference"
        ]
    },
    "です/ます form": {
        "explanation": """
です (desu) and ます (masu) are polite ending forms in Japanese:

です (desu) is used with nouns and adjectives to make polite statements.
ます (masu) is attached to verb stems to create polite verb forms.

These forms are used in formal situations, when speaking to people you don't know well, or in business contexts.
        """,
        "examples": [
            {
                "japanese": "これは本です。",
                "romaji": "Kore wa hon desu.",
                "english": "This is a book."
            },
            {
                "japanese": "私は日本に行きます。",
                "romaji": "Watashi wa Nihon ni ikimasu.",
                "english": "I will go to Japan."
            },
            {
                "japanese": "毎日勉強します。",
                "romaji": "Mainichi benkyō shimasu.",
                "english": "I study every day."
            }
        ],
        "common_mistakes": [
            "Using です with verbs (should use ます)",
            "Forgetting to change the verb form before adding ます",
            "Using casual forms in formal situations"
        ],
        "practice_suggestions": [
            "Practice introducing yourself using です",
            "Convert casual verb forms to ます forms",
            "Try describing your daily routine using ます form"
        ]
    },
    "て form": {
        "explanation": """
The て (te) form is one of the most important verb forms in Japanese. It has multiple uses:

1. Connecting actions in sequence: "I did A and then B"
2. Making requests: "Please do something"
3. Forming the progressive tense: "I am doing something"
4. Giving reasons: "Because of..."

The way to form the て form depends on the type of verb:
- For る-verbs: Drop る and add て
- For う-verbs: The ending changes according to specific rules
        """,
        "examples": [
            {
                "japanese": "食べて寝ます。",
                "romaji": "Tabete nemasu.",
                "english": "I will eat and then sleep."
            },
            {
                "japanese": "水を飲んでください。",
                "romaji": "Mizu o nonde kudasai.",
                "english": "Please drink water."
            },
            {
                "japanese": "今、勉強しています。",
                "romaji": "Ima, benkyō shite imasu.",
                "english": "I am studying now."
            }
        ],
        "common_mistakes": [
            "Incorrect conjugation of irregular verbs (する → して, 来る → 来て)",
            "Forgetting the rules for う-verbs (e.g., 書く → 書いて)",
            "Using the wrong form for negative requests"
        ],
        "practice_suggestions": [
            "Practice conjugating different types of verbs to て form",
            "Try making sentences that connect two actions",
            "Use て form to make polite requests"
        ]
    },
    "に particle": {
        "explanation": """
The に (ni) particle has several important uses in Japanese:

1. Indicating destination: "to" or "toward" a place
2. Marking time: specific points in time
3. Marking the indirect object: the receiver of an action
4. Indicating purpose: "in order to"

It's one of the most versatile particles in Japanese.
        """,
        "examples": [
            {
                "japanese": "東京に行きます。",
                "romaji": "Tōkyō ni ikimasu.",
                "english": "I will go to Tokyo."
            },
            {
                "japanese": "7時に起きます。",
                "romaji": "Shichi-ji ni okimasu.",
                "english": "I wake up at 7 o'clock."
            },
            {
                "japanese": "友達にプレゼントをあげました。",
                "romaji": "Tomodachi ni purezento o agemashita.",
                "english": "I gave a present to my friend."
            }
        ],
        "common_mistakes": [
            "Confusing に and へ for destinations",
            "Using に instead of で for locations where actions take place",
            "Forgetting to use に with time expressions"
        ],
        "practice_suggestions": [
            "Practice making sentences about going to different places",
            "Make a schedule using time expressions with に",
            "Describe giving things to different people using に"
        ]
    },
    "で particle": {
        "explanation": """
The で (de) particle has several important uses in Japanese:

1. Indicating location where an action takes place
2. Indicating means or method: "by" or "with"
3. Indicating material something is made of
4. Indicating a time limit or deadline

It's often confused with に, but they have distinct uses.
        """,
        "examples": [
            {
                "japanese": "公園で遊びます。",
                "romaji": "Kōen de asobimasu.",
                "english": "I play in the park."
            },
            {
                "japanese": "電車で行きます。",
                "romaji": "Densha de ikimasu.",
                "english": "I will go by train."
            },
            {
                "japanese": "木で作りました。",
                "romaji": "Ki de tsukurimashita.",
                "english": "It was made of wood."
            }
        ],
        "common_mistakes": [
            "Using で instead of に for destinations",
            "Using に instead of で for locations where actions occur",
            "Confusing で (means) with を (direct object)"
        ],
        "practice_suggestions": [
            "Practice describing where you do different activities",
            "Make sentences about how you travel to different places",
            "Describe what different things are made of"
        ]
    }
}


class GrammarTemplateManager:
    """
    Manages grammar explanation templates and tracks player interactions.
    
    The GrammarTemplateManager is responsible for:
    - Storing templates for grammar explanations
    - Providing formatted explanations for grammar points
    - Tracking which grammar points the player has encountered
    - Customizing grammar templates for specific points
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the GrammarTemplateManager.
        
        Args:
            data_path: Optional path to load/save grammar data
        """
        # Copy the default grammar templates
        self.grammar_templates = DEFAULT_GRAMMAR_TEMPLATES.copy()
        
        # Track player's grammar history
        self.player_grammar_history = {}
        
        # Path for saving/loading data
        self.data_path = data_path
        
        # Load data if path is provided
        if data_path and os.path.exists(data_path):
            self.load_data(data_path)
        
        logger.debug(f"GrammarTemplateManager initialized with {len(self.grammar_templates)} templates")
    
    def get_grammar_template(self, grammar_point: str) -> str:
        """
        Get a formatted explanation for a grammar point.
        
        Args:
            grammar_point: The grammar point to explain
            
        Returns:
            A formatted explanation string
        """
        # Record this explanation request
        self.record_grammar_explanation(grammar_point)
        
        # Check if we have a template for this grammar point
        if grammar_point in self.grammar_templates:
            template = self.grammar_templates[grammar_point]
            explanation = template["explanation"].strip()
            
            # Add examples if available
            if "examples" in template and template["examples"]:
                explanation += "\n\nExamples:\n"
                for i, example in enumerate(template["examples"][:3], 1):  # Limit to 3 examples
                    japanese = example['japanese']
                    english = example['english']
                    romaji = example.get('romaji', '')  # Make romaji optional
                    
                    if romaji:
                        explanation += f"\n{i}. {japanese}\n   {romaji}\n   {english}\n"
                    else:
                        explanation += f"\n{i}. {japanese}\n   {english}\n"
            
            # Add common mistakes if available
            if "common_mistakes" in template and template["common_mistakes"]:
                explanation += "\n\nCommon mistakes to avoid:\n"
                for mistake in template["common_mistakes"][:3]:  # Limit to 3 mistakes
                    explanation += f"- {mistake}\n"
            
            # Add practice suggestions if available
            if "practice_suggestions" in template and template["practice_suggestions"]:
                explanation += "\n\nPractice suggestions:\n"
                for suggestion in template["practice_suggestions"][:2]:  # Limit to 2 suggestions
                    explanation += f"- {suggestion}\n"
            
            return explanation
        else:
            # Return a generic message for unknown grammar points
            return f"I don't have specific information about '{grammar_point}' yet. If you'd like to learn about this grammar point, please let me know and I can add it to my knowledge base."
    
    def get_grammar_examples(self, grammar_point: str) -> List[Dict[str, str]]:
        """
        Get examples for a grammar point.
        
        Args:
            grammar_point: The grammar point to get examples for
            
        Returns:
            A list of example dictionaries
        """
        if grammar_point in self.grammar_templates and "examples" in self.grammar_templates[grammar_point]:
            return self.grammar_templates[grammar_point]["examples"]
        return []
    
    def record_grammar_explanation(self, grammar_point: str) -> None:
        """
        Record that a grammar point was explained to the player.
        
        Args:
            grammar_point: The grammar point that was explained
        """
        # Initialize history for this grammar point if it doesn't exist
        if grammar_point not in self.player_grammar_history:
            self.player_grammar_history[grammar_point] = {
                "explanation_count": 0,
                "first_explained_at": time.time(),
                "last_explained_at": time.time()
            }
        
        # Update the history
        self.player_grammar_history[grammar_point]["explanation_count"] += 1
        self.player_grammar_history[grammar_point]["last_explained_at"] = time.time()
        
        logger.debug(f"Recorded grammar explanation for: {grammar_point}")
    
    def add_custom_grammar_template(self, grammar_point: str, template: Dict[str, Any]) -> None:
        """
        Add a custom grammar template.
        
        Args:
            grammar_point: The grammar point to add a template for
            template: The template dictionary
        """
        if not template.get("explanation"):
            logger.warning(f"Attempted to add template without explanation for: {grammar_point}")
            return
        
        self.grammar_templates[grammar_point] = template
        logger.debug(f"Added custom grammar template for: {grammar_point}")
    
    def get_all_grammar_points(self) -> List[str]:
        """
        Get a list of all available grammar points.
        
        Returns:
            A list of grammar point names
        """
        return list(self.grammar_templates.keys())
    
    def get_grammar_history(self, grammar_point: str) -> Dict[str, Any]:
        """
        Get the player's history with a grammar point.
        
        Args:
            grammar_point: The grammar point to get history for
            
        Returns:
            A dictionary with history information
        """
        if grammar_point not in self.player_grammar_history:
            return {
                "grammar_point": grammar_point,
                "explanation_count": 0,
                "has_template": grammar_point in self.grammar_templates
            }
        
        history = self.player_grammar_history[grammar_point].copy()
        history["grammar_point"] = grammar_point
        history["has_template"] = grammar_point in self.grammar_templates
        
        return history
    
    def get_frequently_explained_grammar(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most frequently explained grammar points.
        
        Args:
            limit: Maximum number of points to return
            
        Returns:
            A list of dictionaries with grammar point information
        """
        # Sort grammar points by explanation count
        sorted_grammar = sorted(
            self.player_grammar_history.items(),
            key=lambda x: x[1]["explanation_count"],
            reverse=True
        )
        
        # Return the top N points
        result = []
        for grammar_point, history in sorted_grammar[:limit]:
            result.append(self.get_grammar_history(grammar_point))
        
        return result
    
    def save_data(self, path: Optional[str] = None) -> bool:
        """
        Save grammar data to a file.
        
        Args:
            path: The path to save to (defaults to self.data_path)
            
        Returns:
            True if successful, False otherwise
        """
        save_path = path or self.data_path
        if not save_path:
            logger.warning("No path specified for saving grammar data")
            return False
        
        try:
            data = {
                "grammar_templates": self.grammar_templates,
                "player_grammar_history": self.player_grammar_history
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved grammar data to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save grammar data: {e}")
            return False
    
    def load_data(self, path: Optional[str] = None) -> bool:
        """
        Load grammar data from a file.
        
        Args:
            path: The path to load from (defaults to self.data_path)
            
        Returns:
            True if successful, False otherwise
        """
        load_path = path or self.data_path
        if not load_path:
            logger.warning("No path specified for loading grammar data")
            return False
        
        try:
            with open(load_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.grammar_templates = data.get("grammar_templates", {})
            self.player_grammar_history = data.get("player_grammar_history", {})
            
            logger.info(f"Loaded grammar data from {load_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load grammar data: {e}")
            return False 