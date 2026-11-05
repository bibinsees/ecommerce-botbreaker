#!/usr/bin/env python3
"""
Agent factory for Ecommerce BotBreaker framework.
Creates appropriate agent instances based on configuration.
"""

from typing import Optional
from lib.config import AttackConfig
from lib.agents.agent import BotBreakerAgent


def create_agent(role: str, persona_file: Optional[str] = None, goal_file: Optional[str] = None) -> BotBreakerAgent:
    """
    Create an agent instance based on configuration.
    
    Args:
        role: Role of the agent ('target', 'attacker', 'redteam')
        persona_file: Optional persona file for target agents
        goal_file: Optional goal file for attacker agents
        
    Returns:
        BotBreakerAgent instance
    """
    config = AttackConfig.get_instance()
    agent_type = config.get_agent_type(role)
    
    # Map role aliases
    if role == 'redteam':
        role = 'attacker'
    
    if agent_type == 'openai_agents':
        return _create_openai_agent(role, persona_file, goal_file)
    elif agent_type == 'langchain_react':
        return _create_langchain_react_agent(role, persona_file, goal_file)
    elif agent_type == 'strands_agents':
        return _create_strands_agent(role, persona_file, goal_file)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")


def _create_openai_agent(role: str, persona_file: Optional[str], goal_file: Optional[str]) -> BotBreakerAgent:
    """Create OpenAI Agents framework agent"""
    from lib.agents.openai_agents import OpenAITargetAgent, OpenAIAttackerAgent
    
    if role == 'target':
        return OpenAITargetAgent(persona_file=persona_file)
    elif role == 'attacker':
        return OpenAIAttackerAgent(goal_file=goal_file)
    else:
        raise ValueError(f"Unknown role for OpenAI agent: {role}")


def _create_langchain_react_agent(role: str, persona_file: Optional[str], goal_file: Optional[str]) -> BotBreakerAgent:
    """Create LangChain ReActAgent"""
    from lib.agents.langchain_agents import (
        LangChainTargetReActAgent,
        LangChainAttackerReActAgent
    )
    
    if role == 'target':
        return LangChainTargetReActAgent(persona_file=persona_file)
    elif role == 'attacker':
        return LangChainAttackerReActAgent(goal_file=goal_file)
    else:
        raise ValueError(f"Unknown role for LangChain ReAct agent: {role}")


def _create_strands_agent(role: str, persona_file: Optional[str], goal_file: Optional[str]) -> BotBreakerAgent:
    """Create Strands agent"""
    from lib.agents.strands_agents import (
        StrandsTargetAgent,
        StrandsAttackerAgent
    )
    
    if role == 'target':
        return StrandsTargetAgent(persona_file=persona_file)
    elif role == 'attacker':
        return StrandsAttackerAgent(goal_file=goal_file)
    else:
        raise ValueError(f"Unknown role for Strands agent: {role}")


def get_available_agent_types() -> dict:
    """Get dictionary of available agent types and their descriptions"""
    return {
        'openai_agents': 'OpenAI Agents framework with function tools and reasoning',
        'langchain_react': 'LangChain ReAct agent using LangGraph',
        'strands_agents': 'Strands Agents SDK with async invoke and tool integration'
    }


def validate_agent_type(agent_type: str) -> bool:
    """Validate if agent type is supported"""
    return agent_type in get_available_agent_types()


# Convenience functions for backward compatibility
def create_target_agent(persona_file: Optional[str] = None) -> BotBreakerAgent:
    """Create a target agent using configured agent type"""
    return create_agent('target', persona_file=persona_file)


def create_attacker_agent(goal_file: Optional[str] = None) -> BotBreakerAgent:
    """Create an attacker agent using configured agent type"""
    return create_agent('attacker', goal_file=goal_file)