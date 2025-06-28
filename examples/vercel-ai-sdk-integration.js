/**
 * Vercel AI SDK + Paystack MCP Integration Example
 * 
 * This demonstrates how to integrate the Paystack MCP server with
 * a chatbot built using Vercel's AI SDK.
 */

import { openai } from '@ai-sdk/openai';
import { generateText, tool } from 'ai';
import { z } from 'zod';
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

class PaystackMCPIntegration {
    constructor() {
        this.mcpClient = null;
        this.transport = null;
        this.isConnected = false;
    }

    async initialize() {
        // Connect to Python MCP server
        this.transport = new StdioClientTransport({
            command: "python",
            args: ["-m", "paystack_mcp.server"],
            env: {
                ...process.env,
                PAYSTACK_SECRET_KEY: process.env.PAYSTACK_SECRET_KEY
            }
        });

        this.mcpClient = new Client(
            { name: "paystack-chatbot", version: "1.0.0" },
            { capabilities: {} }
        );

        await this.mcpClient.connect(this.transport);
        this.isConnected = true;
        console.log("✅ Paystack MCP connected");
    }

    async disconnect() {
        if (this.mcpClient && this.isConnected) {
            await this.mcpClient.close();
            this.isConnected = false;
        }
    }

    // Convert MCP tool calls to Vercel AI SDK tools
    async getVercelAITools() {
        if (!this.isConnected) await this.initialize();

        return {
            initializePayment: tool({
                description: 'Initialize a payment transaction with Paystack',
                parameters: z.object({
                    email: z.string().email('Valid email required'),
                    amount: z.number().min(100, 'Minimum amount is 100 kobo (1 NGN)'),
                    currency: z.string().default('NGN'),
                    reference: z.string().optional(),
                    callback_url: z.string().url().optional(),
                }),
                execute: async ({ email, amount, currency = 'NGN', reference, callback_url }) => {
                    try {
                        const result = await this.mcpClient.callTool({
                            name: "initialize_transaction",
                            arguments: {
                                email,
                                amount,
                                currency,
                                reference: reference || `tx_${Date.now()}`,
                                callback_url
                            }
                        });

                        const data = JSON.parse(result.content[0].text.split(':\n')[1]);
                        
                        return {
                            success: true,
                            authorization_url: data.data.authorization_url,
                            reference: data.data.reference,
                            access_code: data.data.access_code,
                            message: `Payment link created successfully! Amount: ₦${amount/100}`
                        };
                    } catch (error) {
                        return {
                            success: false,
                            error: error.message,
                            message: 'Failed to initialize payment. Please try again.'
                        };
                    }
                }
            }),

            verifyPayment: tool({
                description: 'Verify a payment transaction status',
                parameters: z.object({
                    reference: z.string().min(1, 'Transaction reference is required'),
                }),
                execute: async ({ reference }) => {
                    try {
                        const result = await this.mcpClient.callTool({
                            name: "verify_transaction",
                            arguments: { reference }
                        });

                        const data = JSON.parse(result.content[0].text.split(':\n')[1]);
                        const transaction = data.data;
                        
                        return {
                            success: true,
                            status: transaction.status,
                            amount: transaction.amount,
                            currency: transaction.currency,
                            paid_at: transaction.paid_at,
                            customer_email: transaction.customer?.email,
                            message: `Payment status: ${transaction.status}. Amount: ₦${transaction.amount/100}`
                        };
                    } catch (error) {
                        return {
                            success: false,
                            error: error.message,
                            message: 'Failed to verify payment. Please check the reference.'
                        };
                    }
                }
            }),

            createCustomer: tool({
                description: 'Create a new customer in Paystack',
                parameters: z.object({
                    email: z.string().email('Valid email required'),
                    first_name: z.string().optional(),
                    last_name: z.string().optional(),
                    phone: z.string().optional(),
                }),
                execute: async ({ email, first_name, last_name, phone }) => {
                    try {
                        const result = await this.mcpClient.callTool({
                            name: "create_customer",
                            arguments: { email, first_name, last_name, phone }
                        });

                        const data = JSON.parse(result.content[0].text.split(':\n')[1]);
                        
                        return {
                            success: true,
                            customer_code: data.data.customer_code,
                            email: data.data.email,
                            message: `Customer created successfully with code: ${data.data.customer_code}`
                        };
                    } catch (error) {
                        return {
                            success: false,
                            error: error.message,
                            message: 'Failed to create customer. Email might already exist.'
                        };
                    }
                }
            }),

            listBanks: tool({
                description: 'Get list of supported banks for transfers',
                parameters: z.object({
                    country: z.string().default('nigeria'),
                }),
                execute: async ({ country = 'nigeria' }) => {
                    try {
                        const result = await this.mcpClient.callTool({
                            name: "list_banks",
                            arguments: { country }
                        });

                        const data = JSON.parse(result.content[0].text.split(':\n')[1]);
                        const banks = data.data.slice(0, 10); // Limit to first 10 for chat display
                        
                        return {
                            success: true,
                            banks: banks.map(bank => ({
                                name: bank.name,
                                code: bank.code,
                                slug: bank.slug
                            })),
                            total_count: data.data.length,
                            message: `Found ${data.data.length} supported banks. Showing first 10.`
                        };
                    } catch (error) {
                        return {
                            success: false,
                            error: error.message,
                            message: 'Failed to fetch banks list.'
                        };
                    }
                }
            })
        };
    }
}

