"""
Simple retry utility for integration tests
Basic retry logic for network issues
"""
import time
import requests
from typing import Callable, Any

def simple_retry(func: Callable, max_attempts: int = 3, delay: float = 1.0) -> Any:
    """
    Simple retry wrapper for network requests

    Args:
        func: Function to retry
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds

    Returns:
        Result of the function call

    Raises:
        Last exception if all attempts fail
    """
    last_exception = None

    for attempt in range(max_attempts):
        try:
            return func()
        except (requests.RequestException, ConnectionError) as e:
            last_exception = e
            if attempt < max_attempts - 1:
                time.sleep(delay)
                continue
            else:
                raise last_exception

    # This should never be reached, but just in case
    if last_exception:
        raise last_exception