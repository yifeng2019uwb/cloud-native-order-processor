"""
Pytest configuration and fixtures for common module tests.
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def patch_controller_deps():
    """Simple fixture for patching controller dependencies."""
    def _patch_dependencies(controller_func, dependencies):
        """Patch multiple dependencies and return mocks."""
        patches = []
        mocks = {}

        for dep_path in dependencies:
            patcher = patch(dep_path)
            mock_obj = patcher.start()
            patches.append(patcher)
            mocks[dep_path] = mock_obj

        return mocks

    return _patch_dependencies
