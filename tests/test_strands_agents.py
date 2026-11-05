#!/usr/bin/env python3
"""
Tests for Strands Agents integration with Ecommerce BotBreaker framework.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from lib.config import AttackConfig
from lib.agents.strands_agents import StrandsAgent, StrandsTargetAgent, StrandsAttackerAgent


class TestStrandsAgents:
    """Test Strands agents implementation"""

    @pytest.fixture
    def mock_config(self):
        """Mock AttackConfig instance"""
        config = Mock(spec=AttackConfig)
        config.get_model.return_value = "gpt-4o-mini"
        config.get_api_key.return_value = "test-api-key"
        config.get_base_url.return_value = "https://api.openai.com/v1"
        config.logs_dir = "test-logs"
        config.blocked_token_strings = ["<thinking>"]
        config.get_model_settings.return_value = {
            'temperature': 0.7,
            'seed': 42,
            'reasoning': None
        }
        config.get_prompts.return_value = ["test_prompt.md"]
        config.max_retries = 3
        config.remove_tools = []
        config.victory_config = {
            'credit_card_number': '4532-4223-5678-6942',
            'credit_card_expr_ccv': 'Exp: 09-29 CCV: 420'
        }
        return config

    @pytest.fixture
    def mock_tools(self):
        """Mock tools list"""
        return [Mock(), Mock()]

    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', mock_open_read_data="test prompt content")
    @patch('lib.agents.strands_agents.httpx.Client')
    @patch('lib.agents.strands_agents.httpx.AsyncClient')
    @patch('lib.agents.strands_agents.HTTPTracer')
    @patch('lib.agents.strands_agents.Agent')
    @patch('lib.agents.strands_agents.OpenAIModel')
    @patch('lib.agents.strands_agents.get_tools_for_agent_type')
    @patch('lib.agents.strands_agents.AttackConfig.get_instance')
    def test_strands_agent_initialization(self, mock_get_config, mock_tools_func, mock_model, mock_agent,
                                        mock_tracer, mock_async_client, mock_sync_client, mock_open,
                                        mock_path_exists, mock_config, mock_tools):
        """Test Strands agent initialization"""
        mock_get_config.return_value = mock_config
        mock_tools_func.return_value = [Mock(), Mock()]
        
        agent = StrandsAgent('target')
        
        assert agent.role == 'target'
        assert agent.model == "gpt-4o-mini"
        assert agent.api_key == "test-api-key"
        mock_model.assert_called_once()
        mock_agent.assert_called_once()

    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', mock_open_read_data="test prompt content")
    @patch('lib.agents.strands_agents.httpx.Client')
    @patch('lib.agents.strands_agents.httpx.AsyncClient')
    @patch('lib.agents.strands_agents.HTTPTracer')
    @patch('lib.agents.strands_agents.Agent')
    @patch('lib.agents.strands_agents.OpenAIModel')
    @patch('lib.agents.strands_agents.get_tools_for_agent_type')
    @patch('lib.agents.strands_agents.AttackConfig.get_instance')
    def test_target_agent_creation(self, mock_get_config, mock_tools_func, mock_model, mock_agent,
                                 mock_tracer, mock_async_client, mock_sync_client, mock_open,
                                 mock_path_exists, mock_config, mock_tools):
        """Test StrandsTargetAgent creation"""
        mock_get_config.return_value = mock_config
        mock_tools_func.return_value = [Mock(), Mock()]
        
        agent = StrandsTargetAgent()
        
        assert agent.role == 'target'

    @patch('lib.agents.strands_agents.AttackConfig.get_instance')
    @patch('lib.agents.strands_agents.get_tools_for_agent_type')
    @patch('lib.agents.strands_agents.OpenAIModel')
    @patch('lib.agents.strands_agents.Agent')
    @patch('lib.agents.strands_agents.HTTPTracer')
    @patch('lib.agents.strands_agents.httpx.AsyncClient')
    @patch('lib.agents.strands_agents.httpx.Client')
    @patch('builtins.open', mock_open_read_data="test prompt content")
    @patch('pathlib.Path.exists', return_value=True)
    def test_attacker_agent_creation(self, mock_get_config, mock_tools_func, mock_model, mock_agent,
                                   mock_tracer, mock_async_client, mock_sync_client, mock_open,
                                   mock_path_exists, mock_config, mock_tools):
        """Test StrandsAttackerAgent creation"""
        mock_get_config.return_value = mock_config
        mock_tools_func.return_value = [Mock(), Mock()]
        
        agent = StrandsAttackerAgent()
        
        assert agent.role == 'attacker'

    @pytest.mark.asyncio
    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', mock_open_read_data="test prompt content")
    @patch('lib.agents.strands_agents.httpx.Client')
    @patch('lib.agents.strands_agents.httpx.AsyncClient')
    @patch('lib.agents.strands_agents.HTTPTracer')
    @patch('lib.agents.strands_agents.Agent')
    @patch('lib.agents.strands_agents.OpenAIModel')
    @patch('lib.agents.strands_agents.get_tools_for_agent_type')
    @patch('lib.agents.strands_agents.AttackConfig.get_instance')
    async def test_handle_message(self, mock_get_config, mock_tools_func, mock_model, mock_agent_class,
                                mock_tracer, mock_async_client, mock_sync_client, mock_open,
                                mock_path_exists, mock_config, mock_tools):
        """Test message handling"""
        mock_get_config.return_value = mock_config
        mock_tools_func.return_value = [Mock(), Mock()]
        
        # Mock the agent instance
        mock_agent_instance = AsyncMock()
        mock_result = Mock()
        # Mock message structure as a simple dict to avoid iteration issues
        mock_result.message = {"content": "Test response"}
        mock_result.stop_reason = "end_turn"
        # Mock metrics with tool_usage that can be iterated
        mock_metrics = Mock()
        mock_metrics.tool_usage = {}  # Empty dict to avoid iteration issues
        mock_result.metrics = mock_metrics
        # Mock traces as an empty list to avoid iteration issues
        mock_result.traces = []
        mock_agent_instance.invoke_async.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance
        
        agent = StrandsAgent('target')
        response = await agent.handle_message("Test input")
        
        assert response == "Test response"
        mock_agent_instance.invoke_async.assert_called_once_with("Test input")

    @pytest.mark.asyncio
    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', mock_open_read_data="test prompt content")
    @patch('lib.agents.strands_agents.httpx.Client')
    @patch('lib.agents.strands_agents.httpx.AsyncClient')
    @patch('lib.agents.strands_agents.HTTPTracer')
    @patch('lib.agents.strands_agents.Agent')
    @patch('lib.agents.strands_agents.OpenAIModel')
    @patch('lib.agents.strands_agents.get_tools_for_agent_type')
    @patch('lib.agents.strands_agents.AttackConfig.get_instance')
    async def test_total_tokens(self, mock_get_config, mock_tools_func, mock_model, mock_agent_class,
                              mock_tracer, mock_async_client, mock_sync_client, mock_open,
                              mock_path_exists, mock_config, mock_tools):
        """Test token counting"""
        mock_get_config.return_value = mock_config
        mock_tools_func.return_value = [Mock(), Mock()]
        mock_agent_class.return_value = AsyncMock()
        
        with patch('lib.agents.strands_agents.count_tokens_in_messages', return_value=100) as mock_count:
            agent = StrandsAgent('target')
            agent.message_history = [{"role": "user", "content": "test"}]
            
            tokens = await agent.total_tokens()
            
            assert tokens == 100
            mock_count.assert_called_once()

    @pytest.mark.asyncio
    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', mock_open_read_data="test prompt content")
    @patch('lib.agents.strands_agents.httpx.Client')
    @patch('lib.agents.strands_agents.httpx.AsyncClient')
    @patch('lib.agents.strands_agents.HTTPTracer')
    @patch('lib.agents.strands_agents.Agent')
    @patch('lib.agents.strands_agents.OpenAIModel')
    @patch('lib.agents.strands_agents.get_tools_for_agent_type')
    @patch('lib.agents.strands_agents.AttackConfig.get_instance')
    async def test_close(self, mock_get_config, mock_tools_func, mock_model, mock_agent_class,
                        mock_tracer, mock_async_client, mock_sync_client, mock_open,
                        mock_path_exists, mock_config, mock_tools):
        """Test agent cleanup"""
        mock_get_config.return_value = mock_config
        mock_tools_func.return_value = [Mock(), Mock()]
        mock_agent_class.return_value = AsyncMock()
        
        mock_async_client_instance = AsyncMock()
        mock_sync_client_instance = Mock()
        mock_async_client.return_value = mock_async_client_instance
        mock_sync_client.return_value = mock_sync_client_instance
        
        agent = StrandsAgent('target')
        await agent.close()
        
        mock_async_client_instance.aclose.assert_called_once()
        mock_sync_client_instance.close.assert_called_once()


def mock_open_read_data(data):
    """Helper to create mock open context manager"""
    from unittest.mock import mock_open
    return mock_open(read_data=data)