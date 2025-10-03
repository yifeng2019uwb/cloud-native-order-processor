"""
Header Validator for Gateway Authentication

This module contains the HeaderValidator class for validating gateway headers
and extracting user information from incoming requests.
"""

from typing import Dict, Optional

from fastapi import HTTPException, status


class HeaderValidator:
    """
    Validates gateway headers and extracts user information.

    This class is used by services to validate incoming requests from the API gateway
    and extract user context information.
    """

    def __init__(self):
        """Initialize the header validator with required header names."""
        self.required_headers = [
            'X-User-ID',
            'X-User-Role',
            'X-Request-ID',
            'X-Source-Service'
        ]

    def validate_gateway_headers(self, headers: Dict[str, str]) -> bool:
        """
        Validate that required gateway headers are present and valid.

        Args:
            headers: Request headers dictionary

        Returns:
            True if headers are valid

        Raises:
            HTTPException: If headers are invalid or missing
        """
        missing_headers = [h for h in self.required_headers if h not in headers]
        if missing_headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required gateway headers: {', '.join(missing_headers)}"
            )

        return True

    def extract_user_from_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Extract user information from gateway headers.

        Args:
            headers: Request headers dictionary

        Returns:
            Dictionary containing user information

        Raises:
            HTTPException: If headers are invalid
        """
        self.validate_gateway_headers(headers)

        return {
            'user_id': headers.get('X-User-ID'),
            'user_role': headers.get('X-User-Role'),
            'request_id': headers.get('X-Request-ID'),
            'source_service': headers.get('X-Source-Service')
        }

    def is_authenticated(self, headers: Dict[str, str]) -> bool:
        """
        Check if the request is properly authenticated.

        Args:
            headers: Request headers dictionary

        Returns:
            True if request is authenticated
        """
        try:
            self.validate_gateway_headers(headers)
            return True
        except HTTPException:
            return False

    def get_user_role(self, headers: Dict[str, str]) -> Optional[str]:
        """
        Get the user role from headers.

        Args:
            headers: Request headers dictionary

        Returns:
            User role string or None if not present
        """
        return headers.get('X-User-Role')

    def get_user_id(self, headers: Dict[str, str]) -> Optional[str]:
        """
        Get the user ID from headers.

        Args:
            headers: Request headers dictionary

        Returns:
            User ID string or None if not present
        """
        return headers.get('X-User-ID')
