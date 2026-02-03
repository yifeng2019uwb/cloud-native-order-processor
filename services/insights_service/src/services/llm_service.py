"""
LLM Service - Google Gemini Integration
"""
import os
import google.generativeai as genai
from common.shared.logging import BaseLogger, LoggerName, LogAction
from api_models.insights.portfolio_context import PortfolioContext
from constants import (
    LLM_MODEL_NAME,
    LLM_API_KEY_ENV_VAR,
    LLM_MAX_OUTPUT_TOKENS,
    LLM_TEMPERATURE,
    LLM_MAX_HOLDINGS_IN_PROMPT,
    LLM_MAX_ORDERS_IN_PROMPT,
    LLM_SYSTEM_PROMPT,
    PROMPT_HEADER,
    PROMPT_USD_BALANCE,
    PROMPT_TOTAL_VALUE,
    PROMPT_HOLDINGS_HEADER,
    PROMPT_RECENT_ACTIVITY_HEADER,
    PROMPT_SUMMARY_INSTRUCTION,
    PROMPT_POSITIVE_SIGN,
    PROMPT_NEGATIVE_SIGN,
    MSG_ERROR_LLM_API_KEY_NOT_CONFIGURED,
    MSG_ERROR_LLM_API_ERROR
)

logger = BaseLogger(LoggerName.INSIGHTS)


class LLMService:
    """Service for calling Google Gemini API"""
    
    def __init__(self):
        api_key = os.getenv(LLM_API_KEY_ENV_VAR)
        if not api_key:
            raise ValueError(f"{LLM_API_KEY_ENV_VAR} {MSG_ERROR_LLM_API_KEY_NOT_CONFIGURED}")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(LLM_MODEL_NAME)
        logger.info(action=LogAction.SERVICE_START, message="LLM Service initialized")
    
    def generate_insights(self, portfolio_context: PortfolioContext) -> str:
        """
        Generate insights from portfolio context
        
        Args:
            portfolio_context: PortfolioContext model with user portfolio data
            
        Returns:
            str: Generated insights summary
        """
        try:
            # Build user prompt from portfolio context
            prompt = self._build_prompt(portfolio_context)
            
            # Call Gemini API
            response = self.model.generate_content(
                system_instruction=LLM_SYSTEM_PROMPT,
                contents=prompt,
                generation_config={
                    "max_output_tokens": LLM_MAX_OUTPUT_TOKENS,
                    "temperature": LLM_TEMPERATURE,
                }
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(action=LogAction.ERROR, message=f"{MSG_ERROR_LLM_API_ERROR}: {str(e)}")
            raise
    
    def _build_prompt(self, context: PortfolioContext) -> str:
        """Build user prompt from portfolio context"""
        lines = [
            PROMPT_HEADER,
            f"{PROMPT_USD_BALANCE}{float(context.usd_balance):,.2f}",
            f"{PROMPT_TOTAL_VALUE}{float(context.total_portfolio_value):,.2f}",
        ]
        
        # Add holdings
        if context.holdings:
            lines.append(PROMPT_HOLDINGS_HEADER)
            for holding in context.holdings[:LLM_MAX_HOLDINGS_IN_PROMPT]:
                allocation = float(holding.allocation_pct)
                change = float(holding.price_change_24h_pct)
                sign = PROMPT_POSITIVE_SIGN if change >= 0 else PROMPT_NEGATIVE_SIGN
                lines.append(f"  {holding.asset_id} ({allocation:.1f}%, {sign}{change:.2f}% 24h)")
        
        # Add recent orders
        if context.recent_orders:
            lines.append(PROMPT_RECENT_ACTIVITY_HEADER)
            for order in context.recent_orders[:LLM_MAX_ORDERS_IN_PROMPT]:
                price = float(order.price)
                quantity = float(order.quantity)
                lines.append(f"  {order.order_type}: {quantity} {order.asset_id} at ${price:,.2f}")
        
        lines.append(PROMPT_SUMMARY_INSTRUCTION)
        
        return "\n".join(lines)
