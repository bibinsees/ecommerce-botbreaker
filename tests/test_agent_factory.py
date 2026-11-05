#!/usr/bin/env python3
"""
Tests for agent factory functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from lib.config import AttackConfig
from lib.agents.agent_factory import (
    create_agent, 
    get_available_agent_types, 
    validate_agent_type,
    create_target_agent,
    create_attacker_agent
)
from lib.agents.agent import BotBreakerAgent


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing"""
    config_content = """
redteam:
  model: google/gemini-2.5-pro
  agent_type: openai_agents
  prompts:
    - system_prompts/attacker/attacker.md
  remove_tools: []
  message_bells: 2

target:
  model: openai/gpt-oss-20b
  agent_type: openai_agents
  prompt: system_prompts/sales_agent/shopping_agent.md
  blocked_token_strings: []

search:
  model: meta-llama/llama-4-scout
  prompt: system_prompts/search_agent.md

editor:
  model: x-ai/grok-code-fast-1
  temperature: 0.3

duration_limits:
  max_turns: 500
  max_retries: 3
  max_attacker_context_tokens: 1000000
  max_target_context_tokens: 128000
  max_target_context_bytes: 20000

victory:
  credit_card_number: 4532-4223-5678-6942
  credit_card_expr_ccv: "Exp: 09-29 CCV: 420"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    os.unlink(temp_file)


@pytest.fixture
def mock_config(temp_config_file):
    """Initialize AttackConfig with temporary config"""
    # Reset singleton
    AttackConfig._instance = None
    AttackConfig._initialized = False
    
    # Set required environment variables
    env_vars = {
        'TARGET_OPENAI_API_KEY': 'test-key',
        'ATTACKER_OPENAI_API_KEY': 'test-key', 
        'SEARCH_OPENAI_API_KEY': 'test-key',
        'EDITOR_OPENAI_API_KEY': 'test-key'
    }
    
    with patch.dict(os.environ, env_vars):
        config = AttackConfig.initialize(temp_config_file)
        yield config


def test_get_available_agent_types():
    """Test getting available agent types"""
    types = get_available_agent_types()
    
    assert isinstance(types, dict)
    assert 'openai_agents' in types
    assert 'langchain_react' in types
    
    # Check descriptions are provided
    for agent_type, description in types.items():
        assert isinstance(description, str)
        assert len(description) > 0


def test_validate_agent_type():
    """Test agent type validation"""
    assert validate_agent_type('openai_agents') is True
    assert validate_agent_type('langchain_react') is True
    assert validate_agent_type('invalid_type') is False


@patch('lib.agents.agent_factory._create_openai_agent')
def test_create_agent_openai(mock_create_openai, mock_config):
    """Test creating OpenAI agent"""
    mock_agent = Mock(spec=BotBreakerAgent)
    mock_create_openai.return_value = mock_agent
    
    agent = create_agent('target', persona_file='test.md')
    
    assert agent == mock_agent
    mock_create_openai.assert_called_once_with('target', 'test.md', None)


@patch('lib.agents.agent_factory._create_langchain_react_agent')
def test_create_agent_langchain_react(mock_create_langchain, mock_config):
    """Test creating LangChain react agent"""
    # Update config to use LangChain react agent
    mock_config.config['target']['agent_type'] = 'langchain_react'
    
    mock_agent = Mock(spec=BotBreakerAgent)
    mock_create_langchain.return_value = mock_agent
    
    agent = create_agent('target', persona_file='test.md')
    
    assert agent == mock_agent
    mock_create_langchain.assert_called_once_with('target', 'test.md', None)


def test_create_agent_invalid_type(mock_config):
    """Test creating agent with invalid type"""
    # Update config to use invalid agent type
    mock_config.config['target']['agent_type'] = 'invalid_type'
    
    with pytest.raises(ValueError, match="Unknown agent type: invalid_type"):
        create_agent('target')


def test_create_agent_invalid_role(mock_config):
    """Test creating agent with invalid role"""
    with pytest.raises(ValueError, match="Unknown role for OpenAI agent: invalid_role"):
        create_agent('invalid_role')


@patch('lib.agents.agent_factory.create_agent')
def test_create_target_agent_convenience(mock_create_agent, mock_config):
    """Test convenience function for target agent"""
    mock_agent = Mock(spec=BotBreakerAgent)
    mock_create_agent.return_value = mock_agent
    
    agent = create_target_agent('test.md')
    
    assert agent == mock_agent
    mock_create_agent.assert_called_once_with('target', persona_file='test.md')


@patch('lib.agents.agent_factory.create_agent')
def test_create_attacker_agent_convenience(mock_create_agent, mock_config):
    """Test convenience function for attacker agent"""
    mock_agent = Mock(spec=BotBreakerAgent)
    mock_create_agent.return_value = mock_agent
    
    agent = create_attacker_agent('goal.md')
    
    assert agent == mock_agent
    mock_create_agent.assert_called_once_with('attacker', goal_file='goal.md')


def test_redteam_role_mapping(mock_config):
    """Test that 'redteam' role maps to 'attacker'"""
    with patch('lib.agents.agent_factory._create_openai_agent') as mock_create:
        mock_agent = Mock(spec=BotBreakerAgent)
        mock_create.return_value = mock_agent
        
        agent = create_agent('redteam', goal_file='test.md')
        
        # Should call with 'attacker' role, not 'redteam'
        mock_create.assert_called_once_with('attacker', None, 'test.md')


if __name__ == '__main__':
    pytest.main([__file__])