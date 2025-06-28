/**
 * Example JavaScript client for the Paystack MCP Server
 * 
 * This demonstrates how to connect to the Python MCP server from a JavaScript application.
 * Install dependencies first: npm install @modelcontextprotocol/sdk
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

class PaystackMCPClient {
    constructor() {
        this.client = null;
        this.transport = null;
    }

    async connect() {
        // Create transport to the Python server
        this.transport = new StdioClientTransport({
            command: "python",
            args: ["-m", "paystack_mcp.server"],
            env: {
                ...process.env,
                PAYSTACK_SECRET_KEY: process.env.PAYSTACK_SECRET_KEY || "sk_test_your_key_here"
            }
        });

        // Create and connect client
        this.client = new Client(
            {
                name: "paystack-js-client",
                version: "1.0.0",
            },
            {
                capabilities: {},
            }
        );

        await this.client.connect(this.transport);
        console.log("✅ Connected to Paystack MCP server");
    }

    async disconnect() {
        if (this.client) {
            await this.client.close();
        }
    }

    async listTools() {
        const tools = await this.client.listTools();
        return tools.tools;
    }

    async initializeTransaction(email, amount, options = {}) {
        const result = await this.client.callTool({
            name: "initialize_transaction",
            arguments: {
                email,
                amount,
                currency: options.currency || "NGN",
                reference: options.reference,
                callback_url: options.callback_url,
                metadata: options.metadata
            }
        });
        
        return JSON.parse(result.content[0].text.split(':\n')[1]);
    }

    async verifyTransaction(reference) {
        const result = await this.client.callTool({
            name: "verify_transaction",
            arguments: { reference }
        });
        
        return JSON.parse(result.content[0].text.split(':\n')[1]);
    }

    async createCustomer(email, firstName, lastName, phone = null, metadata = null) {
        const result = await this.client.callTool({
            name: "create_customer",
            arguments: {
                email,
                first_name: firstName,
                last_name: lastName,
                phone,
                metadata
            }
        });
        
        return JSON.parse(result.content[0].text.split(':\n')[1]);
    }

    async listTransactions(options = {}) {
        const result = await this.client.callTool({
            name: "list_transactions",
            arguments: {
                per_page: options.per_page || 50,
                page: options.page || 1,
                customer: options.customer,
                status: options.status,
                from_date: options.from_date,
                to_date: options.to_date
            }
        });
        
        return JSON.parse(result.content[0].text.split(':\n')[1]);
    }

    async listBanks(country = "nigeria") {
        const result = await this.client.callTool({
            name: "list_banks",
            arguments: { country }
        });
        
        return JSON.parse(result.content[0].text.split(':\n')[1]);
    }

    async resolveAccount(accountNumber, bankCode) {
        const result = await this.client.callTool({
            name: "resolve_account",
            arguments: {
                account_number: accountNumber,
                bank_code: bankCode
            }
        });
        
        return JSON.parse(result.content[0].text.split(':\n')[1]);
    }
}

// Example usage
async function main() {
    const paystackClient = new PaystackMCPClient();
    
    try {
        await paystackClient.connect();
        
        // List available tools
        const tools = await paystackClient.listTools();
        console.log("Available tools:", tools.map(t => t.name));
        
        // Initialize a transaction
        const transaction = await paystackClient.initializeTransaction(
            "customer@example.com",
            50000, // 500 NGN in kobo
            {
                reference: `tx_${Date.now()}`,
                callback_url: "https://example.com/callback"
            }
        );
        console.log("Transaction initialized:", transaction);
        
        // Create a customer
        const customer = await paystackClient.createCustomer(
            "customer@example.com",
            "John",
            "Doe",
            "+2348012345678"
        );
        console.log("Customer created:", customer);
        
        // List banks
        const banks = await paystackClient.listBanks();
        console.log("Available banks:", banks.data?.slice(0, 5)); // Show first 5 banks
        
    } catch (error) {
        console.error("Error:", error);
    } finally {
        await paystackClient.disconnect();
    }
}

// Run the example
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export default PaystackMCPClient; 