"""
Configuration module for Paystack MCP server.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class PaystackConfig(BaseModel):
    """Configuration for Paystack API."""
    
    secret_key: str = Field(..., description="Paystack secret key")
    public_key: Optional[str] = Field(None, description="Paystack public key")
    environment: str = Field(default="test", description="Environment: 'test' or 'live'")
    base_url: str = Field(default="https://api.paystack.co", description="Paystack API base URL")
    
    @classmethod
    def from_env(cls) -> "PaystackConfig":
        """Create configuration from environment variables."""
        secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        if not secret_key:
            # For development/testing without real credentials
            secret_key = "sk_test_placeholder"
            print("⚠️  Warning: Using placeholder secret key. Set PAYSTACK_SECRET_KEY for production.")
        
        return cls(
            secret_key=secret_key,
            public_key=os.getenv("PAYSTACK_PUBLIC_KEY"),
            environment=os.getenv("PAYSTACK_ENVIRONMENT", "test"),
            base_url=os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co")
        )
    
    @property
    def headers(self) -> dict[str, str]:
        """Get headers for Paystack API requests."""
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }


# Global configuration instance
config = PaystackConfig.from_env() 