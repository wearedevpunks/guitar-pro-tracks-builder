from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel

from api.db.redis.tabs_collection import Tab, TabsCollection
from api.infrastructure.logging import get_logger


class GetTabQuery(BaseModel):
    """Query to get a tab by ID."""
    
    tab_id: str


class GetTabResult(BaseModel):
    """Result of getting a tab."""
    
    tab: Optional[Tab] = None
    success: bool
    error: Optional[str] = None


class GetTabHandler(ABC):
    """Abstract handler for getting tabs."""
    
    @abstractmethod
    async def handle(self, query: GetTabQuery) -> GetTabResult:
        """Handle the get tab query."""
        pass


class GetTabHandlerImpl(GetTabHandler):
    """Implementation of get tab handler."""
    
    def __init__(self, tabs_collection: TabsCollection):
        """Initialize the handler with dependencies."""
        self.tabs_collection = tabs_collection
        self.logger = get_logger(__name__)
    
    async def handle(self, query: GetTabQuery) -> GetTabResult:
        """Handle the get tab query."""
        try:
            self.logger.debug(f"Getting tab with ID: {query.tab_id}")
            
            # Get the tab from collection
            tab = await self.tabs_collection.read(query.tab_id)
            
            if tab is None:
                error_msg = f"Tab with ID {query.tab_id} not found"
                self.logger.warning(error_msg)
                return GetTabResult(
                    tab=None,
                    success=False,
                    error=error_msg
                )
            
            self.logger.debug(f"Successfully retrieved tab: {query.tab_id}")
            return GetTabResult(
                tab=tab,
                success=True
            )
            
        except Exception as e:
            error_msg = f"Failed to get tab: {str(e)}"
            self.logger.exception(error_msg)
            return GetTabResult(
                tab=None,
                success=False,
                error=error_msg
            )