"""
Gradio application for testing the companion AI.
"""

import os
import json
import asyncio
import gradio as gr
from typing import Dict, Any, List, Tuple

from client import send_companion_request
from defaults import (
    LOCATIONS,
    QUESTS,
    QUEST_STEPS,
    REQUEST_TYPES,
    LANGUAGES,
    get_default_payload
)


def format_response(response: Dict[str, Any]) -> str:
    """
    Format the response for display.
    
    Args:
        response: The response from the API
        
    Returns:
        A formatted string representation of the response
    """
    if not response:
        return "No response received."
        
    dialogue = response.get("dialogue", {})
    text = dialogue.get("text", "")
    japanese = dialogue.get("japanese", "")
    pronunciation = dialogue.get("pronunciation", "")
    character_name = dialogue.get("characterName", "Hachi")
    
    formatted = f"<b>{character_name}:</b> {text}\n\n"
    
    if japanese:
        formatted += f"<b>Japanese:</b> {japanese}\n"
    
    if pronunciation:
        formatted += f"<b>Pronunciation:</b> {pronunciation}\n"
        
    return formatted


def format_debug_info(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the debug information for display.
    
    Args:
        response: The response from the API
        
    Returns:
        A dictionary with debug information
    """
    if not response:
        return {"error": "No debug information available."}
        
    # Extract relevant parts for debugging
    companion = response.get("companion", {})
    ui = response.get("ui", {})
    game_state = response.get("gameState", {})
    meta = response.get("meta", {})
    
    debug_info = {
        "companion_state": companion,
        "ui_elements": ui,
        "game_state_updates": game_state,
        "metadata": meta
    }
    
    return debug_info


def get_quest_steps_for_quest(quest: str) -> List[str]:
    """
    Get the quest steps for a given quest.
    
    Args:
        quest: The quest name
        
    Returns:
        A list of quest steps
    """
    if not quest:
        return []
        
    return QUEST_STEPS.get(quest, [])


async def handle_submit(
    player_id: str,
    session_id: str,
    location: str,
    quest: str,
    quest_step: str,
    request_type: str,
    text: str,
    target_entity: str,
    target_location: str,
    language: str
) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    """
    Handle form submission.
    
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
        A tuple of (formatted_response, request_payload, response_payload)
    """
    # Create the payload
    payload = get_default_payload(
        player_id=player_id,
        session_id=session_id,
        location=location,
        quest=quest if quest != "None" else None,
        quest_step=quest_step if quest_step != "None" else None,
        request_type=request_type,
        text=text,
        target_entity=target_entity if target_entity else None,
        target_location=target_location if target_location else None,
        language=language
    )
    
    try:
        # Send the request
        response = await send_companion_request(payload)
        
        # Format the response
        formatted_response = format_response(response)
        debug_info = format_debug_info(response)
        
        return formatted_response, payload, response
    except Exception as e:
        return f"Error: {str(e)}", payload, {"error": str(e)}


def create_app():
    """
    Create the Gradio application.
    
    Returns:
        The Gradio interface
    """
    with gr.Blocks(title="Tokyo Train Station Adventure - Companion AI Simulator") as app:
        gr.Markdown("# Tokyo Train Station Adventure - Companion AI Simulator")
        gr.Markdown("Use this simulator to test the companion AI with text input and output.")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Player Information")
                player_id = gr.Textbox(
                    label="Player ID",
                    value="test_player_123",
                    info="Unique identifier for the player"
                )
                session_id = gr.Textbox(
                    label="Session ID",
                    value="test_session_456",
                    info="Current session identifier"
                )
                
                gr.Markdown("### Game Context")
                location = gr.Dropdown(
                    label="Location",
                    choices=LOCATIONS,
                    value=LOCATIONS[0],
                    info="Player's current location in the station"
                )
                quest = gr.Dropdown(
                    label="Current Quest",
                    choices=["None"] + QUESTS,
                    value="None",
                    info="Active quest identifier"
                )
                quest_step = gr.Dropdown(
                    label="Quest Step",
                    choices=["None"],
                    value="None",
                    info="Current step in the active quest"
                )
                
                # Update quest steps when quest changes
                def update_quest_steps(quest_value):
                    if quest_value == "None":
                        return {"choices": ["None"], "value": "None"}
                    steps = get_quest_steps_for_quest(quest_value)
                    return {"choices": ["None"] + steps, "value": "None"}
                
                quest.change(update_quest_steps, inputs=[quest], outputs=[quest_step])
                
            with gr.Column(scale=1):
                gr.Markdown("### Request Details")
                request_type = gr.Dropdown(
                    label="Request Type",
                    choices=REQUEST_TYPES,
                    value=REQUEST_TYPES[0],
                    info="Type of assistance requested"
                )
                text = gr.Textbox(
                    label="Text",
                    value="Can you help me?",
                    info="Player's question or request text",
                    lines=3
                )
                target_entity = gr.Textbox(
                    label="Target Entity",
                    value="",
                    info="Entity the player is asking about (optional)"
                )
                target_location = gr.Textbox(
                    label="Target Location",
                    value="",
                    info="Location the player is asking about (optional)"
                )
                language = gr.Dropdown(
                    label="Language",
                    choices=LANGUAGES,
                    value=LANGUAGES[0],
                    info="Language of the player's request"
                )
                
                submit_button = gr.Button("Submit Request", variant="primary")
        
        # Companion Response Section
        gr.Markdown("### Companion Response")
        response_output = gr.HTML(
            value="Submit a request to see the companion's response.",
            label="Response"
        )
        
        # Debug Information Section
        gr.Markdown("### Debug Information")
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Accordion("Request JSON", open=False):
                    request_json = gr.JSON(
                        value={},
                        label="Request Payload"
                    )
            with gr.Column(scale=1):
                with gr.Accordion("Response JSON", open=False):
                    response_json = gr.JSON(
                        value={},
                        label="Response Payload"
                    )
        
        # Handle form submission
        submit_button.click(
            fn=handle_submit,
            inputs=[
                player_id,
                session_id,
                location,
                quest,
                quest_step,
                request_type,
                text,
                target_entity,
                target_location,
                language
            ],
            outputs=[response_output, request_json, response_json]
        )
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(server_name="0.0.0.0") 