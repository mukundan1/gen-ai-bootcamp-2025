"""
Text Adventure - Request Handler

This module implements the request handler for the companion AI system.
It coordinates the flow of requests through the system.
"""

import logging
import traceback
import inspect
import time
from typing import Optional, Any, Dict, Tuple

from backend.ai.companion.core.models import (
    CompanionRequest,
    ClassifiedRequest,
    CompanionResponse,
    ConversationContext,
    IntentCategory,
    ComplexityLevel,
    ProcessingTier
)


class RequestHandler:
    """
    Handles requests to the companion AI system.
    
    This class is responsible for:
    1. Receiving requests from the player
    2. Classifying the intent and complexity of the request
    3. Routing the request to the appropriate processor
    4. Formatting the response
    5. Tracking conversation context
    """
    
    def __init__(self, intent_classifier, processor_factory, response_formatter, player_history_manager=None):
        """
        Initialize the request handler.
        
        Args:
            intent_classifier: Component that classifies request intent and complexity
            processor_factory: Factory that provides processors for different tiers
            response_formatter: Component that formats responses
            player_history_manager: Optional player history manager for tracking player interactions
        """
        self.intent_classifier = intent_classifier
        self.processor_factory = processor_factory
        self.response_formatter = response_formatter
        self.player_history_manager = player_history_manager
        self.logger = logging.getLogger(__name__)
    
    async def handle_request(self, request: CompanionRequest, 
                      conversation_context: Optional[ConversationContext] = None) -> str:
        """
        Handle a request from the player.
        
        Args:
            request: The request from the player
            conversation_context: Optional conversation context for multi-turn interactions
            
        Returns:
            A formatted response string
        """
        request_id = getattr(request, 'request_id', 'unknown')
        start_time = time.time()
        self.logger.info(f"Handling request: {request_id} - {request.player_input}")
        
        try:
            # Classify the request
            self.logger.debug(f"Classifying request: {request_id}")
            classification_start = time.time()
            intent, complexity, tier, confidence, entities = self.intent_classifier.classify(request)
            classification_time = time.time() - classification_start
            self.logger.debug(f"Request classified in {classification_time:.3f}s as intent={intent.name}, complexity={complexity.name}, tier={tier.name}, confidence={confidence:.2f}: {request_id}")
            
            # Create a classified request
            self.logger.debug(f"Creating classified request: {request_id}")
            classified_request = ClassifiedRequest.from_companion_request(
                request=request,
                intent=intent,
                complexity=complexity,
                processing_tier=tier,
                confidence=confidence,
                extracted_entities=entities
            )
            
            # Log the initial tier selection at INFO level
            self.logger.info(f"Request {request_id} initially classified for {tier.name} processing with intent={intent.name}, complexity={complexity.name}, confidence={confidence:.2f}")
            
            # Try to get a processor using the cascade pattern
            processor_start = time.time()
            processor_response = await self._process_with_cascade(classified_request, tier)
            processor_time = time.time() - processor_start
            self.logger.debug(f"Request processed in {processor_time:.3f}s: {request_id}")
            
            # Check if the response is a special error message that should be returned directly
            if isinstance(processor_response, str) and "All AI services are currently disabled" in processor_response:
                self.logger.warning(f"Returning error message directly: {processor_response}")
                return processor_response
            
            # Extract text from dictionary response if needed
            if isinstance(processor_response, dict):
                if 'response_text' in processor_response:
                    response_text = processor_response['response_text']
                else:
                    # Try common fields
                    for field in ['text', 'content', 'response', 'generated_text']:
                        if field in processor_response:
                            response_text = processor_response[field]
                            break
                    else:
                        # If no recognized fields, convert to string
                        response_text = str(processor_response)
            else:
                response_text = processor_response
            
            # Format the response
            self.logger.debug(f"Formatting response: {request_id}")
            format_start = time.time()
            response = self.response_formatter.format_response(
                processor_response=response_text,
                classified_request=classified_request
            )
            format_time = time.time() - format_start
            self.logger.debug(f"Response formatted in {format_time:.3f}s (length: {len(response)}): {request_id}")
            
            # Update conversation context if provided
            if conversation_context:
                self.logger.debug(f"Updating conversation context: {request_id}")
                # Create a companion response object
                companion_response = CompanionResponse(
                    request_id=request.request_id,
                    response_text=response,
                    intent=intent,
                    processing_tier=tier
                )
                
                # Add the interaction to the conversation context
                conversation_context.add_interaction(request, companion_response)
                self.logger.debug(f"Conversation context updated, history size: {len(conversation_context.request_history)}: {request_id}")
            
            total_time = time.time() - start_time
            self.logger.info(f"Request handled successfully in {total_time:.3f}s: {request_id}")
            return response
            
        except Exception as e:
            # Log the error
            total_time = time.time() - start_time
            self.logger.error(f"Error handling request after {total_time:.3f}s: {str(e)}: {request_id}")
            self.logger.debug(traceback.format_exc())
            
            # Return a fallback response
            return f"I'm sorry, I encountered an error while processing your request. Please try again."
    
    async def _process_with_cascade(self, request: ClassifiedRequest, initial_tier: ProcessingTier) -> Dict[str, Any]:
        """
        Process a request with the specified tier, cascading to lower tiers if needed.
        
        Args:
            request: The request to process
            initial_tier: The initial processing tier to try
            
        Returns:
            The processor response
        """
        # Get the cascade order
        tier_progression = self._get_cascade_order(initial_tier)
        
        # Start from the initial tier's position in the progression
        try:
            start_index = tier_progression.index(initial_tier)
        except ValueError:
            # If not found, start with tier 1
            start_index = 0
        
        # Try tiers in progression order
        for tier_index in range(start_index, len(tier_progression)):
            current_tier = tier_progression[tier_index]
            
            try:
                # Attempt to process with the current tier
                self.logger.debug(f"Attempting to process request {request.request_id} with {current_tier}")
                
                # Try to get a processor for the current tier
                try:
                    processor = self.processor_factory.get_processor(current_tier)
                    self.logger.debug(f"Got processor of type {type(processor).__name__} for {current_tier}")
                except ValueError as e:
                    # If the tier is disabled in configuration, log and skip to next tier
                    if "disabled in configuration" in str(e):
                        self.logger.warning(f"Tier {current_tier} is disabled in configuration, skipping to next tier")
                        continue
                    else:
                        # Other ValueError, re-raise
                        raise
                
                # Process the request
                self.logger.info(f"Processing request {request.request_id} with {current_tier} processor")
                response = await processor.process(request)
                
                # Update the processing tier
                request.processing_tier = current_tier
                return response
                
            except Exception as e:
                # Log the error and try the next tier
                self.logger.warning(f"Failed to process request {request.request_id} with {current_tier} processor: {str(e)}")
                # Continue to next tier in progression
        
        # If we've tried all tiers and none worked, generate a fallback response
        self.logger.warning(f"All processing tiers failed for request {request.request_id}, generating fallback response")
        request.processing_tier = ProcessingTier.RULE
        return self._generate_fallback_response(request)
    
    def _generate_fallback_response(self, request: ClassifiedRequest) -> str:
        # Implement the logic to generate a fallback response based on the request
        # This is a placeholder and should be replaced with the actual implementation
        return "I'm sorry, I encountered an error while processing your request. Please try again."

    def _get_cascade_order(self, preferred_tier: ProcessingTier) -> list:
        """
        Get the cascade order for a preferred tier.
        
        Args:
            preferred_tier: The preferred tier level
            
        Returns:
            List of tier levels in cascade order
        """
        # Start with the preferred tier
        order = [preferred_tier]
        
        # Add the remaining tiers in a sensible order based on the preferred tier
        if preferred_tier == ProcessingTier.TIER_1:
            order.extend([ProcessingTier.TIER_2, ProcessingTier.TIER_3])
        elif preferred_tier == ProcessingTier.TIER_2:
            order.extend([ProcessingTier.TIER_3, ProcessingTier.TIER_1])
        elif preferred_tier == ProcessingTier.TIER_3:
            order.extend([ProcessingTier.TIER_2, ProcessingTier.TIER_1])
        elif preferred_tier == ProcessingTier.RULE:
            # If RULE is preferred, try the AI tiers first in order of complexity
            order = [ProcessingTier.TIER_1, ProcessingTier.TIER_2, ProcessingTier.TIER_3, ProcessingTier.RULE]
        
        return order

    def _is_tier_enabled(self, tier: ProcessingTier, processor) -> bool:
        """Check if a tier is enabled in the configuration"""
        # Try to access the config attribute if it exists
        if hasattr(processor, 'config'):
            return processor.config.get('enabled', False)
        
        # Fallback to checking via the processor factory
        try:
            # This assumes processor_factory has a method to check if a tier is enabled
            return self.processor_factory.is_tier_enabled(tier)
        except AttributeError:
            # If no method exists, we can't determine if it's enabled
            # Default to trying it anyway
            return True 