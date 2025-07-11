import pytest
import bcrypt
from unittest.mock import Mock, AsyncMock
from datetime import datetime
import sys
import os

# Add the common directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.dao.user_dao import UserDAO
from entities.user import UserCreate, User, UserLogin


class TestUserDAO:
    """Test UserDAO database operations"""

    @pytest.fixture
    def mock_db_connection(self):
        """Create mock database connection"""
        mock_connection = Mock()
        mock_connection.users_table = Mock()
        return mock_connection

    @pytest.fixture
    def user_dao(self, mock_db_connection):
        """Create UserDAO instance with mock connection"""
        return UserDAO(mock_db_connection)

    @pytest.fixture
    def sample_user_create(self):
        """Sample user creation data with username"""
        return UserCreate(
            username="john_doe123",
            email="test@example.com",
            password="ValidPass123!",
            first_name="Test",
            last_name="User",
            phone="+1234567890"
        )

    @pytest.fixture
    def sample_user(self):
        """Sample user data with username"""
        return User(
            username="john_doe123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            phone="+1234567890",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

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
        user_dao.get_user_by_username = AsyncMock(return_value=None)
        user_dao.get_user_by_email = AsyncMock(return_value=None)

        # Mock successful database operations
        mock_db_connection.users_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Create user
        result = await user_dao.create_user(sample_user_create)

        # Verify result
        assert isinstance(result, User)
        assert result.username == sample_user_create.username
        assert result.email == sample_user_create.email
        assert result.first_name == sample_user_create.first_name
        assert result.last_name == sample_user_create.last_name
        assert result.phone == sample_user_create.phone
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)

        # Verify database was called with users_table
        mock_db_connection.users_table.put_item.assert_called_once()
        call_args = mock_db_connection.users_table.put_item.call_args[1]['Item']
        assert call_args['user_id'] == sample_user_create.username
        assert call_args['username'] == sample_user_create.username
        assert call_args['email'] == sample_user_create.email
        assert call_args['first_name'] == sample_user_create.first_name
        assert call_args['last_name'] == sample_user_create.last_name
        assert 'password_hash' in call_args

    @pytest.mark.asyncio
    async def test_create_user_username_exists(self, user_dao, sample_user_create, sample_user):
        """Test creating user with existing username"""
        # Mock that username already exists
        user_dao.get_user_by_username = AsyncMock(return_value=sample_user)
        user_dao.get_user_by_email = AsyncMock(return_value=None)

        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            await user_dao.create_user(sample_user_create)

        assert "username john_doe123 already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_user_email_exists(self, user_dao, sample_user_create, sample_user):
        """Test creating user with existing email"""
        # Mock that email already exists
        user_dao.get_user_by_username = AsyncMock(return_value=None)
        user_dao.get_user_by_email = AsyncMock(return_value=sample_user)

        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            await user_dao.create_user(sample_user_create)

        assert "email test@example.com already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_by_username_found(self, user_dao, mock_db_connection):
        """Test getting user by username (Primary Key lookup)"""
        # Mock database response
        mock_item = {
            'username': 'john_doe123',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+1234567890',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
        mock_db_connection.users_table.get_item.return_value = {'Item': mock_item}

        # Get user
        result = await user_dao.get_user_by_username('john_doe123')

        # Verify result
        assert isinstance(result, User)
        assert result.username == 'john_doe123'
        assert result.email == 'test@example.com'
        assert result.first_name == 'Test'
        assert result.last_name == 'User'
        assert result.phone == '+1234567890'

        # Verify database was called correctly
        mock_db_connection.users_table.get_item.assert_called_once_with(
            Key={'user_id': 'john_doe123'}
        )

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, user_dao, mock_db_connection):
        """Test getting user by username that doesn't exist"""
        # Mock database response - no item
        mock_db_connection.users_table.get_item.return_value = {}

        # Get user
        result = await user_dao.get_user_by_username('nonexistent')

        # Should return None
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self, user_dao, mock_db_connection):
        """Test getting user by email (GSI lookup)"""
        # Mock database response for GSI query
        mock_items = [{
            'username': 'john_doe123',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+1234567890',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }]
        mock_db_connection.users_table.query.return_value = {'Items': mock_items}

        # Get user
        result = await user_dao.get_user_by_email('test@example.com')

        # Verify result
        assert isinstance(result, User)
        assert result.username == 'john_doe123'
        assert result.email == 'test@example.com'
        assert result.first_name == 'Test'
        assert result.last_name == 'User'

        # Verify GSI query was called
        mock_db_connection.users_table.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, user_dao, mock_db_connection):
        """Test getting user by email that doesn't exist"""
        # Mock database response - no items
        mock_db_connection.users_table.query.return_value = {'Items': []}

        # Get user
        result = await user_dao.get_user_by_email('nonexistent@example.com')

        # Should return None
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_with_username_success(self, user_dao, mock_db_connection):
        """Test successful authentication with username"""
        # Create a real password hash
        password = "TestPassword123!"
        password_hash = user_dao._hash_password(password)

        # Mock user lookup by username
        mock_user = User(
            username='john_doe123',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            phone='+1234567890',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        user_dao.get_user_by_username = AsyncMock(return_value=mock_user)

        # Mock database response with password hash
        mock_item = {
            'username': 'john_doe123',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password_hash': password_hash,
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
        mock_db_connection.users_table.get_item.return_value = {'Item': mock_item}

        # Authenticate user with username
        result = await user_dao.authenticate_user('john_doe123', password)

        # Verify result
        assert isinstance(result, User)
        assert result.username == 'john_doe123'

    @pytest.mark.asyncio
    async def test_authenticate_user_with_email_success(self, user_dao, mock_db_connection):
        """Test successful authentication with email"""
        # Create a real password hash
        password = "TestPassword123!"
        password_hash = user_dao._hash_password(password)

        # Mock user lookup by email
        mock_user = User(
            username='john_doe123',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            phone='+1234567890',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        user_dao.get_user_by_email = AsyncMock(return_value=mock_user)

        # Mock database response with password hash
        mock_item = {
            'username': 'john_doe123',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password_hash': password_hash,
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
        mock_db_connection.users_table.get_item.return_value = {'Item': mock_item}

        # Authenticate user with email
        result = await user_dao.authenticate_user('test@example.com', password)

        # Verify result
        assert isinstance(result, User)
        assert result.username == 'john_doe123'

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, user_dao, mock_db_connection):
        """Test authentication with wrong password"""
        # Create a password hash
        correct_password = "CorrectPassword123!"
        password_hash = user_dao._hash_password(correct_password)

        # Mock user lookup
        mock_user = User(
            username='john_doe123',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        user_dao.get_user_by_username = AsyncMock(return_value=mock_user)

        # Mock database response
        mock_item = {
            'username': 'john_doe123',
            'password_hash': password_hash,
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-01T00:00:00'
        }
        mock_db_connection.users_table.get_item.return_value = {'Item': mock_item}

        # Try to authenticate with wrong password
        result = await user_dao.authenticate_user('john_doe123', 'WrongPassword123!')

        # Should return None
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, user_dao):
        """Test authentication for non-existent user"""
        # Mock that user doesn't exist
        user_dao.get_user_by_username = AsyncMock(return_value=None)

        # Try to authenticate
        result = await user_dao.authenticate_user('nonexistent', 'password')

        # Should return None
        assert result is None

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_dao, mock_db_connection):
        """Test successful user update"""
        # Mock that email is not taken by another user
        user_dao.get_user_by_email = AsyncMock(return_value=None)

        # Mock database response
        updated_item = {
            'username': 'john_doe123',
            'email': 'newemail@example.com',
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '+9876543210',
            'created_at': '2023-01-01T00:00:00',
            'updated_at': '2023-01-02T00:00:00'
        }
        mock_db_connection.users_table.update_item.return_value = {'Attributes': updated_item}

        # Update user
        result = await user_dao.update_user(
            'john_doe123',
            email='newemail@example.com',
            first_name='Updated',
            last_name='Name',
            phone='+9876543210'
        )

        # Verify result
        assert isinstance(result, User)
        assert result.username == 'john_doe123'
        assert result.email == 'newemail@example.com'
        assert result.first_name == 'Updated'
        assert result.last_name == 'Name'
        assert result.phone == '+9876543210'

        # Verify database was called
        mock_db_connection.users_table.update_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_email_taken(self, user_dao):
        """Test update with email already taken by another user"""
        # Mock that email is taken by another user
        other_user = User(
            username='other_user',
            email='taken@example.com',
            first_name='Other',
            last_name='User',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        user_dao.get_user_by_email = AsyncMock(return_value=other_user)

        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            await user_dao.update_user('john_doe123', email='taken@example.com')

        assert "already in use by another user" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_no_changes(self, user_dao):
        """Test update with no changes returns current user"""
        # Mock get_user_by_username
        mock_user = User(
            username='john_doe123',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        user_dao.get_user_by_username = AsyncMock(return_value=mock_user)

        # Update with no changes
        result = await user_dao.update_user('john_doe123')

        # Should return current user
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_dao, mock_db_connection):
        """Test successful user deletion"""
        # Mock successful deletion
        mock_db_connection.users_table.delete_item.return_value = {'Attributes': {'user_id': 'john_doe123'}}

        # Delete user
        result = await user_dao.delete_user('john_doe123')

        # Should return True
        assert result is True

        # Verify database was called correctly
        mock_db_connection.users_table.delete_item.assert_called_once_with(
            Key={'user_id': 'john_doe123'},
            ReturnValues='ALL_OLD'
        )

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_dao, mock_db_connection):
        """Test deleting non-existent user"""
        # Mock no deletion (user not found)
        mock_db_connection.users_table.delete_item.return_value = {}

        # Delete user
        result = await user_dao.delete_user('nonexistent')

        # Should return False
        assert result is False