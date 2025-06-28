"""
Paystack MCP Server

A Model Context Protocol server for Paystack payment processing.
"""

__version__ = "0.1.0"
__author__ = "Johnmicheal Elijah"
__email__ = "michealelijah301@gmail.com"

from .server import app

__all__ = ["app"] 