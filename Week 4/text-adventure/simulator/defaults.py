"""
Default values for testing the companion AI.
"""

# Default player information
DEFAULT_PLAYER_ID = "test_player_123"
DEFAULT_SESSION_ID = "test_session_456"

# Default game locations
LOCATIONS = [
    "station_entrance",
    "ticket_machine_area",
    "platform_1",
    "platform_2",
    "information_desk",
    "convenience_store",
    "waiting_area"
]

# Default quests
QUESTS = [
    "buy_ticket_to_odawara",
    "find_platform_3",
    "buy_bento_for_journey",
    "help_lost_tourist",
    "learn_station_vocabulary"
]

# Default quest steps
QUEST_STEPS = {
    "buy_ticket_to_odawara": [
        "find_ticket_machine",
        "select_destination",
        "pay_for_ticket",
        "collect_ticket"
    ],
    "find_platform_3": [
        "check_station_map",
        "follow_signs",
        "ask_for_directions",
        "arrive_at_platform"
    ],
    "buy_bento_for_journey": [
        "find_convenience_store",
        "select_bento",
        "pay_for_bento"
    ],
    "help_lost_tourist": [
        "approach_tourist",
        "understand_problem",
        "provide_directions"
    ],
    "learn_station_vocabulary": [
        "learn_ticket_words",
        "learn_platform_words",
        "learn_direction_words",
        "practice_conversation"
    ]
}

# Default nearby entities
NEARBY_ENTITIES = {
    "station_entrance": ["station_map", "information_sign", "ticket_gate"],
    "ticket_machine_area": ["ticket_machine_1", "ticket_machine_2", "fare_chart", "help_button"],
    "platform_1": ["bench", "vending_machine", "platform_sign", "train_schedule"],
    "platform_2": ["bench", "trash_bin", "platform_sign", "waiting_passengers"],
    "information_desk": ["staff_member", "brochure_rack", "lost_and_found_box"],
    "convenience_store": ["cashier", "bento_display", "drinks_refrigerator", "snack_shelf"],
    "waiting_area": ["bench", "clock", "departure_board", "other_passengers"]
}

# Default request types
REQUEST_TYPES = [
    "assistance",
    "vocabulary",
    "grammar",
    "direction",
    "translation"
]

# Default language options
LANGUAGES = ["english", "japanese"]

# Create a default game context
def get_default_game_context(location="station_entrance", quest=None, quest_step=None):
    """
    Get a default game context for testing.
    
    Args:
        location: The player's current location
        quest: The current active quest
        quest_step: The current quest step
        
    Returns:
        A dictionary with default game context values
    """
    if quest and quest in QUEST_STEPS and not quest_step:
        quest_step = QUEST_STEPS[quest][0]
        
    return {
        "location": location,
        "currentQuest": quest,
        "questStep": quest_step,
        "nearbyEntities": NEARBY_ENTITIES.get(location, []),
        "lastInteraction": NEARBY_ENTITIES.get(location, ["none"])[0]
    }

# Create a default request
def get_default_request(
    request_type="assistance",
    text="Can you help me?",
    target_entity=None,
    target_location=None,
    language="english"
):
    """
    Get a default request for testing.
    
    Args:
        request_type: The type of assistance requested
        text: The player's question or request text
        target_entity: The entity the player is asking about
        target_location: The location the player is asking about
        language: The language of the player's request
        
    Returns:
        A dictionary with default request values
    """
    return {
        "type": request_type,
        "text": text,
        "targetEntity": target_entity,
        "targetLocation": target_location,
        "language": language
    }

# Create a complete default request payload
def get_default_payload(
    player_id=DEFAULT_PLAYER_ID,
    session_id=DEFAULT_SESSION_ID,
    location="station_entrance",
    quest=None,
    quest_step=None,
    request_type="assistance",
    text="Can you help me?",
    target_entity=None,
    target_location=None,
    language="english"
):
    """
    Get a complete default request payload for testing.
    
    Args:
        player_id: The player's ID
        session_id: The session ID
        location: The player's current location
        quest: The current active quest
        quest_step: The current quest step
        request_type: The type of assistance requested
        text: The player's question or request text
        target_entity: The entity the player is asking about
        target_location: The location the player is asking about
        language: The language of the player's request
        
    Returns:
        A dictionary with the complete request payload
    """
    if not target_entity and location in NEARBY_ENTITIES and NEARBY_ENTITIES[location]:
        target_entity = NEARBY_ENTITIES[location][0]
        
    return {
        "playerId": player_id,
        "sessionId": session_id,
        "gameContext": get_default_game_context(location, quest, quest_step),
        "request": get_default_request(request_type, text, target_entity, target_location, language)
    } 