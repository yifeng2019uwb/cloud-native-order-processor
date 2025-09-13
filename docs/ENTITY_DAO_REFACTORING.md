# Entity-DAO Refactoring Pattern

## Overview

This document outlines the standardized pattern for refactoring entities and DAOs in the cloud-native order processor system. The pattern ensures clean separation between domain models and database representations while maintaining type safety and consistency.

## Core Principles

### 1. Entity-EntityItem Pattern
- **Entity**: Pure domain model with business logic, no database concerns
- **EntityItem**: Database representation with PK/SK fields and database-specific methods
- **No Response/Create Models**: Eliminate separate API response and creation models

### 2. Service Layer Flow
```
Service → Entity → EntityItem → Database
Database → EntityItem → Entity → Service
```

## Entity Structure

### Domain Entity (e.g., `User`)
```python
class User(BaseModel):
    """User entity - pure domain model (no PK/SK)"""
    username: str = Field(..., max_length=30)
    email: str = Field(..., max_length=255)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    phone: Optional[str] = Field(None, max_length=15)
    date_of_birth: Optional[date] = None
    marketing_emails_consent: bool = False
    role: str = Field(default=DEFAULT_USER_ROLE, max_length=20)
    password: str = Field(..., max_length=128)

    created_at: datetime = Field(description="User creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    def mark_updated(self):
        """Mark entity as updated (sets updated_at to current time)"""
        self.updated_at = datetime.now(timezone.utc)
```

### Database EntityItem (e.g., `UserItem`)
```python
class UserItem(BaseModel):
    """User database item with PK/SK for database operations"""
    Pk: str = Field(..., description="Primary key (username)")
    Sk: str = Field(..., description="Sort key (USER)")
    username: str = Field(..., max_length=30)
    email: str = Field(..., max_length=255)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    phone: Optional[str] = Field(None, max_length=15)
    date_of_birth: Optional[date] = None
    marketing_emails_consent: bool = False
    role: str = Field(default=DEFAULT_USER_ROLE, max_length=20)
    password: str = Field(..., max_length=128)

    created_at: datetime = Field(description="User creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

    def get_key(self) -> dict:
        """Get database key for this user item"""
        return {
            DatabaseFields.PK: self.Pk,
            DatabaseFields.SK: self.Sk
        }

    @staticmethod
    def get_key_for_username(username: str) -> dict:
        """Get database key for a username (static method)"""
        return {
            DatabaseFields.PK: username,
            DatabaseFields.SK: UserFields.SK_VALUE
        }

    @classmethod
    def from_entity(cls, entity: User) -> 'UserItem':
        """Create EntityItem from Entity domain model"""
        return cls(
            Pk=entity.username,  # EntityItem knows username is the PK
            Sk=UserFields.SK_VALUE,
            username=entity.username,
            email=entity.email,
            first_name=entity.first_name,
            last_name=entity.last_name,
            phone=entity.phone,
            date_of_birth=entity.date_of_birth,
            marketing_emails_consent=entity.marketing_emails_consent,
            role=entity.role,
            password=entity.password,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    def to_entity(self) -> User:
        """Convert EntityItem to Entity domain model"""
        return User(
            username=self.username,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            phone=self.phone,
            date_of_birth=self.date_of_birth,
            marketing_emails_consent=self.marketing_emails_consent,
            role=self.role,
            password=self.password,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
```

## DAO Pattern

### Standard DAO Methods
```python
class EntityDAO(BaseDAO):
    """Data Access Object for entity operations"""

    def create_entity(self, entity: Entity) -> Entity:
        """Create a new entity"""
        # Convert to EntityItem
        entity_item = EntityItem.from_entity(entity)

        # Apply any business logic (e.g., password hashing)
        self._apply_business_logic(entity_item)

        # Save to database
        created_item = self._safe_put_item(self.table, entity_item)

        # Return Entity
        return created_item.to_entity()

    def get_entity(self, pk_value: str) -> Entity:
        """Get entity by primary key"""
        key = EntityItem.get_key_for_pk(pk_value)
        item_dict = self._safe_get_item(self.table, key)

        if not item_dict:
            raise EntityNotFoundException(f"Entity with pk '{pk_value}' not found")

        entity_item = EntityItem(**item_dict)
        return entity_item.to_entity()

    def update_entity(self, entity: Entity) -> Entity:
        """Update existing entity"""
        # Convert to EntityItem
        entity_item = EntityItem.from_entity(entity)
        entity_item.mark_updated()

        # Update in database
        updated_item = self._safe_put_item(self.table, entity_item)

        # Return Entity
        return updated_item.to_entity()

    def delete_entity(self, pk_value: str) -> bool:
        """Delete entity by primary key"""
        key = EntityItem.get_key_for_pk(pk_value)
        self._safe_delete_item(self.table, key)
        return True
```

