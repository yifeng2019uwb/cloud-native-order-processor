import pytest
import bcrypt
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from database.dao.user_dao import UserDAO
from models.user import UserCreate, User


class TestUserDAO:
    """Test UserDAO database operations"""

    @pytest.fixture
    def mock_db_connection(self):
        """Create mock database connection"""
        mock_connection = Mock()
        mock_connection.orders_table = Mock()
        return mock_connection

    @pytest.fixture
    def user_dao(self, mock_db_connection):
        """Create UserDAO instance with mock connection"""
        return UserDAO(mock_db_connection)

    @pytest.fixture
    def sample_user_create(self):
        """Sample user creation data"""
        return UserCreate(
            email="test@example.com",
            password="ValidPass123!",
            name="Test User",
            phone="+1234567890"
        )

    @pytest.fixture
    def sample_user(self):
        """Sample user data"""
        return User(
            email="test@example.com",
            name="Test User",
            phone="+1234567890",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    def test_get_entity_type(self, user_dao):
        """Test entity type method"""
        assert user_dao._get_entity_type() == "USER"

    def test_hash_password(self, user_dao):
        """Test password hashing"""
        password = "TestPassword123!"
        hashed = user_dao._hash_password(password)

        # Check that hash is different from original
        assert hashed != password

        # Check that hash can be verified
        assert bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def test_verify_password(self, user_dao):
        """Test password verification"""
        password = "TestPassword123!"
        hashed = user_dao._hash_password(password)

        # Correct password should verify
        assert user_dao._verify_password(password, hashed) is True

        # Wrong password should not verify
        assert user_dao._verify_password("WrongPassword123!", hashed) is False

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_dao, sample_user_create, mock_db_connection):
        """Test successful user creation"""
        # Mock that user doesn't exist
        user_dao.get_user_by_email = AsyncMock(return_value=None)

        # Mock successful database operations
        mock_db_connection.orders_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Create user
        result = await user_dao.create_user(sample_user_create)

        # Verify result
        assert isinstance(result, User)
        assert result.email == sample_user_create.email
        assert result.name == sample_user_create.name
        assert result.phone == sample_user_create.phone
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)

        # Verify database was called
        mock_db_connection.orders_table.put_item.assert_called_once()
        call_args = mock_db_connection.orders_table.put_item.call_args[1]['Item']
        assert call_args['PK'] == f"USER#{sample_user_create.email}"
        assert call_args['SK'] == 'PROFILE'
        assert call_args['entity_type'] == 'USER'
        assert 'password_hash' in call_args

    @pytest.mark.asyncio
    async def test_create_user_already_exists(self, user_dao, sample_user_create, sample_user):
        """Test creating user that already exists"""
        # Mock that user already exists
        user_dao.get_user_by_email = AsyncMock(return_value=sample_user)

        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            await user_dao.create_user(sample_user_create)

        assert "already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self, user_dao, mock_db_connection):
        """Test getting user that exists"""
        # Mock database response
        mock_item = {
            'email': 'test@example.com',
            'name': 'Test User',
            'phone': '+1234567890',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
        mock_db_connection.orders_table.get_item.return_value = {'Item': mock_item}

        # Get user
        result = await user_dao.get_user_by_email('test@example.com')

        # Verify result
        assert isinstance(result, User)
        assert result.email == 'test@example.com'
        assert result.name == 'Test User'
        assert result.phone == '+1234567890'

        # Verify database was called correctly
        mock_db_connection.orders_table.get_item.assert_called_once_with(
            Key={
                'PK': 'USER#test@example.com',
                'SK': 'PROFILE'
            }
        )

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, user_dao, mock_db_connection):
        """Test getting user that doesn't exist"""
        # Mock database response - no item
        mock_db_connection.orders_table.get_item.return_value = {}

        # Get user
        result = await user_dao.get_user_by_email('nonexistent@example.com')

        # Should return None
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, user_dao, mock_db_connection):
        """Test successful user authentication"""
        # Create a real password hash
        password = "TestPassword123!"
        password_hash = user_dao._hash_password(password)

        # Mock database response
        mock_item = {
            'email': 'test@example.com',
            'name': 'Test User',
            'phone': '+1234567890',
            'password_hash': password_hash,
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
        mock_db_connection.orders_table.get_item.return_value = {'Item': mock_item}

        # Authenticate user
        result = await user_dao.authenticate_user('test@example.com', password)

        # Verify result
        assert isinstance(result, User)
        assert result.email == 'test@example.com'

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, user_dao, mock_db_connection):
        """Test authentication with wrong password"""
        # Create a password hash
        password_hash = user_dao._hash_password("CorrectPassword123!")

        # Mock database response
        mock_item = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password_hash': password_hash,
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
        mock_db_connection.orders_table.get_item.return_value = {'Item': mock_item}

        # Try to authenticate with wrong password
        result = await user_dao.authenticate_user('test@example.com', 'WrongPassword123!')

        # Should return None
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, user_dao, mock_db_connection):
        """Test authentication for non-existent user"""
        # Mock database response - no item
        mock_db_connection.orders_table.get_item.return_value = {}

        # Try to authenticate
        result = await user_dao.authenticate_user('nonexistent@example.com', 'password')

        # Should return None
        assert result is None

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_dao, mock_db_connection):
        """Test successful user update"""
        # Mock database response
        updated_item = {
            'email': 'test@example.com',
            'name': 'Updated Name',
            'phone': '+9876543210',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-02T00:00:00'
        }
        mock_db_connection.orders_table.update_item.return_value = {'Attributes': updated_item}

        # Update user
        result = await user_dao.update_user('test@example.com', name='Updated Name', phone='+9876543210')

        # Verify result
        assert isinstance(result, User)
        assert result.name == 'Updated Name'
        assert result.phone == '+9876543210'

        # Verify database was called
        mock_db_connection.orders_table.update_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_no_changes(self, user_dao):
        """Test update with no changes returns current user"""
        # Mock get_user_by_email
        mock_user = User(
            email='test@example.com',
            name='Test User',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        user_dao.get_user_by_email = AsyncMock(return_value=mock_user)

        # Update with no changes
        result = await user_dao.update_user('test@example.com')

        # Should return current user
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_dao, mock_db_connection):
        """Test updating non-existent user"""
        # Mock database response - no item returned
        mock_db_connection.orders_table.update_item.return_value = {}

        # Try to update
        result = await user_dao.update_user('nonexistent@example.com', name='New Name')

        # Should return None
        assert result is None


