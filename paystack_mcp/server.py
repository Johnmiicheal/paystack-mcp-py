"""
Main MCP server for Paystack integration.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
import json

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource, 
    LoggingLevel
)
import mcp.types as types

from .client import paystack_client, PaystackAPIError
from .models import TransactionRequest, Customer, Plan, RefundRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("paystack-mcp")

# Create the server instance
server = Server("paystack-mcp")


@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="paystack://docs/api",
            name="Paystack API Documentation",
            description="Access to Paystack API endpoints and documentation"
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Handle resource reading requests."""
    if uri == "paystack://docs/api":
        return """
        # Paystack MCP Server
        
        This MCP server provides access to Paystack payment processing API.
        
        ## Available Tools:
        - initialize_transaction: Create a new payment transaction
        - verify_transaction: Verify payment status
        - list_transactions: Get transaction history
        - create_customer: Create new customer
        - list_customers: Get customer list
        - create_plan: Create subscription plan
        - list_plans: Get subscription plans
        - list_banks: Get supported banks
        - resolve_account: Verify bank account details
        - create_refund: Process refunds
        """
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="initialize_transaction",
            description="Initialize a new payment transaction",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "Customer email"},
                    "amount": {"type": "integer", "description": "Amount in kobo/cents"},
                    "currency": {"type": "string", "default": "NGN", "description": "Currency code"},
                    "reference": {"type": "string", "description": "Unique transaction reference"},
                    "callback_url": {"type": "string", "description": "Callback URL after payment"},
                    "metadata": {"type": "object", "description": "Additional transaction data"}
                },
                "required": ["email", "amount"]
            }
        ),
        Tool(
            name="verify_transaction",
            description="Verify a transaction by reference",
            inputSchema={
                "type": "object",
                "properties": {
                    "reference": {"type": "string", "description": "Transaction reference to verify"}
                },
                "required": ["reference"]
            }
        ),
        Tool(
            name="list_transactions",
            description="List transactions with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "per_page": {"type": "integer", "default": 50, "description": "Number of results per page"},
                    "page": {"type": "integer", "default": 1, "description": "Page number"},
                    "customer": {"type": "string", "description": "Filter by customer ID"},
                    "status": {"type": "string", "description": "Filter by transaction status"},
                    "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                }
            }
        ),
        Tool(
            name="create_customer",
            description="Create a new customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "Customer email"},
                    "first_name": {"type": "string", "description": "Customer first name"},
                    "last_name": {"type": "string", "description": "Customer last name"},
                    "phone": {"type": "string", "description": "Customer phone number"},
                    "metadata": {"type": "object", "description": "Additional customer data"}
                },
                "required": ["email"]
            }
        ),
        Tool(
            name="list_customers",
            description="List customers",
            inputSchema={
                "type": "object",
                "properties": {
                    "per_page": {"type": "integer", "default": 50, "description": "Number of results per page"},
                    "page": {"type": "integer", "default": 1, "description": "Page number"}
                }
            }
        ),
        Tool(
            name="create_plan",
            description="Create a subscription plan",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Plan name"},
                    "amount": {"type": "integer", "description": "Plan amount in kobo/cents"},
                    "interval": {"type": "string", "description": "Billing interval", 
                              "enum": ["daily", "weekly", "monthly", "quarterly", "biannually", "annually"]},
                    "description": {"type": "string", "description": "Plan description"},
                    "currency": {"type": "string", "default": "NGN", "description": "Currency code"}
                },
                "required": ["name", "amount", "interval"]
            }
        ),
        Tool(
            name="list_plans",
            description="List subscription plans",
            inputSchema={
                "type": "object",
                "properties": {
                    "per_page": {"type": "integer", "default": 50, "description": "Number of results per page"},
                    "page": {"type": "integer", "default": 1, "description": "Page number"}
                }
            }
        ),
        Tool(
            name="list_banks",
            description="List supported banks",
            inputSchema={
                "type": "object",
                "properties": {
                    "country": {"type": "string", "default": "nigeria", "description": "Country to get banks for"}
                }
            }
        ),
        Tool(
            name="resolve_account",
            description="Resolve and verify bank account details",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_number": {"type": "string", "description": "Account number to verify"},
                    "bank_code": {"type": "string", "description": "Bank code"}
                },
                "required": ["account_number", "bank_code"]
            }
        ),
        Tool(
            name="create_refund",
            description="Create a refund for a transaction",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction": {"type": "string", "description": "Transaction ID or reference"},
                    "amount": {"type": "integer", "description": "Amount to refund in kobo/cents (full amount if not specified)"},
                    "currency": {"type": "string", "description": "Currency code"},
                    "customer_note": {"type": "string", "description": "Note for customer"},
                    "merchant_note": {"type": "string", "description": "Internal merchant note"}
                },
                "required": ["transaction"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
    """Handle tool calls."""
    try:
        if name == "initialize_transaction":
            transaction_request = TransactionRequest(**arguments)
            result = await paystack_client.initialize_transaction(transaction_request)
            return [types.TextContent(
                type="text",
                text=f"Transaction initialized successfully:\n{json.dumps(result, indent=2)}"
            )]
        
        elif name == "verify_transaction":
            reference = arguments["reference"]
            result = await paystack_client.verify_transaction(reference)
            return [types.TextContent(
                type="text",
                text=f"Transaction verification result:\n{json.dumps(result, indent=2)}"
            )]
        
        elif name == "list_transactions":
            result = await paystack_client.list_transactions(**arguments)
            return [types.TextContent(
                type="text",
                text=f"Transactions list:\n{json.dumps(result, indent=2)}"
            )]
        
        elif name == "create_customer":
            customer = Customer(**arguments)
            result = await paystack_client.create_customer(customer)
            return [types.TextContent(
                type="text",
                text=f"Customer created successfully:\n{json.dumps(result, indent=2)}"
            )]
        
        elif name == "list_customers":
            result = await paystack_client.list_customers(**arguments)
            return [types.TextContent(
                type="text",
                text=f"Customers list:\n{json.dumps(result, indent=2)}"
            )]
        
        elif name == "create_plan":
            plan = Plan(**arguments)
            result = await paystack_client.create_plan(plan)
            return [types.TextContent(
                type="text",
                text=f"Plan created successfully:\n{json.dumps(result, indent=2)}"
            )]
        
        elif name == "list_plans":
            result = await paystack_client.list_plans(**arguments)
            return [types.TextContent(
                type="text",
                text=f"Plans list:\n{json.dumps(result, indent=2)}"
            )]
        
        elif name == "list_banks":
            result = await paystack_client.list_banks(**arguments)
            return [types.TextContent(
                type="text",
                text=f"Banks list:\n{json.dumps(result, indent=2)}"
            )]
        
        elif name == "resolve_account":
            result = await paystack_client.resolve_account(**arguments)
            return [types.TextContent(
                type="text",
                text=f"Account resolution result:\n{json.dumps(result, indent=2)}"
            )]
        
        elif name == "create_refund":
            refund_request = RefundRequest(**arguments)
            result = await paystack_client.create_refund(refund_request)
            return [types.TextContent(
                type="text",
                text=f"Refund created successfully:\n{json.dumps(result, indent=2)}"
            )]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except PaystackAPIError as e:
        return [types.TextContent(
            type="text",
            text=f"Paystack API Error: {e.message}\nStatus Code: {e.status_code}\nResponse: {e.response_data}"
        )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Main function to run the server."""
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="paystack-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


# Export the app for use in other modules
app = server

if __name__ == "__main__":
    asyncio.run(main()) 