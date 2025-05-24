from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from .base import RedisCollectionBase
from api.abstractions.storage import FileReference
from api.infrastructure.logging import get_logger


class Tab(BaseModel):
    """Tab model for Guitar Pro tabs."""
    
    id: str = Field(..., description="Tab unique identifier")
    file: FileReference = Field(..., description="Reference to the tab file")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "file": {
                    "provider": "s3",
                    "reference": "tabs/master_of_puppets.gp5"
                }
            }
        }


class TabsCollection(RedisCollectionBase[Tab]):
    """Tabs collection with specialized methods for Guitar Pro tabs."""
    
    def __init__(self, redis_client=None):
        """Initialize the tabs collection."""
        super().__init__(
            collection_name="tabs",
            model_class=Tab,
            redis_client=redis_client
        )
        self.logger = get_logger(__name__)
    
    async def get_tab_by_file_reference(self, provider: str, reference: str) -> Optional[Tab]:
        """Get a tab by file reference."""
        self.logger.debug(f"Searching tab by file reference: {provider}://{reference}")
        
        # Get all tabs and filter by file reference
        all_tabs = await self.list(limit=1000)
        
        for tab in all_tabs:
            if tab.file.provider == provider and tab.file.reference == reference:
                self.logger.debug(f"Found tab with matching file reference: {tab.id}")
                return tab
        
        self.logger.debug("No tab found with matching file reference")
        return None
    
    async def get_tabs_by_provider(self, provider: str, limit: int = 100) -> List[Tab]:
        """Get all tabs from a specific storage provider."""
        self.logger.debug(f"Getting tabs from provider: {provider}")
        
        all_tabs = await self.list(limit=1000)
        
        matching_tabs = [
            tab for tab in all_tabs 
            if tab.file.provider == provider
        ][:limit]
        
        self.logger.debug(f"Found {len(matching_tabs)} tabs from provider: {provider}")
        return matching_tabs
    
    async def search_by_reference_pattern(self, pattern: str, limit: int = 100) -> List[Tab]:
        """Search tabs by reference pattern (case-insensitive)."""
        self.logger.debug(f"Searching tabs by reference pattern: {pattern}")
        
        all_tabs = await self.list(limit=1000)
        
        matching_tabs = [
            tab for tab in all_tabs 
            if pattern.lower() in tab.file.reference.lower()
        ][:limit]
        
        self.logger.debug(f"Found {len(matching_tabs)} tabs matching pattern: {pattern}")
        return matching_tabs
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get collection statistics."""
        self.logger.debug("Getting tabs collection statistics")
        
        total_tabs = await self.count()
        all_tabs = await self.list(limit=10000)
        
        providers = {}
        
        for tab in all_tabs:
            provider = tab.file.provider
            providers[provider] = providers.get(provider, 0) + 1
        
        stats = {
            "total_tabs": total_tabs,
            "provider_distribution": dict(sorted(providers.items(), key=lambda x: x[1], reverse=True))
        }
        
        self.logger.debug("Generated tabs collection statistics")
        return stats


# Global tabs collection instance
_tabs_collection: Optional[TabsCollection] = None


def get_tabs_collection() -> TabsCollection:
    """Get the global tabs collection instance."""
    global _tabs_collection
    
    if _tabs_collection is None:
        _tabs_collection = TabsCollection()
    
    return _tabs_collection


def reset_tabs_collection() -> None:
    """Reset the global tabs collection instance (useful for testing)."""
    global _tabs_collection
    if _tabs_collection:
        # Note: In a real scenario, you might want to close the Redis connection
        pass
    _tabs_collection = None