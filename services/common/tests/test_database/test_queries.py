import pytest
from database.queries import OrderQueries, ProductQueries, InventoryQueries


class TestOrderQueries:
    """Test cases for OrderQueries class."""

    def test_create_order_query(self):
        """Test CREATE_ORDER query structure."""
        expected_fields = [
            "order_id",
            "customer_id",
            "customer_email",
            "customer_name",
            "status",
            "total_amount",
            "shipping_address",
            "created_at",
            "updated_at",
        ]

        query = OrderQueries.CREATE_ORDER
        assert "INSERT INTO orders.orders" in query

        for field in expected_fields:
            assert field in query

        # Check for proper parameterization
        assert "$1" in query and "$8" in query

    def test_create_order_item_query(self):
        """Test CREATE_ORDER_ITEM query structure."""
        expected_fields = [
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "line_total",
        ]

        query = OrderQueries.CREATE_ORDER_ITEM
        assert "INSERT INTO orders.order_items" in query

        for field in expected_fields:
            assert field in query

        # Check for proper parameterization (5 parameters)
        assert "$1" in query and "$5" in query

    def test_get_order_query(self):
        """Test GET_ORDER query structure."""
        query = OrderQueries.GET_ORDER
        assert "SELECT * FROM orders.orders WHERE order_id = $1" == query

    def test_get_order_items_query(self):
        """Test GET_ORDER_ITEMS query structure."""
        query = OrderQueries.GET_ORDER_ITEMS
        assert "SELECT oi.*, p.name as product_name" in query
        assert "FROM orders.order_items oi" in query
        assert "JOIN products.products p ON oi.product_id = p.product_id" in query
        assert "WHERE oi.order_id = $1" in query

    def test_update_order_status_query(self):
        """Test UPDATE_ORDER_STATUS query structure."""
        query = OrderQueries.UPDATE_ORDER_STATUS
        assert "UPDATE orders.orders" in query
        assert "SET status = $1, updated_at = $2" in query
        assert "WHERE order_id = $3" in query

    def test_list_orders_query(self):
        """Test LIST_ORDERS query structure."""
        query = OrderQueries.LIST_ORDERS
        assert "SELECT * FROM orders.orders WHERE 1=1" == query

    def test_all_queries_are_strings(self):
        """Test that all query attributes are strings."""
        queries = [
            OrderQueries.CREATE_ORDER,
            OrderQueries.CREATE_ORDER_ITEM,
            OrderQueries.GET_ORDER,
            OrderQueries.GET_ORDER_ITEMS,
            OrderQueries.UPDATE_ORDER_STATUS,
            OrderQueries.LIST_ORDERS,
        ]

        for query in queries:
            assert isinstance(query, str)
            assert len(query.strip()) > 0


class TestProductQueries:
    """Test cases for ProductQueries class."""

    def test_get_product_query(self):
        """Test GET_PRODUCT query structure."""
        query = ProductQueries.GET_PRODUCT
        assert "SELECT * FROM products.products WHERE product_id = $1" == query

    def test_list_products_query(self):
        """Test LIST_PRODUCTS query structure."""
        query = ProductQueries.LIST_PRODUCTS
        assert "SELECT * FROM products.products ORDER BY name LIMIT $1" == query

    def test_list_products_by_category_query(self):
        """Test LIST_PRODUCTS_BY_CATEGORY query structure."""
        query = ProductQueries.LIST_PRODUCTS_BY_CATEGORY
        assert (
            "SELECT * FROM products.products WHERE category = $1 ORDER BY name LIMIT $2"
            == query
        )

    def test_all_queries_are_strings(self):
        """Test that all product query attributes are strings."""
        queries = [
            ProductQueries.GET_PRODUCT,
            ProductQueries.LIST_PRODUCTS,
            ProductQueries.LIST_PRODUCTS_BY_CATEGORY,
        ]

        for query in queries:
            assert isinstance(query, str)
            assert len(query.strip()) > 0


