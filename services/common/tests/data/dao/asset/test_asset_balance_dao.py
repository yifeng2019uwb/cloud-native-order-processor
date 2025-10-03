"""
Tests for Asset Balance DAO
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from src.data.dao.asset.asset_balance_dao import AssetBalanceDAO
from src.data.entities.asset import AssetBalance, AssetBalanceItem
from src.data.exceptions import CNOPDatabaseOperationException
from src.exceptions.shared_exceptions import CNOPAssetBalanceNotFoundException


class TestAssetBalanceDAO:
    """Test AssetBalanceDAO class"""

    @pytest.fixture
    def mock_db_connection(self):
        """Create mock database connection"""
        mock_connection = MagicMock()
        mock_users_table = MagicMock()
        mock_connection.users_table = mock_users_table
        return mock_connection

    @pytest.fixture
    def asset_balance_dao(self, mock_db_connection):
        """Create AssetBalanceDAO instance with mock connection"""
        return AssetBalanceDAO(mock_db_connection)

    @pytest.fixture
    def sample_asset_balance(self):
        """Sample asset balance for testing"""
        now = datetime.now(timezone.utc)
        return AssetBalance(
            username="testuser123",
            asset_id="BTC",
            quantity=Decimal('10.5'),
            created_at=now,
            updated_at=now
        )

    def test_upsert_asset_balance_update_existing(self, asset_balance_dao, sample_asset_balance, mock_db_connection):
        """Test successful asset balance update (existing item)"""
        # Convert sample_asset_balance to AssetBalanceItem for database operations
        sample_asset_balance_item = AssetBalanceItem.from_asset_balance(sample_asset_balance)

        # Mock get_asset_balance to return existing balance
        with patch.object(asset_balance_dao, 'get_asset_balance', return_value=sample_asset_balance):
            # Mock database response for existing item (return AssetBalanceItem data)
            mock_updated_item = {
                'Pk': sample_asset_balance_item.Pk,
                'Sk': sample_asset_balance_item.Sk,
                'username': 'testuser123',
                'asset_id': 'BTC',
                'quantity': '15.5',
                'created_at': sample_asset_balance_item.created_at,
                'updated_at': '2024-01-01T12:00:00'
            }
            mock_db_connection.users_table.update_item.return_value = {'Attributes': mock_updated_item}

            result = asset_balance_dao.upsert_asset_balance('testuser123', 'BTC', Decimal('15.5'))

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.asset_id == "BTC"
        assert result.quantity == Decimal('15.5')

        # Verify database was called with correct parameters
        mock_db_connection.users_table.update_item.assert_called_once()
        call_args = mock_db_connection.users_table.update_item.call_args
        assert call_args[1]['Key'] == {'Pk': 'testuser123', 'Sk': 'ASSET#BTC'}
        assert 'SET #quantity = :quantity, updated_at = :updated_at' in call_args[1]['UpdateExpression']

    def test_upsert_asset_balance_create_new(self, asset_balance_dao, mock_db_connection):
        """Test successful asset balance creation (new item)"""
        # Create AssetBalance entity for test input
        test_asset_balance = AssetBalance(
            username="testuser123",
            asset_id="ETH",
            quantity=Decimal('5.0'),
            created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        )

        # Convert to AssetBalanceItem for database operations
        test_asset_balance_item = AssetBalanceItem.from_asset_balance(test_asset_balance)

        # Mock get_asset_balance to raise CNOPAssetBalanceNotFoundException
        with patch.object(asset_balance_dao, 'get_asset_balance', side_effect=CNOPAssetBalanceNotFoundException("Not found")):
            # Mock database response for new item (return the AssetBalanceItem data)
            mock_created_item = {
                'Pk': test_asset_balance_item.Pk,
                'Sk': test_asset_balance_item.Sk,
                'username': test_asset_balance_item.username,
                'asset_id': test_asset_balance_item.asset_id,
                'quantity': str(test_asset_balance_item.quantity),
                'created_at': test_asset_balance_item.created_at,
                'updated_at': test_asset_balance_item.updated_at
            }

            mock_db_connection.users_table.put_item.return_value = mock_created_item

            result = asset_balance_dao.upsert_asset_balance('testuser123', 'ETH', Decimal('5.0'))

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.asset_id == "ETH"
        assert result.quantity == Decimal('5.0')

        # Verify put_item was called for new item
        mock_db_connection.users_table.put_item.assert_called_once()

    def test_upsert_asset_balance_zero_quantity(self, asset_balance_dao, mock_db_connection):
        """Test asset balance upsert with zero quantity"""
        # Create a sample balance with existing quantity
        existing_balance = AssetBalance(
            Pk='testuser123',
            Sk='ASSET#BTC',
            username='testuser123',
            asset_id='BTC',
            quantity=Decimal('10.0'),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(asset_balance_dao, 'get_asset_balance', return_value=existing_balance):
            mock_updated_item = {
                'Pk': 'testuser123',
                'Sk': 'ASSET#BTC',
                'username': 'testuser123',
                'asset_id': 'BTC',
                'quantity': '10.0',  # 10.0 + 0.00 = 10.0
                'created_at': '2024-01-01T12:00:00',
                'updated_at': '2024-01-01T12:00:00'
            }
            mock_db_connection.users_table.update_item.return_value = {'Attributes': mock_updated_item}

            result = asset_balance_dao.upsert_asset_balance('testuser123', 'BTC', Decimal('0.00'))

        assert result.quantity == Decimal('10.0')  # Should remain the same when adding 0

    def test_upsert_asset_balance_negative_quantity(self, asset_balance_dao, mock_db_connection):
        """Test asset balance upsert with negative quantity"""
        # Create a sample balance with positive quantity
        positive_balance = AssetBalance(
            Pk='testuser123',
            Sk='ASSET#BTC',
            username='testuser123',
            asset_id='BTC',
            quantity=Decimal('10.0'),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        with patch.object(asset_balance_dao, 'get_asset_balance', return_value=positive_balance):
            mock_updated_item = {
                'Pk': 'testuser123',
                'Sk': 'ASSET#BTC',
                'username': 'testuser123',
                'asset_id': 'BTC',
                'quantity': '5.0',  # 10.0 + (-5.0) = 5.0
                'created_at': '2024-01-01T12:00:00',
                'updated_at': '2024-01-01T12:00:00'
            }
            mock_db_connection.users_table.update_item.return_value = {'Attributes': mock_updated_item}

            result = asset_balance_dao.upsert_asset_balance('testuser123', 'BTC', Decimal('-5.0'))

        assert result.quantity == Decimal('5.0')  # Should be 10.0 - 5.0 = 5.0

    def test_upsert_asset_balance_database_error(self, asset_balance_dao, mock_db_connection):
        """Test asset balance upsert with database error"""
        # Mock get_asset_balance to raise CNOPAssetBalanceNotFoundException
        with patch.object(asset_balance_dao, 'get_asset_balance', side_effect=CNOPAssetBalanceNotFoundException("Not found")):
            # Mock database error for put operation
            mock_db_connection.users_table.put_item.side_effect = ClientError(
                {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
                'PutItem'
            )

            with pytest.raises(CNOPDatabaseOperationException):
                asset_balance_dao.upsert_asset_balance('testuser123', 'BTC', Decimal('10.0'))

    def test_get_asset_balance_success(self, asset_balance_dao, sample_asset_balance, mock_db_connection):
        """Test successful asset balance retrieval"""
        # Mock database response
        mock_item = {
            'Pk': 'testuser123',
            'Sk': 'ASSET#BTC',
            'username': 'testuser123',
            'asset_id': 'BTC',
            'quantity': '10.5',
            'created_at': sample_asset_balance.created_at.isoformat(),
            'updated_at': sample_asset_balance.updated_at.isoformat()
        }
        mock_db_connection.users_table.get_item.return_value = {'Item': mock_item}

        result = asset_balance_dao.get_asset_balance('testuser123', 'BTC')

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.asset_id == "BTC"
        assert result.quantity == Decimal('10.5')

        # Verify database was called
        mock_db_connection.users_table.get_item.assert_called_once_with(
            Key={'Pk': 'testuser123', 'Sk': 'ASSET#BTC'}
        )

    def test_get_asset_balance_not_found(self, asset_balance_dao, mock_db_connection):
        """Test asset balance retrieval when not found"""
        # Mock empty database response
        mock_db_connection.users_table.get_item.return_value = {}

        # Should raise CNOPAssetBalanceNotFoundException
        with pytest.raises(CNOPAssetBalanceNotFoundException):
            asset_balance_dao.get_asset_balance('testuser123', 'BTC')

    def test_get_asset_balance_database_error(self, asset_balance_dao, mock_db_connection):
        """Test asset balance retrieval with database error"""
        # Mock database error
        mock_db_connection.users_table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'GetItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            asset_balance_dao.get_asset_balance('testuser123', 'BTC')

    def test_get_all_asset_balances_success(self, asset_balance_dao, mock_db_connection):
        """Test successful retrieval of all asset balances for user"""
        # Mock database response
        mock_items = [
            {
                'Pk': 'testuser123',
                'Sk': 'ASSET#BTC',
                'username': 'testuser123',
                'asset_id': 'BTC',
                'quantity': '10.5',
                'created_at': '2024-01-01T12:00:00',
                'updated_at': '2024-01-01T12:00:00'
            },
            {
                'Pk': 'testuser123',
                'Sk': 'ASSET#ETH',
                'username': 'testuser123',
                'asset_id': 'ETH',
                'quantity': '25.0',
                'created_at': '2024-01-01T12:00:00',
                'updated_at': '2024-01-01T12:00:00'
            }
        ]
        mock_db_connection.users_table.query.return_value = {'Items': mock_items}

        result = asset_balance_dao.get_all_asset_balances('testuser123')

        # Verify result
        assert len(result) == 2
        assert result[0].asset_id == "BTC"
        assert result[0].quantity == Decimal('10.5')
        assert result[1].asset_id == "ETH"
        assert result[1].quantity == Decimal('25.0')

        # Verify database was called with correct query
        mock_db_connection.users_table.query.assert_called_once()
        call_args = mock_db_connection.users_table.query.call_args
        assert 'KeyConditionExpression' in call_args[1]

    def test_get_all_asset_balances_empty(self, asset_balance_dao, mock_db_connection):
        """Test retrieval of asset balances when user has none"""
        # Mock empty database response
        mock_db_connection.users_table.query.return_value = {'Items': []}

        result = asset_balance_dao.get_all_asset_balances('testuser123')

        assert len(result) == 0

    def test_get_all_asset_balances_database_error(self, asset_balance_dao, mock_db_connection):
        """Test retrieval of asset balances with database error"""
        # Mock database error
        mock_db_connection.users_table.query.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'Query'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            asset_balance_dao.get_all_asset_balances('testuser123')

    def test_delete_asset_balance_success(self, asset_balance_dao, mock_db_connection):
        """Test successful asset balance deletion"""
        # Mock successful deletion with Attributes returned
        mock_db_connection.users_table.delete_item.return_value = {'Attributes': {'Pk': 'testuser123', 'Sk': 'ASSET#BTC'}}

        result = asset_balance_dao.delete_asset_balance('testuser123', 'BTC')

        # Verify result
        assert result is True

        # Verify database was called
        mock_db_connection.users_table.delete_item.assert_called_once_with(
            Key={'Pk': 'testuser123', 'Sk': 'ASSET#BTC'},
            ReturnValues='ALL_OLD'
        )

    def test_delete_asset_balance_database_error(self, asset_balance_dao, mock_db_connection):
        """Test asset balance deletion with database error"""
        # Mock database error
        mock_db_connection.users_table.delete_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'DeleteItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            asset_balance_dao.delete_asset_balance('testuser123', 'BTC')

    def test_asset_balance_dao_initialization(self, mock_db_connection):
        """Test AssetBalanceDAO initialization"""
        dao = AssetBalanceDAO(mock_db_connection)

        assert dao.db == mock_db_connection
        assert dao.table == mock_db_connection.users_table

    def test_asset_balance_dao_table_reference(self, mock_db_connection):
        """Test that AssetBalanceDAO uses correct table reference"""
        dao = AssetBalanceDAO(mock_db_connection)

        # Verify it uses users_table
        assert dao.table == mock_db_connection.users_table