"""
User Service Validation Enums - For validation-related type safety
"""
from enum import Enum


class ValidationActions(str, Enum):
    """Validation action names - for type safety and consistency"""
    VIEW_PORTFOLIO = "view_portfolio"
    GET_ASSET_BALANCE = "get_asset_balance"