// Chatbot implementation with Vercel AI SDK
export async function createPaymentChatbot() {
    const paystackIntegration = new PaystackMCPIntegration();
    
    // Initialize the MCP connection
    await paystackIntegration.initialize();
    
    // Get payment tools for the AI
    const tools = await paystackIntegration.getVercelAITools();

    // Create the chatbot function
    async function handleChatMessage(message, conversation = []) {
        try {
            const result = await generateText({
                model: openai('gpt-4'),
                messages: [
                    {
                        role: 'system',
                        content: `You are a helpful payment assistant powered by Paystack. You can:
                        
                        1. Initialize payments for users
                        2. Verify payment transactions  
                        3. Create customer accounts
                        4. List supported banks
                        
                        When users want to make payments:
                        - Ask for their email and amount
                        - Use the initializePayment tool
                        - Provide them with the payment link
                        
                        When users want to verify payments:
                        - Ask for the transaction reference
                        - Use verifyPayment tool
                        - Tell them the status
                        
                        Be friendly and helpful. Always explain what you're doing.
                        Amounts should be in kobo (multiply Naira by 100).`
                    },
                    ...conversation,
                    {
                        role: 'user',
                        content: message
                    }
                ],
                tools,
                maxToolRoundtrips: 3,
            });

            return {
                response: result.text,
                toolResults: result.toolResults || [],
                usage: result.usage
            };

        } catch (error) {
            console.error('Chat error:', error);
            return {
                response: "I'm sorry, I encountered an error. Please try again.",
                error: error.message
            };
        }
    }

    // Return the chatbot interface
    return {
        chat: handleChatMessage,
        disconnect: () => paystackIntegration.disconnect(),
        tools: Object.keys(tools)
    };
}

// Example usage in a Next.js API route
export async function POST(request) {
    const { message, conversation } = await request.json();
    
    const chatbot = await createPaymentChatbot();
    
    try {
        const result = await chatbot.chat(message, conversation);
        
        return new Response(JSON.stringify(result), {
            headers: { 'Content-Type': 'application/json' }
        });
    } finally {
        await chatbot.disconnect();
    }
}

// Example frontend integration
export const PaymentChatbotComponent = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        const newMessages = [...messages, userMessage];
        setMessages(newMessages);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    conversation: messages
                })
            });

            const result = await response.json();
            
            setMessages([
                ...newMessages,
                { role: 'assistant', content: result.response }
            ]);

            // Handle tool results (show payment links, etc.)
            if (result.toolResults?.length > 0) {
                console.log('Tool results:', result.toolResults);
            }

        } catch (error) {
            console.error('Error:', error);
            setMessages([
                ...newMessages,
                { role: 'assistant', content: 'Sorry, I encountered an error.' }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="chat-container">
            <div className="messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                        {msg.content}
                    </div>
                ))}
                {isLoading && <div className="loading">Processing...</div>}
            </div>
            
            <div className="input-area">
                <input 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Ask me about payments..."
                />
                <button onClick={sendMessage} disabled={isLoading}>
                    Send
                </button>
            </div>
        </div>
    );
}; 