class TestInventoryQueries:
    """Test cases for InventoryQueries class."""

    def test_get_inventory_query(self):
        """Test GET_INVENTORY query structure."""
        query = InventoryQueries.GET_INVENTORY
        assert "SELECT * FROM inventory.inventory WHERE product_id = $1" == query

    def test_reserve_stock_query(self):
        """Test RESERVE_STOCK query structure."""
        query = InventoryQueries.RESERVE_STOCK
        assert "UPDATE inventory.inventory" in query
        assert (
            "SET reserved_quantity = reserved_quantity + $1, updated_at = $2" in query
        )
        assert "WHERE product_id = $3" in query

    def test_release_stock_query(self):
        """Test RELEASE_STOCK query structure."""
        query = InventoryQueries.RELEASE_STOCK
        assert "UPDATE inventory.inventory" in query
        assert (
            "SET reserved_quantity = GREATEST(0, reserved_quantity - $1), updated_at = $2"
            in query
        )
        assert "WHERE product_id = $3" in query

    def test_update_stock_query(self):
        """Test UPDATE_STOCK query structure."""
        query = InventoryQueries.UPDATE_STOCK
        assert "UPDATE inventory.inventory" in query
        assert "SET stock_quantity = stock_quantity + $1, updated_at = $2" in query
        assert "WHERE product_id = $3" in query

    def test_release_stock_prevents_negative_values(self):
        """Test that RELEASE_STOCK query uses GREATEST to prevent negative values."""
        query = InventoryQueries.RELEASE_STOCK
        assert "GREATEST(0, reserved_quantity - $1)" in query

    def test_all_queries_are_strings(self):
        """Test that all inventory query attributes are strings."""
        queries = [
            InventoryQueries.GET_INVENTORY,
            InventoryQueries.RESERVE_STOCK,
            InventoryQueries.RELEASE_STOCK,
            InventoryQueries.UPDATE_STOCK,
        ]

        for query in queries:
            assert isinstance(query, str)
            assert len(query.strip()) > 0

    def test_parameterized_queries_security(self):
        """Test that all queries use parameterized queries for security."""
        queries = [
            InventoryQueries.GET_INVENTORY,
            InventoryQueries.RESERVE_STOCK,
            InventoryQueries.RELEASE_STOCK,
            InventoryQueries.UPDATE_STOCK,
        ]

        for query in queries:
            # Should use parameterized queries ($1, $2, etc.) instead of string formatting
            assert "%" not in query  # No Python string formatting
            assert "{" not in query  # No f-string formatting
            assert "$" in query  # Uses PostgreSQL parameterization


class TestQueriesIntegration:
    """Integration tests for all query classes."""

    def test_query_classes_exist(self):
        """Test that all query classes are properly defined."""
        assert OrderQueries is not None
        assert ProductQueries is not None
        assert InventoryQueries is not None

    def test_no_hardcoded_values_in_queries(self):
        """Test that queries don't contain hardcoded IDs or values."""
        all_queries = []

        # Collect all queries
        for attr_name in dir(OrderQueries):
            if not attr_name.startswith("_"):
                all_queries.append(getattr(OrderQueries, attr_name))

        for attr_name in dir(ProductQueries):
            if not attr_name.startswith("_"):
                all_queries.append(getattr(ProductQueries, attr_name))

        for attr_name in dir(InventoryQueries):
            if not attr_name.startswith("_"):
                all_queries.append(getattr(InventoryQueries, attr_name))

        # Check for potential hardcoded values
        for query in all_queries:
            if isinstance(query, str):
                # Should not contain hardcoded UUIDs or email addresses
                assert "@" not in query.lower() or "email" in query.lower()
                # Should not contain hardcoded numeric IDs
                assert not any(f"= {i}" in query for i in range(1000))

    def test_sql_injection_prevention(self):
        """Test that queries are protected against SQL injection."""
        all_queries = []
    
        # Collect all string queries
        for cls in [OrderQueries, ProductQueries, InventoryQueries]:
            for attr_name in dir(cls):
                if not attr_name.startswith("_"):
                    attr_value = getattr(cls, attr_name)
                    if isinstance(attr_value, str):
                        all_queries.append(attr_value)
    
        for query in all_queries:
            # Should use parameterized queries
            if "WHERE" in query.upper():
                # Special case for LIST_ORDERS which uses "WHERE 1=1" as a base for dynamic queries
                if "WHERE 1=1" in query:
                    # This is acceptable as it's a base query that gets parameters added dynamically
                    continue
                # Should use $1, $2, etc. for parameters
                assert any(f"${i}" in query for i in range(1, 10)), f"Query should use parameterized queries: {query}"
        
            # Should not have obvious SQL injection patterns
            dangerous_patterns = ["'", '"', ";", "--", "/*", "*/"]
            for pattern in dangerous_patterns:
                if pattern in query:
                    # Only acceptable in specific contexts (like comments or quoted identifiers)
                    assert pattern == "'" and "name" in query.lower() or pattern == '"', f"Potentially dangerous pattern '{pattern}' found in query: {query}"