"""
Pydantic models for Paystack API data structures.
"""

from datetime import datetime
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field


class PaystackResponse(BaseModel):
    """Base response model for Paystack API."""
    status: bool
    message: str
    data: Optional[Any] = None


class Customer(BaseModel):
    """Customer model."""
    id: Optional[int] = None
    customer_code: Optional[str] = None
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Transaction(BaseModel):
    """Transaction model."""
    id: Optional[int] = None
    reference: Optional[str] = None
    amount: int  # Amount in kobo/cents
    currency: str = "NGN"
    status: Optional[str] = None
    gateway_response: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    channel: Optional[str] = None
    customer: Optional[Customer] = None
    authorization: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class TransactionRequest(BaseModel):
    """Request model for initializing transactions."""
    email: str
    amount: int  # Amount in kobo/cents
    currency: str = "NGN"
    reference: Optional[str] = None
    callback_url: Optional[str] = None
    plan: Optional[str] = None
    invoice_limit: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    channels: Optional[List[str]] = None
    split_code: Optional[str] = None
    subaccount: Optional[str] = None
    transaction_charge: Optional[int] = None
    bearer: Optional[str] = None


class Plan(BaseModel):
    """Subscription plan model."""
    id: Optional[int] = None
    plan_code: Optional[str] = None
    name: str
    amount: int  # Amount in kobo/cents
    interval: str  # daily, weekly, monthly, quarterly, biannually, annually
    description: Optional[str] = None
    currency: str = "NGN"
    invoice_limit: Optional[int] = None
    send_invoices: bool = True
    send_sms: bool = True
    hosted_page: bool = False
    hosted_page_url: Optional[str] = None
    hosted_page_summary: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Bank(BaseModel):
    """Bank model."""
    id: Optional[int] = None
    name: str
    slug: str
    code: str
    longcode: str
    gateway: Optional[str] = None
    pay_with_bank: bool = False
    active: bool = True
    country: str = "Nigeria"
    currency: str = "NGN"
    type: str = "nuban"
    is_deleted: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RefundRequest(BaseModel):
    """Request model for refunds."""
    transaction: str  # Transaction ID or reference
    amount: Optional[int] = None  # Amount in kobo/cents, full amount if not specified
    currency: Optional[str] = None
    customer_note: Optional[str] = None
    merchant_note: Optional[str] = None 