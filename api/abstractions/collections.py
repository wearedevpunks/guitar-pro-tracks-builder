from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, TypeVar, Generic
from datetime import datetime

# Generic type for collection items
T = TypeVar('T')


class CollectionBase(ABC, Generic[T]):
    """Abstract base class for collection storage providers implementing CRUD operations."""
    
    @abstractmethod
    async def create(self, item: T, item_id: Optional[str] = None) -> str:
        """Create a new item in the collection.
        
        Args:
            item: The item to create
            item_id: Optional custom ID for the item. If None, an ID will be generated.
            
        Returns:
            The ID of the created item
            
        Raises:
            ValueError: If item_id already exists or item is invalid
        """
        pass
    
    @abstractmethod
    async def read(self, item_id: str) -> Optional[T]:
        """Read an item from the collection by ID.
        
        Args:
            item_id: The ID of the item to retrieve
            
        Returns:
            The item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self, item_id: str, item: T) -> bool:
        """Update an existing item in the collection.
        
        Args:
            item_id: The ID of the item to update
            item: The updated item data
            
        Returns:
            True if the item was updated, False if not found
        """
        pass
    
    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """Delete an item from the collection.
        
        Args:
            item_id: The ID of the item to delete
            
        Returns:
            True if the item was deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def list(self, offset: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """List items from the collection with pagination and filtering.
        
        Args:
            offset: Number of items to skip (for pagination)
            limit: Maximum number of items to return
            filters: Optional dictionary of field filters
            
        Returns:
            List of items matching the criteria
        """
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count the number of items in the collection.
        
        Args:
            filters: Optional dictionary of field filters
            
        Returns:
            Number of items matching the criteria
        """
        pass
    
    @abstractmethod
    async def exists(self, item_id: str) -> bool:
        """Check if an item exists in the collection.
        
        Args:
            item_id: The ID of the item to check
            
        Returns:
            True if the item exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all items from the collection.
        
        Returns:
            True if successful, False otherwise
            
        Warning:
            This operation is destructive and cannot be undone
        """
        pass
    
    # Optional methods with default implementations
    
    async def upsert(self, item_id: str, item: T) -> str:
        """Insert or update an item in the collection.
        
        Args:
            item_id: The ID of the item
            item: The item data
            
        Returns:
            The ID of the item (same as input)
        """
        if await self.exists(item_id):
            await self.update(item_id, item)
        else:
            await self.create(item, item_id)
        return item_id
    
    async def batch_create(self, items: List[T], item_ids: Optional[List[str]] = None) -> List[str]:
        """Create multiple items in the collection.
        
        Args:
            items: List of items to create
            item_ids: Optional list of custom IDs. Must match items length if provided.
            
        Returns:
            List of created item IDs
            
        Raises:
            ValueError: If item_ids length doesn't match items length
        """
        if item_ids is not None and len(item_ids) != len(items):
            raise ValueError("item_ids length must match items length")
        
        created_ids = []
        for i, item in enumerate(items):
            item_id = item_ids[i] if item_ids else None
            created_id = await self.create(item, item_id)
            created_ids.append(created_id)
        
        return created_ids
    
    async def batch_read(self, item_ids: List[str]) -> Dict[str, Optional[T]]:
        """Read multiple items from the collection.
        
        Args:
            item_ids: List of item IDs to retrieve
            
        Returns:
            Dictionary mapping item IDs to items (None if not found)
        """
        results = {}
        for item_id in item_ids:
            results[item_id] = await self.read(item_id)
        return results
    
    async def batch_delete(self, item_ids: List[str]) -> Dict[str, bool]:
        """Delete multiple items from the collection.
        
        Args:
            item_ids: List of item IDs to delete
            
        Returns:
            Dictionary mapping item IDs to deletion success status
        """
        results = {}
        for item_id in item_ids:
            results[item_id] = await self.delete(item_id)
        return results
    
    async def search(self, query: str, fields: Optional[List[str]] = None, limit: int = 100) -> List[T]:
        """Search for items in the collection.
        
        Note: Default implementation uses list() with no filtering.
        Implementations should override this for proper search functionality.
        
        Args:
            query: Search query string
            fields: Optional list of fields to search in
            limit: Maximum number of results to return
            
        Returns:
            List of items matching the search criteria
        """
        # Default implementation - should be overridden by concrete classes
        # Parameters intentionally unused in default implementation
        _ = query
        _ = fields
        return await self.list(limit=limit)


class TimestampedCollectionBase(CollectionBase[T]):
    """Extended collection base class with timestamp tracking."""
    
    @abstractmethod
    async def create_with_timestamps(self, item: T, item_id: Optional[str] = None) -> tuple[str, datetime]:
        """Create an item with automatic timestamp tracking.
        
        Args:
            item: The item to create
            item_id: Optional custom ID for the item
            
        Returns:
            Tuple of (item_id, created_timestamp)
        """
        pass
    
    @abstractmethod
    async def update_with_timestamps(self, item_id: str, item: T) -> Optional[datetime]:
        """Update an item with automatic timestamp tracking.
        
        Args:
            item_id: The ID of the item to update
            item: The updated item data
            
        Returns:
            Updated timestamp if successful, None if item not found
        """
        pass
    
    @abstractmethod
    async def get_timestamps(self, item_id: str) -> Optional[Dict[str, datetime]]:
        """Get timestamp information for an item.
        
        Args:
            item_id: The ID of the item
            
        Returns:
            Dictionary with 'created' and 'updated' timestamps, None if item not found
        """
        pass
    
    async def list_by_created_date(self, 
                                   start_date: Optional[datetime] = None, 
                                   end_date: Optional[datetime] = None,
                                   limit: int = 100) -> List[T]:
        """List items filtered by creation date.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of items to return
            
        Returns:
            List of items created within the date range
        """
        # Default implementation - should be overridden for efficiency
        filters = {}
        if start_date:
            filters['created_after'] = start_date
        if end_date:
            filters['created_before'] = end_date
        
        return await self.list(limit=limit, filters=filters)
    
    async def list_by_updated_date(self, 
                                   start_date: Optional[datetime] = None, 
                                   end_date: Optional[datetime] = None,
                                   limit: int = 100) -> List[T]:
        """List items filtered by update date.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of items to return
            
        Returns:
            List of items updated within the date range
        """
        # Default implementation - should be overridden for efficiency
        filters = {}
        if start_date:
            filters['updated_after'] = start_date
        if end_date:
            filters['updated_before'] = end_date
        
        return await self.list(limit=limit, filters=filters)