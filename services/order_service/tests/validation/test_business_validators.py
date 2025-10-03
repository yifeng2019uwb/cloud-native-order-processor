"""
Unit tests for Order Service Business Validators

Testing business validation logic to improve coverage.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from common.data.entities.order.enums import OrderType, OrderStatus
from src.validation.business_validators import (
    _validate_username_exists_and_active,
    _validate_asset_exists_and_tradeable,
    _validate_asset_exists,
    _validate_user_balance_for_buy_order,
    validate_order_creation_business_rules,
    validate_order_cancellation_business_rules,
    validate_order_retrieval_business_rules,
    validate_order_listing_business_rules,
    validate_user_permissions,
    validate_market_conditions,
    validate_order_history_business_rules
)


# Import exceptions
from common.exceptions import CNOPAssetNotFoundException, CNOPOrderNotFoundException
from order_exceptions import CNOPOrderValidationException

# Define the interface as a list of method names
USER_DAO_SPEC = [
    'get_user_by_username',
    'get_user_by_email',
    'save_user',
    'delete_user',
    'update_user'
]

# Define AssetDAO interface
ASSET_DAO_SPEC = [
    'get_asset_by_id',
    'save_asset',
    'delete_asset',
    'update_asset'
]


class TestBusinessValidators:
    """Test class for business validation functions"""

    def test_validate_username_exists_and_active(self):
        """Test _validate_username_exists_and_active function"""
        # Create mock DAO with spec
        mock_user_dao = Mock(spec=USER_DAO_SPEC)

        # Test successful case - user exists
        mock_user = Mock()
        mock_user_dao.get_user_by_username.return_value = mock_user

        # Should not raise exception when user exists
        _validate_username_exists_and_active("testuser", mock_user_dao)

        # Verify the DAO method was called
        mock_user_dao.get_user_by_username.assert_called_once_with("testuser")

        # Test case where user doesn't exist (DAO raises exception)
        mock_user_dao.get_user_by_username.side_effect = Exception("User not found")

        with pytest.raises(CNOPOrderValidationException, match="User 'testuser' not found or invalid"):
            _validate_username_exists_and_active("testuser", mock_user_dao)

    def test_validate_asset_exists_and_tradeable(self):
        """Test _validate_asset_exists_and_tradeable function"""
        # Create mock DAO with spec
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)

        # Test successful case - asset exists and is active
        mock_asset = Mock()
        mock_asset.is_active = True
        mock_asset_dao.get_asset_by_id.return_value = mock_asset

        # Import and test the function

        # Should not raise exception when asset exists and is active
        _validate_asset_exists_and_tradeable("BTC", mock_asset_dao)

        # Verify the DAO method was called
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

        # Test case where asset is not active
        mock_asset.is_active = False
        with pytest.raises(CNOPOrderValidationException, match="Asset BTC is not tradeable"):
            _validate_asset_exists_and_tradeable("BTC", mock_asset_dao)

        # Test case where asset is not found
        mock_asset_dao.get_asset_by_id.side_effect = CNOPAssetNotFoundException("Asset not found")
        with pytest.raises(CNOPOrderValidationException, match="Asset BTC not found"):
            _validate_asset_exists_and_tradeable("BTC", mock_asset_dao)

    def test_validate_asset_exists(self):
        """Test _validate_asset_exists function"""
        # Create mock DAO with spec
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)

        # Test successful case - asset exists
        mock_asset_dao.get_asset_by_id.return_value = Mock()

        # Should not raise exception when asset exists
        _validate_asset_exists("ETH", mock_asset_dao)

        # Verify the DAO method was called
        mock_asset_dao.get_asset_by_id.assert_called_once_with("ETH")

        # Test case where asset is not found
        mock_asset_dao.get_asset_by_id.side_effect = CNOPAssetNotFoundException("Asset not found")
        with pytest.raises(CNOPOrderValidationException, match="Asset ETH not found"):
            _validate_asset_exists("ETH", mock_asset_dao)

    def test_validate_user_balance_for_buy_order(self):
        """Test _validate_user_balance_for_buy_order function"""
        # Define BalanceDAO interface
        BALANCE_DAO_SPEC = [
            'get_balance',
            'save_balance',
            'update_balance'
        ]

        # Create mock DAOs with spec
        mock_balance_dao = Mock(spec=BALANCE_DAO_SPEC)
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)

        # Test successful case - user has sufficient balance
        mock_balance = Mock()
        mock_balance.current_balance = Decimal("1000.00")
        mock_balance_dao.get_balance.return_value = mock_balance

        # Should not raise exception when user has sufficient balance
        _validate_user_balance_for_buy_order(
            "testuser",
            Decimal("1.0"),
            Decimal("100.00"),
            mock_balance_dao,
            mock_asset_dao,
            "BTC"
        )

        # Verify the DAO method was called
        mock_balance_dao.get_balance.assert_called_once_with("testuser")

        # Test market order case (order_price is None)
        # Mock the dependency function at the import location
        with patch('controllers.dependencies.get_current_market_price') as mock_get_price:
            mock_get_price.return_value = Decimal("500.00")

            # Test market order with sufficient balance
            mock_balance.current_balance = Decimal("1000.00")  # Sufficient for 1.0 * 500.00

            _validate_user_balance_for_buy_order(
                "testuser",
                Decimal("1.0"),
                None,  # order_price is None for market orders
                mock_balance_dao,
                mock_asset_dao,
                "BTC"
            )

            # Verify get_current_market_price was called
            mock_get_price.assert_called_once_with("BTC", mock_asset_dao)

        # Test market order case where market price lookup fails
        with patch('controllers.dependencies.get_current_market_price') as mock_get_price:
            mock_get_price.side_effect = Exception("Market price service unavailable")

            # Test market order with market price failure
            with pytest.raises(CNOPOrderValidationException, match="Unable to validate market order for BTC: Market price service unavailable"):
                _validate_user_balance_for_buy_order(
                    "testuser",
                    Decimal("1.0"),
                    None,  # order_price is None for market orders
                    mock_balance_dao,
                    mock_asset_dao,
                    "BTC"
                )


    def test_validate_order_creation_business_rules(self):
        """Test validate_order_creation_business_rules function"""
        # Create mock DAOs with specs
        mock_user_dao = Mock(spec=USER_DAO_SPEC)
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)
        mock_balance_dao = Mock(spec=['get_balance', 'save_balance', 'update_balance'])

        # Mock successful validations
        mock_user_dao.get_user_by_username.return_value = Mock()
        mock_asset_dao.get_asset_by_id.return_value = Mock(is_active=True)
        mock_balance_dao.get_balance.return_value = Mock(current_balance=Decimal("100000.00"))  # Sufficient for 1.0 * 50000.00

        # Test successful case - limit buy order with all required fields
        validate_order_creation_business_rules(
            OrderType.LIMIT_BUY,
            "BTC",
            Decimal("1.0"),
            Decimal("50000.00"),  # order_price
            datetime.now() + timedelta(days=1),  # expires_at
            "testuser",
            mock_asset_dao,
            mock_user_dao,
            mock_balance_dao,
        )

        # Test limit order without order_price
        with pytest.raises(CNOPOrderValidationException, match="order_price is required for limit_buy orders"):
            validate_order_creation_business_rules(
                OrderType.LIMIT_BUY,
                "BTC",
                Decimal("1.0"),
                None,  # order_price missing
                datetime.now() + timedelta(days=1),
                "testuser",
                mock_asset_dao,
                mock_user_dao,
                mock_balance_dao,
            )

        # Test limit order without expires_at
        with pytest.raises(CNOPOrderValidationException, match="expires_at is required for limit orders"):
            validate_order_creation_business_rules(
                OrderType.LIMIT_BUY,
                "BTC",
                Decimal("1.0"),
                Decimal("50000.00"),
                None,  # expires_at missing
                "testuser",
                mock_asset_dao,
                mock_user_dao,
                mock_balance_dao,
            )

        # Test quantity below minimum threshold
        with pytest.raises(CNOPOrderValidationException, match="Order quantity below minimum threshold"):
            validate_order_creation_business_rules(
                OrderType.MARKET_BUY,
                "BTC",
                Decimal("0.0001"),  # Below 0.001
                None,
                None,
                "testuser",
                mock_asset_dao,
                mock_user_dao,
                mock_balance_dao,
            )

        # Test quantity above maximum threshold
        with pytest.raises(CNOPOrderValidationException, match="Order quantity exceeds maximum threshold"):
            validate_order_creation_business_rules(
                OrderType.MARKET_BUY,
                "BTC",
                Decimal("1500.0"),  # Above 1000
                None,
                None,
                "testuser",
                mock_asset_dao,
                mock_user_dao,
                mock_balance_dao,
            )

    def test_validate_order_cancellation_business_rules(self):
        """Test validate_order_cancellation_business_rules function"""
        # Define OrderDAO interface
        ORDER_DAO_SPEC = [
            'get_order',
            'save_order',
            'update_order',
            'delete_order'
        ]

        # Create mock DAOs with specs
        mock_order_dao = Mock(spec=ORDER_DAO_SPEC)
        mock_user_dao = Mock(spec=USER_DAO_SPEC)

        # Mock successful validations
        mock_user_dao.get_user_by_username.return_value = Mock()

        # Test successful case - limit order in pending state
        mock_order = Mock()
        mock_order.username = "testuser"
        mock_order.order_type = OrderType.LIMIT_BUY
        mock_order.status = OrderStatus.PENDING
        mock_order_dao.get_order.return_value = mock_order

        validate_order_cancellation_business_rules("order123", "testuser", mock_order_dao, mock_user_dao)

        # Verify the DAO method was called
        mock_order_dao.get_order.assert_called_once_with("order123")

        # Test case where order belongs to different user
        mock_order.username = "otheruser"
        with pytest.raises(CNOPOrderValidationException, match="You can only cancel your own orders"):
            validate_order_cancellation_business_rules("order123", "testuser", mock_order_dao, mock_user_dao)

        # Test case where order is market order (cannot be cancelled)
        mock_order.username = "testuser"
        mock_order.order_type = OrderType.MARKET_BUY
        with pytest.raises(CNOPOrderValidationException, match="Market orders cannot be cancelled"):
            validate_order_cancellation_business_rules("order123", "testuser", mock_order_dao, mock_user_dao)

        # Test case where order is in non-cancellable state
        mock_order.order_type = OrderType.LIMIT_BUY
        mock_order.status = OrderStatus.COMPLETED
        with pytest.raises(CNOPOrderValidationException, match="Order in this state cannot be cancelled in completed state"):
            validate_order_cancellation_business_rules("order123", "testuser", mock_order_dao, mock_user_dao)

        # Test case where order is not found
        mock_order_dao.get_order.side_effect = CNOPOrderNotFoundException("Order not found")
        with pytest.raises(CNOPOrderValidationException, match="Order order123 not found"):
            validate_order_cancellation_business_rules("order123", "testuser", mock_order_dao, mock_user_dao)

    def test_validate_order_retrieval_business_rules(self):
        """Test validate_order_retrieval_business_rules function"""
        # Create mock DAOs with specs
        mock_order_dao = Mock(spec=['get_order', 'save_order', 'update_order', 'delete_order'])
        mock_user_dao = Mock(spec=USER_DAO_SPEC)

        # Mock successful validations
        mock_user_dao.get_user_by_username.return_value = Mock()

        # Import and test the function

        # Test successful case - order exists and belongs to user
        mock_order = Mock()
        mock_order.username = "testuser"
        mock_order_dao.get_order.return_value = mock_order

        validate_order_retrieval_business_rules("order123", "testuser", mock_order_dao, mock_user_dao)

        # Verify the DAO method was called
        mock_order_dao.get_order.assert_called_once_with("order123")

        # Test case where order belongs to different user
        mock_order.username = "otheruser"
        with pytest.raises(CNOPOrderValidationException, match="You can only view your own orders"):
            validate_order_retrieval_business_rules("order123", "testuser", mock_order_dao, mock_user_dao)

        # Test case where order is not found
        mock_order_dao.get_order.side_effect = CNOPOrderNotFoundException("Order not found")
        with pytest.raises(CNOPOrderNotFoundException, match="Order order123 not found"):
            validate_order_retrieval_business_rules("order123", "testuser", mock_order_dao, mock_user_dao)

    def test_validate_order_listing_business_rules(self):
        """Test validate_order_listing_business_rules function"""
        # Create mock DAOs with specs
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)
        mock_user_dao = Mock(spec=USER_DAO_SPEC)

        # Mock successful validations
        mock_user_dao.get_user_by_username.return_value = Mock()

        # Import and test the function

        # Test successful case - no asset filtering
        validate_order_listing_business_rules("testuser", None, None, mock_asset_dao, mock_user_dao)

        # Test successful case - with asset filtering (asset exists)
        mock_asset_dao.get_asset_by_id.return_value = Mock()
        validate_order_listing_business_rules("testuser", None, "BTC", mock_asset_dao, mock_user_dao)

        # Verify the asset validation was called when asset_id is provided
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

        # Test case where asset filtering fails (asset not found)
        mock_asset_dao.get_asset_by_id.side_effect = CNOPAssetNotFoundException("Asset not found")
        with pytest.raises(CNOPOrderValidationException, match="Asset BTC not found"):
            validate_order_listing_business_rules("testuser", None, "BTC", mock_asset_dao, mock_user_dao)

    def test_validate_order_history_business_rules(self):
        """Test validate_order_history_business_rules function"""
        # Create mock DAOs with specs
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)
        mock_user_dao = Mock(spec=USER_DAO_SPEC)

        # Mock successful validations
        mock_user_dao.get_user_by_username.return_value = Mock()
        mock_asset_dao.get_asset_by_id.return_value = Mock()

        # Test successful case - user exists and asset exists
        validate_order_history_business_rules("BTC", "testuser", mock_asset_dao, mock_user_dao)

        # Verify both validation functions were called
        mock_user_dao.get_user_by_username.assert_called_once_with("testuser")
        mock_asset_dao.get_asset_by_id.assert_called_once_with("BTC")

        # Test case where asset validation fails
        mock_asset_dao.get_asset_by_id.side_effect = CNOPAssetNotFoundException("Asset not found")
        with pytest.raises(CNOPOrderValidationException, match="Asset BTC not found"):
            validate_order_history_business_rules("BTC", "testuser", mock_asset_dao, mock_user_dao)

    def test_validate_market_conditions(self):
        """Test validate_market_conditions function"""

        # Test successful case - small order quantity (below threshold)
        validate_market_conditions("BTC", OrderType.MARKET_BUY, Decimal("50.0"))

        # Test successful case - order quantity exactly at threshold
        validate_market_conditions("BTC", OrderType.LIMIT_SELL, Decimal("100.0"))

        # Test successful case - large order quantity (above threshold)
        # This should pass since the function currently just has a placeholder (pass)
        validate_market_conditions("BTC", OrderType.MARKET_BUY, Decimal("150.0"))

        # Test with different asset and order type combinations
        validate_market_conditions("ETH", OrderType.LIMIT_BUY, Decimal("200.0"))
        validate_market_conditions("XRP", OrderType.MARKET_SELL, Decimal("500.0"))

    def test_validate_user_permissions(self):
        """Test validate_user_permissions function"""
        # Create mock DAO with spec
        mock_user_dao = Mock(spec=USER_DAO_SPEC)

        # Mock successful validations
        mock_user_dao.get_user_by_username.return_value = Mock()

        # Test successful case - user exists and is active
        validate_user_permissions("testuser", "create_order", mock_user_dao)

        # Verify the validation function was called
        mock_user_dao.get_user_by_username.assert_called_once_with("testuser")

        # Test with different actions
        validate_user_permissions("testuser", "cancel_order", mock_user_dao)
        validate_user_permissions("testuser", "view_orders", mock_user_dao)
        validate_user_permissions("testuser", "modify_order", mock_user_dao)

        # Test with different usernames
        validate_user_permissions("otheruser", "create_order", mock_user_dao)
        validate_user_permissions("adminuser", "delete_order", mock_user_dao)

    def test_validate_order_creation_business_rules_sell_order_validation(self):
        """Test line 203: sell order validation call in validate_order_creation_business_rules"""
        # Import enums

        # Create mock DAOs with specs
        mock_user_dao = Mock(spec=USER_DAO_SPEC)
        mock_asset_dao = Mock(spec=ASSET_DAO_SPEC)
        mock_balance_dao = Mock(spec=['get_balance', 'save_balance', 'update_balance'])

        # Mock successful validations
        mock_user_dao.get_user_by_username.return_value = Mock()
        mock_asset_dao.get_asset_by_id.return_value = Mock(is_active=True)
        # Test sell order case - no longer validates asset balance (moved to user service)
        validate_order_creation_business_rules(
            OrderType.MARKET_SELL,
            "BTC",
            Decimal("5.0"),
            None,  # order_price not needed for market sell
            None,  # expires_at not needed for market sell
            "testuser",
            mock_asset_dao,
            mock_user_dao,
            mock_balance_dao,
        )
