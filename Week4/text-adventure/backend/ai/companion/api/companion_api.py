# Initialize the player history manager
player_history_manager = PlayerHistoryManager()

@router.post("/companion")
async def handle_companion_request(request: dict):
    """Handle a companion request."""
    try:
        player_id = request["playerId"]
        session_id = request["sessionId"]
        
        # Create a Request object
        companion_request = Request(
            request_id=str(uuid.uuid4()),
            player_input=request["request"]["text"],
            request_type=request["request"]["type"],
            timestamp=datetime.now(),
            game_context={
                "player_location": request["gameContext"]["location"],
                "active_quest": request["gameContext"].get("currentQuest"),
                "quest_step": request["gameContext"].get("questStep"),
                "nearby_npcs": request["gameContext"].get("nearbyEntities", []),
                "last_interaction": request["gameContext"].get("lastInteraction")
            },
            additional_params={
                "player_id": player_id,
                "session_id": session_id,
                "target_entity": request["request"].get("targetEntity"),
                "target_location": request["request"].get("targetLocation"),
                "language": request["request"].get("language", "english")
            }
        )
        
        # Get player history and add to additional_params
        player_history = player_history_manager.get_player_history(player_id)
        companion_request.additional_params["player_history"] = player_history
        
        # Process the request
        response = await request_handler.handle_request(companion_request)
        
        # Store the interaction in player history
        player_history_manager.add_interaction(
            player_id=player_id,
            user_query=request["request"]["text"],
            assistant_response=response,
            session_id=session_id,
            metadata={
                "location": request["gameContext"]["location"],
                "request_type": request["request"]["type"],
                "language": request["request"].get("language", "english")
            }
        )
        
        # Format the response for the API
        api_response = {
            "dialogue": {
                "text": response,
                "characterName": "Hachi"
            }
        }
        
        return api_response
    except Exception as e:
        # Handle errors
        logger.error(f"Error handling companion request: {str(e)}")
        return {
            "error": str(e),
            "dialogue": {
                "text": f"I'm sorry, I encountered an error: {str(e)}",
                "characterName": "System"
            }
        } 