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
    MSG_ERROR_LLM_API_ERROR,
    MSG_ERROR_LLM_BLOCKED
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
            # Note: system_instruction parameter not supported, include in prompt instead
            full_prompt = f"{LLM_SYSTEM_PROMPT}\n\n{prompt}"
            response = self.model.generate_content(
                contents=full_prompt,
                generation_config={
                    "max_output_tokens": LLM_MAX_OUTPUT_TOKENS,
                    "temperature": LLM_TEMPERATURE,
                }
            )
            
            # Check if response was blocked by safety filters
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = candidate.finish_reason
                    # finish_reason: 1=STOP (normal), 2=MAX_TOKENS, 3=SAFETY (blocked), 4=RECITATION (blocked)
                    if finish_reason in [3, 4]:  # SAFETY or RECITATION (blocked)
                        logger.warning(
                            action=LogAction.ERROR,
                            message=f"Gemini API blocked response (finish_reason: {finish_reason})"
                        )
                        raise ValueError(MSG_ERROR_LLM_BLOCKED)
            
            # Extract text from response
            try:
                if hasattr(response, 'text') and response.text:
                    return response.text.strip()
            except ValueError as e:
                # Handle case where response.text fails (e.g., blocked response)
                if "finish_reason" in str(e).lower() or "no valid" in str(e).lower():
                    logger.warning(
                        action=LogAction.ERROR,
                        message=f"Gemini API response blocked: {str(e)}"
                    )
                    raise ValueError(MSG_ERROR_LLM_BLOCKED)
                raise
            
            # Fallback: try to extract from candidates
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    parts = candidate.content.parts
                    if parts and len(parts) > 0 and hasattr(parts[0], 'text'):
                        return parts[0].text.strip()
            
            raise ValueError("No text content in Gemini API response")
            
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
