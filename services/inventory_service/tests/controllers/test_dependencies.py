"""
Unit tests for dependencies module
Path: services/inventory-service/tests/controllers/test_dependencies.py
"""
from unittest.mock import patch, MagicMock
from controllers.dependencies import get_asset_dao_dependency
from common.data.dao.inventory.asset_dao import AssetDAO

PATH_GET_ASSET_DAO = 'controllers.dependencies.get_asset_dao'

class TestDependencies:
    """Test dependency injection functions"""


    def test_get_asset_dao_dependency(self):
        """Test getting AssetDAO dependency"""
        mock_asset_dao = MagicMock(spec=AssetDAO)

        with patch(PATH_GET_ASSET_DAO, return_value=mock_asset_dao) as mock_get_asset_dao:
            result = get_asset_dao_dependency()

            assert result == mock_asset_dao
            mock_get_asset_dao.assert_called_once()