## Key Methods Required

### Entity Methods
```python
def mark_updated(self):
    """Mark entity as updated (sets updated_at to current time)"""
    self.updated_at = datetime.now(timezone.utc)
```

### EntityItem Methods
```python
def get_key(self) -> dict:
    """Get database key for this entity item"""
    return {
        DatabaseFields.PK: self.Pk,
        DatabaseFields.SK: self.Sk
    }

@staticmethod
def get_key_for_pk(pk_value: str) -> dict:
    """Get database key for a primary key value (static method)"""
    return {
        DatabaseFields.PK: pk_value,
        DatabaseFields.SK: UserFields.SK_VALUE
    }

@classmethod
def from_entity(cls, entity: Entity) -> 'EntityItem':
    """Create EntityItem from Entity domain model"""

def to_entity(self) -> Entity:
    """Convert EntityItem to Entity domain model"""
```

## Service Layer Integration

### Controller Pattern
```python
@router.post("/create", response_model=EntityResponse)
def create_entity(
    entity_data: EntityRequest,
    entity_dao = Depends(get_entity_dao)
) -> EntityResponse:
    """Create new entity"""
    # Convert request to Entity
    entity = Entity(**entity_data.dict())

    # Create via DAO
    created_entity = entity_dao.create_entity(entity)

    # Return response (no separate response model needed)
    return EntityResponse(
        success=True,
        message="Entity created successfully",
        data=created_entity
    )
```

## Benefits

### 1. Clean Separation
- Domain logic stays in Entity
- Database concerns in EntityItem
- No mixing of concerns

### 2. Type Safety
- Strong typing throughout the flow
- Compile-time error detection
- IDE support and autocomplete

### 3. Consistency
- Standardized pattern across all entities
- Predictable method names and behavior
- Easy to understand and maintain

### 4. Testability
- Entities can be tested independently
- DAOs can be mocked easily
- Clear boundaries for unit tests

### 5. Flexibility
- Easy to change database schema (EntityItem)
- Domain model remains stable (Entity)
- Can add database-specific optimizations

## Migration Strategy

### Phase 1: Create New Pattern
1. Create Entity and EntityItem classes
2. Implement required methods (get_key, from_entity, to_entity)
3. Update DAO to use new pattern

### Phase 2: Update Services
1. Update controllers to use Entity instead of response models
2. Remove old response/request models
3. Update service layer to work with Entity

### Phase 3: Cleanup
1. Remove unused models
2. Update tests
3. Update documentation

## Example Implementation

### User Entity Refactoring
```python
# Before: Multiple models
class UserCreateRequest(BaseModel): ...
class UserResponse(BaseModel): ...
class UserUpdateRequest(BaseModel): ...

# After: Single Entity + EntityItem
class User(BaseModel): ...
class UserItem(BaseModel): ...
```

### DAO Refactoring
```python
# Before: Complex conversion logic
def create_user(self, user_data: dict) -> dict:
    # Complex conversion logic
    pass

# After: Clean Entity flow
def create_user(self, user: User) -> User:
    user_item = UserItem.from_user(user, user.username)
    # Save and return
    return created_item.to_user()
```

## Constants and Fields

### Entity Fields
```python
class EntityFields:
    SK_VALUE = "ENTITY"  # Sort key value for this entity type
    PK_PREFIX = "ENTITY#"  # Primary key prefix if needed
```

### Database Fields
```python
class DatabaseFields:
    PK = "Pk"  # Primary key field name
    SK = "Sk"  # Sort key field name
    GSI1_PK = "GSI1PK"  # Global Secondary Index 1 PK
    GSI1_SK = "GSI1SK"  # Global Secondary Index 1 SK
```

## Best Practices

### 1. Naming Conventions
- Entity: `User`, `Order`, `Asset`
- EntityItem: `UserItem`, `OrderItem`, `AssetItem`
- DAO: `UserDAO`, `OrderDAO`, `AssetDAO`

### 2. Method Naming
- `get_key()`: Get database key for this item
- `get_key_for_pk()`: Get database key for primary key value
- `from_entity()`: Create EntityItem from Entity
- `to_entity()`: Convert EntityItem to Entity

### 3. Error Handling
- Use specific exceptions for each entity type
- Provide meaningful error messages
- Handle database errors gracefully

### 4. Validation
- Validate at Entity level for business rules
- Validate at EntityItem level for database constraints
- Use Pydantic validators for field validation

This pattern provides a clean, maintainable, and scalable approach to entity management in the cloud-native order processor system.
