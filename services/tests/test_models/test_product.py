import pytest
from datetime import datetime
from decimal import Decimal
from pydantic import ValidationError

from models.product import ProductCreate, Product


class TestProductCreate:
    """Test cases for ProductCreate model."""

    def test_product_create_success(self):
        """Test successful ProductCreate creation."""
        product = ProductCreate(
            sku="TEST-SKU-001",
            name="Test Product",
            description="A test product for unit testing",
            price=Decimal("29.99"),
            category="Electronics",
        )

        assert product.sku == "TEST-SKU-001"
        assert product.name == "Test Product"
        assert product.description == "A test product for unit testing"
        assert product.price == Decimal("29.99")
        assert product.category == "Electronics"

    def test_product_create_required_fields(self):
        """Test that required fields are enforced."""
        base_data = {
            "sku": "TEST-SKU-001",
            "name": "Test Product",
            "price": Decimal("29.99"),
            "category": "Electronics",
        }

        required_fields = ["sku", "name", "price", "category"]

        for field in required_fields:
            test_data = base_data.copy()
            del test_data[field]

            with pytest.raises(ValidationError) as exc_info:
                ProductCreate(**test_data)
            assert field in str(exc_info.value)

    def test_product_create_optional_description(self):
        """Test that description is optional."""
        product = ProductCreate(
            sku="TEST-SKU-001",
            name="Test Product",
            price=Decimal("29.99"),
            category="Electronics",
            # description not provided
        )

        assert product.description is None

    def test_product_create_with_none_description(self):
        """Test ProductCreate with explicitly None description."""
        product = ProductCreate(
            sku="TEST-SKU-001",
            name="Test Product",
            description=None,
            price=Decimal("29.99"),
            category="Electronics",
        )

        assert product.description is None

    def test_product_create_price_validation(self):
        """Test price field validation."""
        # Negative price should be invalid
        with pytest.raises(ValidationError):
            ProductCreate(
                sku="TEST-SKU-001",
                name="Test Product",
                price=Decimal("-10.00"),
                category="Electronics",
            )

        # Zero price should be valid
        product = ProductCreate(
            sku="TEST-SKU-001",
            name="Test Product",
            price=Decimal("0.00"),
            category="Electronics",
        )
        assert product.price == Decimal("0.00")

        # Very high precision should work
        product = ProductCreate(
            sku="TEST-SKU-001",
            name="Test Product",
            price=Decimal("123.456789"),
            category="Electronics",
        )
        assert product.price == Decimal("123.456789")

    def test_product_create_string_fields_validation(self):
        """Test string field validation."""
        # Empty string should be invalid for required fields
        with pytest.raises(ValidationError):
            ProductCreate(
                sku="",
                name="Test Product",
                price=Decimal("29.99"),
                category="Electronics",
            )

        with pytest.raises(ValidationError):
            ProductCreate(
                sku="TEST-SKU-001",
                name="",
                price=Decimal("29.99"),
                category="Electronics",
            )

        with pytest.raises(ValidationError):
            ProductCreate(
                sku="TEST-SKU-001",
                name="Test Product",
                price=Decimal("29.99"),
                category="",
            )

    def test_product_create_serialization(self):
        """Test ProductCreate JSON serialization."""
        product = ProductCreate(
            sku="TEST-SKU-001",
            name="Test Product",
            description="A test product",
            price=Decimal("29.99"),
            category="Electronics",
        )

        json_str = product.model_dump_json()
        assert "TEST-SKU-001" in json_str
        assert "Test Product" in json_str
        assert "29.99" in json_str
        assert "Electronics" in json_str

    def test_product_create_deserialization(self):
        """Test ProductCreate JSON deserialization."""
        json_data = {
            "sku": "TEST-SKU-001",
            "name": "Test Product",
            "description": "A test product",
            "price": "29.99",
            "category": "Electronics",
        }

        product = ProductCreate(**json_data)
        assert product.price == Decimal("29.99")

    def test_product_create_special_characters(self):
        """Test ProductCreate with special characters."""
        product = ProductCreate(
            sku="TEST-SKU-001",
            name="Test Product with Special Chars: !@#$%",
            description="Description with émojis 🚀 and ñoñó",
            price=Decimal("29.99"),
            category="Electronics & Gadgets",
        )

        assert "Special Chars" in product.name
        assert "émojis" in product.description
        assert "&" in product.category


