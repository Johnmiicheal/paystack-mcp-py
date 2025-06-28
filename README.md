# Paystack MCP Server

A Model Context Protocol (MCP) server for Paystack payment processing. This server provides AI assistants with the ability to interact with Paystack's payment API through standardized tools.

## Features

🚀 **Payment Operations**
- Initialize transactions
- Verify payment status  
- List transaction history
- Process refunds

👥 **Customer Management**
- Create and manage customers
- List customers
- Update customer information

📋 **Subscription Plans**
- Create subscription plans
- List and manage plans

🏦 **Banking Integration**
- List supported banks
- Verify bank account details

## Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd paystack-mcp
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp example.env .env
# Edit .env with your Paystack credentials
```

Required environment variables:
- `PAYSTACK_SECRET_KEY`: Your Paystack secret key (required)
- `PAYSTACK_PUBLIC_KEY`: Your Paystack public key (optional)
- `PAYSTACK_ENVIRONMENT`: Set to 'test' or 'live' (default: 'test')

## Usage

### Running the Server

The MCP server can be run directly:

```bash
python -m paystack_mcp.server
```

Or using the installed script:

```bash
paystack-mcp
```

### JavaScript Client Integration

This Python MCP server can be easily integrated with JavaScript clients. Here's an example:

```javascript
// Using the MCP client in Node.js
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// Create transport to the Python server
const transport = new StdioClientTransport({
  command: "python",
  args: ["-m", "paystack_mcp.server"]
});

// Create and connect client
const client = new Client(
  {
    name: "paystack-client",
    version: "1.0.0",
  },
  {
    capabilities: {},
  }
);

await client.connect(transport);

// Use Paystack tools
const result = await client.callTool({
  name: "initialize_transaction",
  arguments: {
    email: "customer@example.com",
    amount: 50000, // 500 NGN in kobo
    currency: "NGN"
  }
});

console.log(result);
```

## Available Tools

### Transaction Management

#### `initialize_transaction`
Create a new payment transaction.

**Parameters:**
- `email` (string, required): Customer email
- `amount` (integer, required): Amount in kobo/cents
- `currency` (string, optional): Currency code (default: "NGN")
- `reference` (string, optional): Unique transaction reference
- `callback_url` (string, optional): Callback URL after payment
- `metadata` (object, optional): Additional transaction data

#### `verify_transaction`
Verify a transaction by reference.

**Parameters:**
- `reference` (string, required): Transaction reference to verify

#### `list_transactions`
List transactions with optional filters.

**Parameters:**
- `per_page` (integer, optional): Number of results per page (default: 50)
- `page` (integer, optional): Page number (default: 1)
- `customer` (string, optional): Filter by customer ID
- `status` (string, optional): Filter by transaction status
- `from_date` (string, optional): Start date (YYYY-MM-DD)
- `to_date` (string, optional): End date (YYYY-MM-DD)

### Customer Management

#### `create_customer`
Create a new customer.

**Parameters:**
- `email` (string, required): Customer email
- `first_name` (string, optional): Customer first name
- `last_name` (string, optional): Customer last name
- `phone` (string, optional): Customer phone number
- `metadata` (object, optional): Additional customer data

#### `list_customers`
List customers.

**Parameters:**
- `per_page` (integer, optional): Number of results per page (default: 50)
- `page` (integer, optional): Page number (default: 1)

### Subscription Plans

#### `create_plan`
Create a subscription plan.

**Parameters:**
- `name` (string, required): Plan name
- `amount` (integer, required): Plan amount in kobo/cents
- `interval` (string, required): Billing interval (daily, weekly, monthly, quarterly, biannually, annually)
- `description` (string, optional): Plan description
- `currency` (string, optional): Currency code (default: "NGN")

#### `list_plans`
List subscription plans.

**Parameters:**
- `per_page` (integer, optional): Number of results per page (default: 50)
- `page` (integer, optional): Page number (default: 1)

### Banking

#### `list_banks`
List supported banks.

**Parameters:**
- `country` (string, optional): Country to get banks for (default: "nigeria")

#### `resolve_account`
Resolve and verify bank account details.

**Parameters:**
- `account_number` (string, required): Account number to verify
- `bank_code` (string, required): Bank code

### Refunds

#### `create_refund`
Create a refund for a transaction.

**Parameters:**
- `transaction` (string, required): Transaction ID or reference
- `amount` (integer, optional): Amount to refund in kobo/cents (full amount if not specified)
- `currency` (string, optional): Currency code
- `customer_note` (string, optional): Note for customer
- `merchant_note` (string, optional): Internal merchant note

## Development

### Testing

Run tests with pytest:

```bash
pytest tests/
```

Run tests with coverage:

```bash
pytest tests/ --cov=paystack_mcp
```

### Code Quality

Format code:
```bash
black paystack_mcp/
```

Lint code:
```bash
ruff check paystack_mcp/
```

Type check:
```bash
mypy paystack_mcp/
```

## Project Structure

```
paystack-mcp/
├── paystack_mcp/           # Main package
│   ├── __init__.py        # Package initialization
│   ├── server.py          # Main MCP server
│   ├── client.py          # Paystack API client
│   ├── models.py          # Pydantic models
│   └── config.py          # Configuration
├── tests/                 # Test files
│   ├── __init__.py
│   └── test_server.py
├── pyproject.toml         # Project configuration
├── requirements.txt       # Dependencies
├── example.env           # Environment variables example
└── README.md             # This file
```

## Configuration

The server uses environment variables for configuration:

- **PAYSTACK_SECRET_KEY**: Your Paystack secret key (sk_test_... or sk_live_...)
- **PAYSTACK_PUBLIC_KEY**: Your Paystack public key (optional)
- **PAYSTACK_ENVIRONMENT**: Environment setting ('test' or 'live')
- **PAYSTACK_BASE_URL**: API base URL (usually not needed)

## Error Handling

The server provides comprehensive error handling:

- **PaystackAPIError**: Raised for Paystack API errors
- **Validation errors**: For invalid input parameters
- **Network errors**: For connection issues

All errors are properly formatted and returned to the client with descriptive messages.

## Security

- Never commit your `.env` file or actual API keys
- Use test keys during development
- Only use live keys in production environments
- Validate all input parameters
- Follow Paystack's security best practices

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions about this MCP server:
- Open an issue on GitHub
- Check the Paystack API documentation
- Review the MCP specification

For Paystack API questions:
- Visit [Paystack Documentation](https://paystack.com/docs)
- Contact Paystack Support
