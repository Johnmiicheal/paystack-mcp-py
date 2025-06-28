"""
Paystack API client for making HTTP requests.
"""

import asyncio
from typing import Dict, Any, Optional, List
import httpx
from .config import config
from .models import (
    PaystackResponse, 
    Customer, 
    Transaction, 
    TransactionRequest, 
    Plan, 
    Bank, 
    RefundRequest
)


class PaystackAPIError(Exception):
    """Exception raised for Paystack API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class PaystackClient:
    """Async client for Paystack API."""
    
    def __init__(self):
        self.base_url = config.base_url
        self.headers = config.headers
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to Paystack API."""
        try:
            response = await self.client.request(
                method=method,
                url=endpoint,
                json=data,
                params=params
            )
            
            response_data = response.json()
            
            if not response.is_success:
                raise PaystackAPIError(
                    message=response_data.get("message", "API request failed"),
                    status_code=response.status_code,
                    response_data=response_data
                )
            
            return response_data
            
        except httpx.HTTPError as e:
            raise PaystackAPIError(f"HTTP error occurred: {str(e)}")
    
    # Transaction methods
    async def initialize_transaction(self, transaction_data: TransactionRequest) -> Dict[str, Any]:
        """Initialize a new transaction."""
        data = transaction_data.model_dump(exclude_unset=True)
        return await self._make_request("POST", "/transaction/initialize", data=data)
    
    async def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """Verify a transaction by reference."""
        return await self._make_request("GET", f"/transaction/verify/{reference}")
    
    async def list_transactions(
        self, 
        per_page: int = 50, 
        page: int = 1,
        customer: Optional[str] = None,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """List transactions with optional filters."""
        params = {
            "perPage": per_page,
            "page": page
        }
        
        if customer:
            params["customer"] = customer
        if status:
            params["status"] = status
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        
        return await self._make_request("GET", "/transaction", params=params)
    
    async def get_transaction(self, transaction_id: int) -> Dict[str, Any]:
        """Get transaction details by ID."""
        return await self._make_request("GET", f"/transaction/{transaction_id}")
    
    # Customer methods
    async def create_customer(self, customer_data: Customer) -> Dict[str, Any]:
        """Create a new customer."""
        data = customer_data.model_dump(exclude_unset=True, exclude={"id", "customer_code", "created_at", "updated_at"})
        return await self._make_request("POST", "/customer", data=data)
    
    async def list_customers(
        self, 
        per_page: int = 50, 
        page: int = 1
    ) -> Dict[str, Any]:
        """List customers."""
        params = {
            "perPage": per_page,
            "page": page
        }
        return await self._make_request("GET", "/customer", params=params)
    
    async def get_customer(self, customer_code: str) -> Dict[str, Any]:
        """Get customer details by customer code."""
        return await self._make_request("GET", f"/customer/{customer_code}")
    
    async def update_customer(self, customer_code: str, customer_data: Customer) -> Dict[str, Any]:
        """Update customer information."""
        data = customer_data.model_dump(exclude_unset=True, exclude={"id", "customer_code", "created_at", "updated_at"})
        return await self._make_request("PUT", f"/customer/{customer_code}", data=data)
    
    # Plan methods
    async def create_plan(self, plan_data: Plan) -> Dict[str, Any]:
        """Create a subscription plan."""
        data = plan_data.model_dump(exclude_unset=True, exclude={"id", "plan_code", "created_at", "updated_at"})
        return await self._make_request("POST", "/plan", data=data)
    
    async def list_plans(
        self, 
        per_page: int = 50, 
        page: int = 1
    ) -> Dict[str, Any]:
        """List subscription plans."""
        params = {
            "perPage": per_page,
            "page": page
        }
        return await self._make_request("GET", "/plan", params=params)
    
    async def get_plan(self, plan_code: str) -> Dict[str, Any]:
        """Get plan details by plan code."""
        return await self._make_request("GET", f"/plan/{plan_code}")
    
    # Bank methods
    async def list_banks(self, country: str = "nigeria") -> Dict[str, Any]:
        """List supported banks."""
        params = {"country": country}
        return await self._make_request("GET", "/bank", params=params)
    
    async def resolve_account(self, account_number: str, bank_code: str) -> Dict[str, Any]:
        """Resolve account number to get account details."""
        params = {
            "account_number": account_number,
            "bank_code": bank_code
        }
        return await self._make_request("GET", "/bank/resolve", params=params)
    
    # Refund methods
    async def create_refund(self, refund_data: RefundRequest) -> Dict[str, Any]:
        """Create a refund."""
        data = refund_data.model_dump(exclude_unset=True)
        return await self._make_request("POST", "/refund", data=data)
    
    async def list_refunds(
        self, 
        per_page: int = 50, 
        page: int = 1,
        reference: Optional[str] = None,
        currency: Optional[str] = None
    ) -> Dict[str, Any]:
        """List refunds."""
        params = {
            "perPage": per_page,
            "page": page
        }
        
        if reference:
            params["reference"] = reference
        if currency:
            params["currency"] = currency
        
        return await self._make_request("GET", "/refund", params=params)
    
    async def get_refund(self, refund_id: int) -> Dict[str, Any]:
        """Get refund details by ID."""
        return await self._make_request("GET", f"/refund/{refund_id}")


# Global client instance
paystack_client = PaystackClient() 