#!/usr/bin/env python3
"""
Abstract base class for Ecommerce BotBreaker agents.
"""

import tiktoken
import asyncio

from abc import ABC, abstractmethod
from lib.logging import HTTPTracer

class BotBreakerAgent(ABC):
    """
    Abstract base class for all agents in the Ecommerce BotBreaker framework.
    Defines the common interface that all agents must implement.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the agent."""
        # Default attributes that all agents should have
        # Create a default HTTPTracer - subclasses can override
        self.http_tracer = HTTPTracer(None)
        self.model_tokens = []

    @abstractmethod
    async def handle_message(self, input_prompt: str) -> str:
        """
        Process an input message and return a response.

        Args:
            input_prompt: The input message to process

        Returns:
            The agent's response as a string
        """
        pass

    @abstractmethod
    async def total_tokens(self) -> int:
        """
        Get the total number of tokens used by this agent.

        Returns:
            The total token count
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Clean up resources used by the agent.
        """
        pass

# This is agent-agnostic but lives here until we support other agent frameworks
async def count_tokens_in_messages(model: str, messages: list) -> int:
    """Count the number of tokens in a list of messages, including tool calls."""
    # Get the encoding for the current model
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base encoding if model is not found
        encoding = tiktoken.get_encoding("cl100k_base")

    async def count_message_tokens(message):
        if not isinstance(message, dict):
            return 0
        num_tokens = 0
        # Count tokens in message content
        if "content" in message and message["content"]:
            num_tokens += await asyncio.to_thread(lambda: len(encoding.encode(str(message["content"]), disallowed_special=())))

        # Count tokens in tool calls
        if "tool_calls" in message and message["tool_calls"]:
            for tool_call in message["tool_calls"]:
                # Count tokens in tool call id
                if "id" in tool_call:
                    num_tokens += await asyncio.to_thread(lambda: len(encoding.encode(str(tool_call["id"]), disallowed_special=())))

                # Count tokens in tool call type
                if "type" in tool_call:
                    num_tokens += await asyncio.to_thread(lambda: len(encoding.encode(str(tool_call["type"]), disallowed_special=())))

                # Count tokens in function name and arguments
                if "function" in tool_call:
                    function_data = tool_call["function"]
                    if "name" in function_data:
                        num_tokens += await asyncio.to_thread(lambda: len(encoding.encode(str(function_data["name"]), disallowed_special=())))
                    if "arguments" in function_data:
                        num_tokens += await asyncio.to_thread(lambda: len(encoding.encode(str(function_data["arguments"]), disallowed_special=())))

        return num_tokens

    # Process all messages concurrently to avoid blocking
    tasks = [count_message_tokens(message) for message in messages]
    token_counts = await asyncio.gather(*tasks)
    return sum(token_counts)