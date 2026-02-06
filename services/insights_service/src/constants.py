"""
Insights Service Constants
"""
# =============================================================================
# SUCCESS MESSAGES
# =============================================================================
MSG_SUCCESS_INSIGHTS_GENERATED = "Insights generated successfully"

# =============================================================================
# ERROR MESSAGES
# =============================================================================
MSG_ERROR_INSIGHTS_NOT_CONFIGURED = "AI insights not configured"
MSG_ERROR_INSIGHTS_TIMEOUT = "Analysis timed out"
MSG_ERROR_INSIGHTS_FAILED = "Unable to generate analysis"
MSG_ERROR_INSIGHTS_RATE_LIMITED = "Too many requests, try again later"
MSG_ERROR_EMPTY_PORTFOLIO = "Your portfolio is empty. Deposit funds to get started!"
MSG_ERROR_INVALID_USER_CONTEXT = "Invalid user context"
MSG_ERROR_UNEXPECTED = "An unexpected error occurred"
MSG_ERROR_USER_NOT_FOUND = "User not found"
MSG_ERROR_LLM_API_KEY_NOT_CONFIGURED = "not configured"
MSG_ERROR_LLM_API_ERROR = "LLM API error"
MSG_ERROR_LLM_BLOCKED = "Analysis temporarily unavailable due to content filtering"

# =============================================================================
# LLM CONFIGURATION
# =============================================================================
LLM_MODEL_NAME = "gemini-flash-latest"  # Use latest flash model (was gemini-1.5-flash which is deprecated)
LLM_API_KEY_ENV_VAR = "GOOGLE_GEMINI_API_KEY"
LLM_MAX_OUTPUT_TOKENS = 150
LLM_TEMPERATURE = 0.7
# Prompt limits - what we send to Gemini (keep reasonable for API)
LLM_MAX_HOLDINGS_IN_PROMPT = 10  # Top 10 holdings in prompt
LLM_MAX_ORDERS_IN_PROMPT = 10  # Last 10 orders in prompt
# Fetch limits - what we get from DB (can be higher for accounts with many records)
LLM_MAX_RECENT_ORDERS = 100  # Fetch up to 100 orders, use top 10 in prompt
LLM_MAX_HOLDINGS_FETCH = 100  # Fetch up to 100 holdings, use top 10 in prompt

# =============================================================================
# LLM PROMPT TEMPLATES
# =============================================================================
PROMPT_HEADER = "Analyze this portfolio:"
PROMPT_USD_BALANCE = "- USD Balance: $"
PROMPT_TOTAL_VALUE = "- Total Portfolio Value: $"
PROMPT_HOLDINGS_HEADER = "- Holdings:"
PROMPT_RECENT_ACTIVITY_HEADER = "- Recent Activity:"
PROMPT_SUMMARY_INSTRUCTION = "\nProvide a 2-4 sentence summary."
PROMPT_POSITIVE_SIGN = "+"
PROMPT_NEGATIVE_SIGN = ""

# System prompt for portfolio analysis
LLM_SYSTEM_PROMPT = """You are a helpful financial assistant analyzing a cryptocurrency portfolio. 
Provide a brief, actionable summary (2-4 sentences) based on the user's 
portfolio composition, recent trading activity, and current market conditions.
Be concise and avoid financial advice disclaimers."""

# =============================================================================
# RESPONSE FIELD NAMES
# =============================================================================
RESPONSE_FIELD_SERVICE = "service"
RESPONSE_FIELD_VERSION = "version"
RESPONSE_FIELD_STATUS = "status"
RESPONSE_FIELD_TIMESTAMP = "timestamp"
RESPONSE_FIELD_ENDPOINTS = "endpoints"
RESPONSE_FIELD_DOCS = "docs"
RESPONSE_FIELD_HEALTH = "health"
RESPONSE_FIELD_INSIGHTS = "insights"

# =============================================================================
# ERROR DETECTION STRINGS (for parsing LLM API errors)
# =============================================================================
ERROR_KEYWORD_TIMEOUT = "timeout"
ERROR_KEYWORD_TIMED_OUT = "timed out"
ERROR_KEYWORD_RATE_LIMIT = "rate limit"
ERROR_CODE_RATE_LIMIT = "429"

# =============================================================================
# SERVICE CONFIGURATION
# =============================================================================
DEFAULT_SERVICE_PORT = 8004
SERVICE_PORT_ENV_VAR = "SERVICE_PORT"
