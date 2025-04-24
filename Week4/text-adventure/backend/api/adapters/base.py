"""
Base adapter interfaces for transforming between API and internal data formats.
"""

from typing import Dict, Any, TypeVar, Generic, Type

# Generic type variables
T = TypeVar('T')  # Request/Response type
U = TypeVar('U')  # Adapted type


class RequestAdapter(Generic[T, U]):
    """Base interface for request adapters."""
    
    def adapt(self, request: T) -> U:
        """
        Adapt the request to the internal format.
        
        Args:
            request: The request to adapt.
            
        Returns:
            The adapted request.
        """
        raise NotImplementedError("Subclasses must implement adapt()")


class ResponseAdapter(Generic[T, U]):
    """Base interface for response adapters."""
    
    def adapt(self, response: T) -> U:
        """
        Adapt the response to the API format.
        
        Args:
            response: The response to adapt.
            
        Returns:
            The adapted response.
        """
        raise NotImplementedError("Subclasses must implement adapt()")


class AdapterFactory:
    """Factory for creating adapters."""
    
    @staticmethod
    def get_request_adapter(adapter_type: str) -> RequestAdapter:
        """
        Get a request adapter by type.
        
        Args:
            adapter_type: The type of adapter to get.
            
        Returns:
            The adapter.
        """
        # Import adapters here to avoid circular imports
        from backend.api.adapters.companion_assist import CompanionAssistRequestAdapter
        from backend.api.adapters.dialogue_process import DialogueProcessRequestAdapter
        from backend.api.adapters.player_progress import PlayerProgressRequestAdapter
        from backend.api.adapters.game_state import (
            GameStateSaveRequestAdapter,
            GameStateLoadRequestAdapter,
            GameStateListRequestAdapter
        )
        from backend.api.adapters.npc import NPCConfigurationUpdateRequestAdapter
        from backend.api.adapters.deepseek_parameters import DeepSeekParametersRequestAdapter
        
        adapters = {
            "companion_assist": CompanionAssistRequestAdapter(),
            "dialogue_process": DialogueProcessRequestAdapter(),
            "player_progress": PlayerProgressRequestAdapter(),
            "game_state_save": GameStateSaveRequestAdapter(),
            "game_state_load": GameStateLoadRequestAdapter(),
            "game_state_list": GameStateListRequestAdapter(),
            "npc_configuration_update": NPCConfigurationUpdateRequestAdapter(),
            "deepseek_parameters": DeepSeekParametersRequestAdapter()
        }
        
        return adapters.get(adapter_type)
    
    @staticmethod
    def get_response_adapter(adapter_type: str) -> ResponseAdapter:
        """
        Get a response adapter by type.
        
        Args:
            adapter_type: The type of adapter to get.
            
        Returns:
            The adapter.
            
        Raises:
            ValueError: If the adapter type is not supported.
        """
        # Import adapters here to avoid circular imports
        from backend.api.adapters.companion_assist import CompanionAssistResponseAdapter
        from backend.api.adapters.dialogue_process import DialogueProcessResponseAdapter
        from backend.api.adapters.player_progress import PlayerProgressResponseAdapter
        from backend.api.adapters.game_state import (
            GameStateSaveResponseAdapter,
            GameStateLoadResponseAdapter,
            GameStateListResponseAdapter
        )
        from backend.api.adapters.npc import (
            NPCInformationResponseAdapter,
            NPCConfigurationResponseAdapter,
            NPCInteractionStateResponseAdapter
        )
        from backend.api.adapters.npc_dialogue import NPCDialogueResponseAdapter
        from backend.api.adapters.deepseek_parameters import DeepSeekParametersResponseAdapter
        
        adapters = {
            "companion_assist": CompanionAssistResponseAdapter(),
            "dialogue_process": DialogueProcessResponseAdapter(),
            "player_progress": PlayerProgressResponseAdapter(),
            "game_state_save": GameStateSaveResponseAdapter(),
            "game_state_load": GameStateLoadResponseAdapter(),
            "game_state_list": GameStateListResponseAdapter(),
            "npc_information": NPCInformationResponseAdapter(),
            "npc_configuration": NPCConfigurationResponseAdapter(),
            "npc_interaction_state": NPCInteractionStateResponseAdapter(),
            "npc_dialogue": NPCDialogueResponseAdapter(),
            "deepseek_parameters": DeepSeekParametersResponseAdapter()
        }
        
        if adapter_type not in adapters:
            raise ValueError(f"Unsupported response adapter type: {adapter_type}")
        
        return adapters[adapter_type] 