#!/usr/bin/env python3
"""
Tests for Strands tool conversion functionality.
"""

import pytest
from unittest.mock import Mock, patch
from lib.agents.tool_converter import (
    convert_to_strands_tools,
    get_tools_for_agent_type,
    get_attacker_tool_functions,
    get_target_tool_functions
)


class TestStrandsToolConverter:
    """Test Strands tool conversion functionality"""

    def test_get_attacker_tool_functions(self):
        """Test getting attacker tool functions"""
        tools = get_attacker_tool_functions()
        
        assert len(tools) > 0
        # Verify some key attacker tools are present
        tool_names = [func.__name__ for func in tools]
        assert 'add_review' in tool_names
        assert 'make_web_page' in tool_names
        assert 'declare_victory' in tool_names

    def test_get_target_tool_functions(self):
        """Test getting target tool functions"""
        tools = get_target_tool_functions()
        
        assert len(tools) > 0
        # Verify some key target tools are present
        tool_names = [func.__name__ for func in tools]
        assert 'invoice_user' in tool_names
        assert 'make_purchase' in tool_names
        assert 'search_web' in tool_names

    @patch('lib.agents.tool_converter.strands_tool')
    def test_convert_to_strands_tools(self, mock_strands_tool):
        """Test converting functions to Strands tools"""
        # Mock strands tool decorator
        def mock_decorator(func):
            decorated_func = Mock()
            decorated_func.__name__ = func.__name__
            return decorated_func
        
        mock_strands_tool.side_effect = mock_decorator
        
        # Test functions
        def test_func1():
            pass
        
        def test_func2():
            pass
        
        tool_functions = [test_func1, test_func2]
        tools = convert_to_strands_tools(tool_functions)
        
        assert len(tools) == 2
        assert mock_strands_tool.call_count == 2

    @patch('lib.agents.tool_converter.strands_tool')
    def test_convert_to_strands_tools_with_removal(self, mock_strands_tool):
        """Test converting functions to Strands tools with tool removal"""
        # Mock strands tool decorator
        def mock_decorator(func):
            decorated_func = Mock()
            decorated_func.__name__ = func.__name__
            return decorated_func
        
        mock_strands_tool.side_effect = mock_decorator
        
        # Test functions
        def test_func1():
            pass
        
        def test_func2():
            pass
        
        tool_functions = [test_func1, test_func2]
        remove_tools = ['test_func1']
        tools = convert_to_strands_tools(tool_functions, remove_tools)
        
        # Should have only one tool after removal
        assert len(tools) == 1
        assert tools[0].__name__ == 'test_func2'

    @patch('lib.agents.tool_converter.AttackConfig')
    @patch('lib.agents.tool_converter.convert_to_strands_tools')
    @patch('lib.agents.tool_converter.get_target_tool_functions')
    def test_get_tools_for_agent_type_strands_target(self, mock_get_target_tools, mock_convert, mock_config_class):
        """Test getting tools for Strands target agent"""
        # Mock the config instance
        mock_config = Mock()
        mock_config.get_remove_tools.return_value = []
        mock_config_class.get_instance.return_value = mock_config
        
        mock_tools = [Mock(), Mock()]
        mock_get_target_tools.return_value = mock_tools
        mock_convert.return_value = mock_tools
        
        result = get_tools_for_agent_type('strands_agents', 'target')
        
        mock_get_target_tools.assert_called_once()
        mock_config.get_remove_tools.assert_called_once_with('target')
        mock_convert.assert_called_once_with(mock_tools, [])
        assert result == mock_tools

    @patch('lib.agents.tool_converter.AttackConfig')
    @patch('lib.agents.tool_converter.convert_to_strands_tools')
    @patch('lib.agents.tool_converter.get_attacker_tool_functions')
    def test_get_tools_for_agent_type_strands_attacker(self, mock_get_attacker_tools, mock_convert, mock_config_class):
        """Test getting tools for Strands attacker agent"""
        # Mock the config instance
        mock_config = Mock()
        mock_config.get_remove_tools.return_value = []
        mock_config_class.get_instance.return_value = mock_config
        
        mock_tools = [Mock(), Mock()]
        mock_get_attacker_tools.return_value = mock_tools
        mock_convert.return_value = mock_tools
        
        result = get_tools_for_agent_type('strands_agents', 'attacker')
        
        mock_get_attacker_tools.assert_called_once()
        mock_config.get_remove_tools.assert_called_once_with('attacker')
        mock_convert.assert_called_once_with(mock_tools, [])
        assert result == mock_tools

    @patch('lib.agents.tool_converter.AttackConfig')
    @patch('lib.agents.tool_converter.convert_to_strands_tools')
    @patch('lib.agents.tool_converter.get_attacker_tool_functions')
    def test_get_tools_for_agent_type_with_removal(self, mock_get_attacker_tools, mock_convert, mock_config_class):
        """Test getting tools for Strands agent with tool removal"""
        # Mock the config instance
        mock_config = Mock()
        remove_tools = ['declare_victory']
        mock_config.get_remove_tools.return_value = remove_tools
        mock_config_class.get_instance.return_value = mock_config
        
        mock_tools = [Mock(), Mock()]
        mock_get_attacker_tools.return_value = mock_tools
        mock_convert.return_value = mock_tools
        
        result = get_tools_for_agent_type('strands_agents', 'attacker')
        
        mock_get_attacker_tools.assert_called_once()
        mock_config.get_remove_tools.assert_called_once_with('attacker')
        mock_convert.assert_called_once_with(mock_tools, remove_tools)
        assert result == mock_tools

    def test_get_tools_for_agent_type_invalid_agent_type(self):
        """Test error handling for invalid agent type"""
        with pytest.raises(ValueError, match="Unknown agent type"):
            get_tools_for_agent_type('invalid_agent_type', 'target')

    def test_get_tools_for_agent_type_invalid_role(self):
        """Test error handling for invalid role"""
        with pytest.raises(ValueError, match="Unknown role"):
            get_tools_for_agent_type('strands_agents', 'invalid_role')