class TestBaseDAOIntegration:
    """Test that UserDAO properly inherits from BaseDAO"""

    @pytest.fixture
    def mock_db_connection(self):
        """Create mock database connection"""
        mock_connection = Mock()
        mock_connection.orders_table = Mock()
        return mock_connection

    @pytest.fixture
    def user_dao(self, mock_db_connection):
        """Create UserDAO instance with mock connection"""
        return UserDAO(mock_db_connection)

    def test_create_primary_key(self, user_dao):
        """Test primary key creation"""
        email = "test@example.com"
        pk = user_dao._create_primary_key(email)
        assert pk == "USER#test@example.com"

    def test_add_timestamps(self, user_dao):
        """Test timestamp addition"""
        item = {"email": "test@example.com"}

        # Test create timestamps
        result = user_dao._add_timestamps(item, is_create=True)
        assert 'created_at' in result
        assert 'updated_at' in result

        # Test update timestamps
        result = user_dao._add_timestamps(item, is_create=False)
        assert 'created_at' not in result or result['created_at'] == item.get('created_at')
        assert 'updated_at' in result

    def test_validate_required_fields(self, user_dao):
        """Test required field validation"""
        # Valid item
        item = {"email": "test@example.com", "name": "Test User"}
        user_dao._validate_required_fields(item, ["email", "name"])  # Should not raise

        # Missing field
        with pytest.raises(ValueError) as exc_info:
            user_dao._validate_required_fields(item, ["email", "name", "phone"])
        assert "Missing required fields" in str(exc_info.value)