class TestProduct:
    """Test cases for Product model."""

    def test_product_creation_success(self, sample_product_data):
        """Test successful Product creation."""
        product = Product(**sample_product_data)

        assert product.product_id == "prod-123"
        assert product.sku == "TEST-SKU-001"
        assert product.name == "Test Product"
        assert product.description == "A test product"
        assert product.price == Decimal("29.99")
        assert product.category == "Electronics"
        assert isinstance(product.created_at, datetime)
        assert isinstance(product.updated_at, datetime)

    def test_product_required_fields(self):
        """Test that all fields are required."""
        base_data = {
            "product_id": "prod-123",
            "sku": "TEST-SKU-001",
            "name": "Test Product",
            "price": Decimal("29.99"),
            "category": "Electronics",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        required_fields = [
            "product_id",
            "sku",
            "name",
            "price",
            "category",
            "created_at",
            "updated_at",
        ]

        for field in required_fields:
            test_data = base_data.copy()
            del test_data[field]

            with pytest.raises(ValidationError) as exc_info:
                Product(**test_data)
            assert field in str(exc_info.value)

    def test_product_optional_description(self):
        """Test that description is optional in Product."""
        product = Product(
            product_id="prod-123",
            sku="TEST-SKU-001",
            name="Test Product",
            price=Decimal("29.99"),
            category="Electronics",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            # description not provided
        )

        assert product.description is None

    def test_product_with_description(self):
        """Test Product with description."""
        product = Product(
            product_id="prod-123",
            sku="TEST-SKU-001",
            name="Test Product",
            description="A detailed product description",
            price=Decimal("29.99"),
            category="Electronics",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert product.description == "A detailed product description"

    def test_product_datetime_fields(self):
        """Test that datetime fields are properly handled."""
        created_at = datetime(2024, 1, 1, 10, 0, 0)
        updated_at = datetime(2024, 1, 1, 12, 0, 0)

        product = Product(
            product_id="prod-123",
            sku="TEST-SKU-001",
            name="Test Product",
            price=Decimal("29.99"),
            category="Electronics",
            created_at=created_at,
            updated_at=updated_at,
        )

        assert product.created_at == created_at
        assert product.updated_at == updated_at

    def test_product_price_precision(self):
        """Test that Product maintains price precision."""
        high_precision_price = Decimal("123.456789")

        product = Product(
            product_id="prod-123",
            sku="TEST-SKU-001",
            name="Test Product",
            price=high_precision_price,
            category="Electronics",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert product.price == high_precision_price

    def test_product_serialization(self, sample_product_data):
        """Test Product JSON serialization."""
        product = Product(**sample_product_data)

        json_str = product.model_dump_json()
        assert "prod-123" in json_str
        assert "TEST-SKU-001" in json_str
        assert "Test Product" in json_str
        assert "29.99" in json_str

    def test_product_deserialization(self):
        """Test Product JSON deserialization."""
        json_data = {
            "product_id": "prod-123",
            "sku": "TEST-SKU-001",
            "name": "Test Product",
            "description": "A test product",
            "price": "29.99",
            "category": "Electronics",
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-01T12:00:00",
        }

        product = Product(**json_data)
        assert product.price == Decimal("29.99")
        assert isinstance(product.created_at, datetime)

    def test_product_id_validation(self):
        """Test product_id field validation."""
        # Empty product_id should be invalid
        with pytest.raises(ValidationError):
            Product(
                product_id="",
                sku="TEST-SKU-001",
                name="Test Product",
                price=Decimal("29.99"),
                category="Electronics",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_product_sku_uniqueness_assumption(self):
        """Test that SKU should be unique (business logic assumption)."""
        # Note: This test documents the assumption that SKUs should be unique
        # The actual uniqueness constraint would be enforced at the database level

        sku = "UNIQUE-SKU-001"

        product1 = Product(
            product_id="prod-123",
            sku=sku,
            name="Product 1",
            price=Decimal("29.99"),
            category="Electronics",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        product2 = Product(
            product_id="prod-456",
            sku=sku,  # Same SKU - should be prevented at business logic level
            name="Product 2",
            price=Decimal("39.99"),
            category="Electronics",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Both products can be created (model doesn't enforce uniqueness)
        # But business logic should prevent this
        assert product1.sku == product2.sku
        assert product1.product_id != product2.product_id


class TestProductModelsIntegration:
    """Integration tests for Product models."""

    def test_product_create_to_product_workflow(self):
        """Test the workflow from ProductCreate to Product."""
        # Start with ProductCreate
        product_create = ProductCreate(
            sku="NEW-PRODUCT-001",
            name="New Product",
            description="A newly created product",
            price=Decimal("49.99"),
            category="Home & Garden",
        )

        # Simulate creating a Product from ProductCreate
        now = datetime.now()
        product = Product(
            product_id="generated-product-id",
            sku=product_create.sku,
            name=product_create.name,
            description=product_create.description,
            price=product_create.price,
            category=product_create.category,
            created_at=now,
            updated_at=now,
        )

        # Verify consistency
        assert product.sku == product_create.sku
        assert product.name == product_create.name
        assert product.description == product_create.description
        assert product.price == product_create.price
        assert product.category == product_create.category

    def test_product_update_simulation(self):
        """Test simulating a product update."""
        # Original product
        original_product = Product(
            product_id="prod-123",
            sku="TEST-SKU-001",
            name="Original Product",
            description="Original description",
            price=Decimal("29.99"),
            category="Electronics",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
        )

        # Update data
        update_data = ProductCreate(
            sku="TEST-SKU-001",  # SKU typically doesn't change
            name="Updated Product Name",
            description="Updated description with more details",
            price=Decimal("34.99"),
            category="Electronics",
        )

        # Simulate applying update
        updated_product = original_product.model_copy(
            update={
                "name": update_data.name,
                "description": update_data.description,
                "price": update_data.price,
                "category": update_data.category,
                "updated_at": datetime.now(),
            }
        )

        assert updated_product.product_id == original_product.product_id
        assert updated_product.sku == original_product.sku
        assert updated_product.created_at == original_product.created_at
        assert updated_product.name == update_data.name
        assert updated_product.price == update_data.price
        assert updated_product.updated_at > original_product.updated_at

    def test_product_models_field_compatibility(self):
        """Test that ProductCreate and Product have compatible fields."""
        product_create_fields = set(ProductCreate.model_fields.keys())
        product_fields = set(Product.model_fields.keys())

        # ProductCreate fields should be a subset of Product fields
        # (except for the additional fields in Product like product_id, timestamps)
        create_only_fields = product_create_fields - product_fields
        assert (
            len(create_only_fields) == 0
        ), f"ProductCreate has fields not in Product: {create_only_fields}"

        # Product should have additional fields
        product_only_fields = product_fields - product_create_fields
        expected_additional_fields = {"product_id", "created_at", "updated_at"}
        assert product_only_fields == expected_additional_fields
