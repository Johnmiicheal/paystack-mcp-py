"""
Tests for the Paystack MCP server.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from paystack_mcp.server import server
from paystack_mcp.models import TransactionRequest, Customer


class TestPaystackMCPServer:
    """Test cases for Paystack MCP server."""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that tools are properly listed."""
        tools = await server.call_list_tools()
        assert len(tools) > 0
        
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "initialize_transaction",
            "verify_transaction", 
            "list_transactions",
            "create_customer",
            "list_customers",
            "create_plan",
            "list_plans",
            "list_banks",
            "resolve_account",
            "create_refund"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Test that resources are properly listed."""
        resources = await server.call_list_resources()
        assert len(resources) > 0
        assert resources[0].uri == "paystack://docs/api"
    
    @pytest.mark.asyncio
    @patch('paystack_mcp.server.paystack_client.initialize_transaction')
    async def test_initialize_transaction_tool(self, mock_initialize):
        """Test the initialize_transaction tool."""
        # Mock the API response
        mock_response = {
            "status": True,
            "message": "Authorization URL created",
            "data": {
                "authorization_url": "https://checkout.paystack.com/test123",
                "access_code": "test_access_code",
                "reference": "test_ref_123"
            }
        }
        mock_initialize.return_value = mock_response
        
        # Test the tool call
        arguments = {
            "email": "test@example.com",
            "amount": 50000,  # 500 NGN in kobo
            "currency": "NGN"
        }
        
        result = await server.call_call_tool("initialize_transaction", arguments)
        
        # Verify the mock was called
        mock_initialize.assert_called_once()
        
        # Verify the result
        assert len(result) == 1
        assert "Transaction initialized successfully" in result[0].text
        assert "authorization_url" in result[0].text
    
    @pytest.mark.asyncio
    @patch('paystack_mcp.server.paystack_client.create_customer')
    async def test_create_customer_tool(self, mock_create_customer):
        """Test the create_customer tool."""
        # Mock the API response
        mock_response = {
            "status": True,
            "message": "Customer created",
            "data": {
                "email": "test@example.com",
                "customer_code": "CUS_test123",
                "id": 123
            }
        }
        mock_create_customer.return_value = mock_response
        
        # Test the tool call
        arguments = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        result = await server.call_call_tool("create_customer", arguments)
        
        # Verify the mock was called
        mock_create_customer.assert_called_once()
        
        # Verify the result
        assert len(result) == 1
        assert "Customer created successfully" in result[0].text
        assert "customer_code" in result[0].text 