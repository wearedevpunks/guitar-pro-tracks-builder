import uuid
from typing import Optional, List, Dict, Any, TypeVar, Type
from datetime import datetime
import redis.asyncio as redis
from pydantic import BaseModel, ValidationError

from api.abstractions.collections import TimestampedCollectionBase
from api.settings.app_settings import settings
from api.infrastructure.logging import get_logger

T = TypeVar('T', bound=BaseModel)


class RedisCollectionBase(TimestampedCollectionBase[T]):
    """Redis implementation of CollectionBase for Pydantic models."""
    
    def __init__(self, 
                 collection_name: str, 
                 model_class: Type[T],
                 redis_client: Optional[redis.Redis] = None,
                 key_prefix: Optional[str] = None):
        """Initialize the Redis collection.
        
        Args:
            collection_name: Name of the collection (used as Redis key prefix)
            model_class: Pydantic model class for type safety and serialization
            redis_client: Optional Redis client. If None, creates from settings.
            key_prefix: Optional custom key prefix. Defaults to collection_name.
        """
        self.collection_name = collection_name
        self.model_class = model_class
        self.key_prefix = key_prefix or collection_name
        self.logger = get_logger(__name__)
        
        # Initialize Redis client
        self._redis = redis_client or self._create_redis_client()
        
        # Redis key patterns
        self._item_key_pattern = f"{self.key_prefix}:item:{{item_id}}"
        self._timestamp_key_pattern = f"{self.key_prefix}:timestamps:{{item_id}}"
        self._index_key = f"{self.key_prefix}:index"
        self._counter_key = f"{self.key_prefix}:counter"
        
        self.logger.info(f"Initialized RedisCollectionBase for {collection_name} with model {model_class.__name__}")
    
    def _create_redis_client(self) -> redis.Redis:
        """Create a Redis client from settings."""
        return redis.from_url(
            settings.redis_url,
            db=settings.redis_db,
            decode_responses=True
        )
    
    def _get_item_key(self, item_id: str) -> str:
        """Get the Redis key for an item."""
        return self._item_key_pattern.format(item_id=item_id)
    
    def _get_timestamp_key(self, item_id: str) -> str:
        """Get the Redis key for item timestamps."""
        return self._timestamp_key_pattern.format(item_id=item_id)
    
    def _generate_id(self) -> str:
        """Generate a unique ID for new items."""
        return str(uuid.uuid4())
    
    async def _serialize_item(self, item: T) -> str:
        """Serialize a Pydantic model to JSON string."""
        return item.model_dump_json()
    
    async def _deserialize_item(self, data: str) -> T:
        """Deserialize JSON string to Pydantic model."""
        try:
            return self.model_class.model_validate_json(data)
        except ValidationError as e:
            self.logger.error(f"Failed to deserialize item: {e}")
            raise ValueError(f"Invalid data format for {self.model_class.__name__}") from e
    
    async def create(self, item: T, item_id: Optional[str] = None) -> str:
        """Create a new item in the collection."""
        if item_id is None:
            item_id = self._generate_id()
        
        self.logger.debug(f"Creating item with ID: {item_id}")
        
        item_key = self._get_item_key(item_id)
        
        # Check if item already exists
        if await self._redis.exists(item_key):
            self.logger.error(f"Item with ID {item_id} already exists")
            raise ValueError(f"Item with ID {item_id} already exists")
        
        # Serialize and store item
        serialized_item = await self._serialize_item(item)
        
        async with self._redis.pipeline() as pipe:
            # Store the item
            pipe.set(item_key, serialized_item)
            # Add to index
            pipe.sadd(self._index_key, item_id)
            # Increment counter
            pipe.incr(self._counter_key)
            
            await pipe.execute()
        
        self.logger.info(f"Successfully created item: {item_id}")
        return item_id
    
    async def read(self, item_id: str) -> Optional[T]:
        """Read an item from the collection by ID."""
        self.logger.debug(f"Reading item: {item_id}")
        
        item_key = self._get_item_key(item_id)
        data = await self._redis.get(item_key)
        
        if data is None:
            self.logger.debug(f"Item not found: {item_id}")
            return None
        
        try:
            item = await self._deserialize_item(data)
            self.logger.debug(f"Successfully read item: {item_id}")
            return item
        except ValueError as e:
            self.logger.error(f"Failed to deserialize item {item_id}: {e}")
            return None
    
    async def update(self, item_id: str, item: T) -> bool:
        """Update an existing item in the collection."""
        self.logger.debug(f"Updating item: {item_id}")
        
        item_key = self._get_item_key(item_id)
        
        # Check if item exists
        if not await self._redis.exists(item_key):
            self.logger.warning(f"Item not found for update: {item_id}")
            return False
        
        # Serialize and update item
        serialized_item = await self._serialize_item(item)
        await self._redis.set(item_key, serialized_item)
        
        self.logger.info(f"Successfully updated item: {item_id}")
        return True
    
    async def delete(self, item_id: str) -> bool:
        """Delete an item from the collection."""
        self.logger.debug(f"Deleting item: {item_id}")
        
        item_key = self._get_item_key(item_id)
        timestamp_key = self._get_timestamp_key(item_id)
        
        async with self._redis.pipeline() as pipe:
            # Delete the item
            pipe.delete(item_key)
            # Delete timestamps
            pipe.delete(timestamp_key)
            # Remove from index
            pipe.srem(self._index_key, item_id)
            # Decrement counter
            pipe.decr(self._counter_key)
            
            results = await pipe.execute()
        
        deleted = results[0] > 0  # Number of keys deleted
        
        if deleted:
            self.logger.info(f"Successfully deleted item: {item_id}")
        else:
            self.logger.warning(f"Item not found for deletion: {item_id}")
        
        return deleted
    
    async def list(self, offset: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """List items from the collection with pagination."""
        self.logger.debug(f"Listing items with offset={offset}, limit={limit}")
        
        # Get all item IDs from the index
        all_item_ids = await self._redis.smembers(self._index_key)
        
        # Apply pagination
        item_ids = list(all_item_ids)[offset:offset + limit]
        
        if not item_ids:
            return []
        
        # Batch read items
        items = []
        for item_id in item_ids:
            item = await self.read(item_id)
            if item is not None:
                # Apply filters if provided
                if filters is None or self._matches_filters(item, filters):
                    items.append(item)
        
        self.logger.debug(f"Found {len(items)} items")
        return items
    
    def _matches_filters(self, item: T, filters: Dict[str, Any]) -> bool:
        """Check if an item matches the given filters."""
        for field, value in filters.items():
            if hasattr(item, field):
                item_value = getattr(item, field)
                if item_value != value:
                    return False
            else:
                return False
        return True
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count the number of items in the collection."""
        if filters is None:
            # Use the counter for efficiency
            count = await self._redis.get(self._counter_key)
            return int(count) if count else 0
        
        # For filtered count, we need to check each item
        items = await self.list(limit=10000, filters=filters)  # Large limit for counting
        return len(items)
    
    async def exists(self, item_id: str) -> bool:
        """Check if an item exists in the collection."""
        item_key = self._get_item_key(item_id)
        exists = await self._redis.exists(item_key)
        self.logger.debug(f"Item {'exists' if exists else 'does not exist'}: {item_id}")
        return bool(exists)
    
    async def clear(self) -> bool:
        """Clear all items from the collection."""
        self.logger.warning(f"Clearing all items from collection: {self.collection_name}")
        
        try:
            # Get all item IDs
            all_item_ids = await self._redis.smembers(self._index_key)
            
            if all_item_ids:
                # Build list of all keys to delete
                keys_to_delete = []
                for item_id in all_item_ids:
                    keys_to_delete.append(self._get_item_key(item_id))
                    keys_to_delete.append(self._get_timestamp_key(item_id))
                
                # Add index and counter keys
                keys_to_delete.extend([self._index_key, self._counter_key])
                
                # Delete all keys
                await self._redis.delete(*keys_to_delete)
            else:
                # Just delete index and counter
                await self._redis.delete(self._index_key, self._counter_key)
            
            self.logger.info(f"Successfully cleared collection: {self.collection_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to clear collection: {e}")
            return False
    
    # Timestamp-related methods
    
    async def create_with_timestamps(self, item: T, item_id: Optional[str] = None) -> tuple[str, datetime]:
        """Create an item with automatic timestamp tracking."""
        created_id = await self.create(item, item_id)
        
        # Add timestamps
        now = datetime.utcnow()
        timestamp_key = self._get_timestamp_key(created_id)
        
        timestamps = {
            'created': now.isoformat(),
            'updated': now.isoformat()
        }
        
        await self._redis.hset(timestamp_key, mapping=timestamps)
        
        return created_id, now
    
    async def update_with_timestamps(self, item_id: str, item: T) -> Optional[datetime]:
        """Update an item with automatic timestamp tracking."""
        success = await self.update(item_id, item)
        
        if not success:
            return None
        
        # Update timestamp
        now = datetime.utcnow()
        timestamp_key = self._get_timestamp_key(item_id)
        
        await self._redis.hset(timestamp_key, 'updated', now.isoformat())
        
        return now
    
    async def get_timestamps(self, item_id: str) -> Optional[Dict[str, datetime]]:
        """Get timestamp information for an item."""
        if not await self.exists(item_id):
            return None
        
        timestamp_key = self._get_timestamp_key(item_id)
        timestamps_raw = await self._redis.hgetall(timestamp_key)
        
        if not timestamps_raw:
            return None
        
        try:
            timestamps = {}
            for key, value in timestamps_raw.items():
                timestamps[key] = datetime.fromisoformat(value)
            return timestamps
        except ValueError as e:
            self.logger.error(f"Invalid timestamp format for item {item_id}: {e}")
            return None
    
    async def search(self, query: str, fields: Optional[List[str]] = None, limit: int = 100) -> List[T]:
        """Search for items in the collection.
        
        Note: This is a basic implementation that searches in serialized JSON.
        For better performance, consider using Redis Search or external search engines.
        """
        self.logger.debug(f"Searching for query: {query}")
        
        # Get all items and search in their serialized form
        all_item_ids = await self._redis.smembers(self._index_key)
        matching_items = []
        
        for item_id in all_item_ids:
            if len(matching_items) >= limit:
                break
                
            item_key = self._get_item_key(item_id)
            data = await self._redis.get(item_key)
            
            if data and query.lower() in data.lower():
                try:
                    item = await self._deserialize_item(data)
                    matching_items.append(item)
                except ValueError:
                    continue
        
        self.logger.debug(f"Found {len(matching_items)} matching items")
        return matching_items
    
    async def close(self):
        """Close the Redis connection."""
        await self._redis.close()
        self.logger.info(f"Closed Redis connection for collection: {self.collection_name}")