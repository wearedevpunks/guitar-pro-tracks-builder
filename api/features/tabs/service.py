from typing import Optional

from api.collections.redis.tabs_collection import TabsCollection, get_tabs_collection
from api.abstractions.storage import FileReference
from api.infrastructure.logging import get_logger

from .commands.create_tab import CreateTabHandler, CreateTabHandlerImpl, CreateTabCommand, CreateTabResult
from .queries.get_tab import GetTabHandler, GetTabHandlerImpl, GetTabQuery, GetTabResult


class TabsService:
    """Service for managing tabs using CQRS pattern with dependency injection."""
    
    def __init__(
        self,
        create_tab_handler: Optional[CreateTabHandler] = None,
        get_tab_handler: Optional[GetTabHandler] = None,
        tabs_collection: Optional[TabsCollection] = None
    ):
        """Initialize the service with dependency injection.
        
        Args:
            create_tab_handler: Handler for create tab commands
            get_tab_handler: Handler for get tab queries
            tabs_collection: Tabs collection instance
        """
        self.logger = get_logger(__name__)
        
        # Use dependency injection with fallback to default implementations
        self._tabs_collection = tabs_collection or get_tabs_collection()
        self._create_tab_handler = create_tab_handler or CreateTabHandlerImpl(self._tabs_collection)
        self._get_tab_handler = get_tab_handler or GetTabHandlerImpl(self._tabs_collection)
        
        self.logger.info("TabsService initialized with dependency injection")
    
    async def create_tab(self, file: FileReference, tab_id: Optional[str] = None) -> CreateTabResult:
        """Create a new tab.
        
        Args:
            file: File reference for the tab
            tab_id: Optional custom tab ID
            
        Returns:
            CreateTabResult with creation status and tab ID
        """
        self.logger.debug(f"Creating tab with file: {file}")
        
        command = CreateTabCommand(file=file, tab_id=tab_id)
        result = await self._create_tab_handler.handle(command)
        
        if result.success:
            self.logger.info(f"Tab created successfully: {result.tab_id}")
        else:
            self.logger.warning(f"Tab creation failed: {result.error}")
        
        return result
    
    async def get_tab(self, tab_id: str) -> GetTabResult:
        """Get a tab by ID.
        
        Args:
            tab_id: The tab ID to retrieve
            
        Returns:
            GetTabResult with tab data or error
        """
        self.logger.debug(f"Getting tab: {tab_id}")
        
        query = GetTabQuery(tab_id=tab_id)
        result = await self._get_tab_handler.handle(query)
        
        if result.success:
            self.logger.debug(f"Tab retrieved successfully: {tab_id}")
        else:
            self.logger.warning(f"Tab retrieval failed: {result.error}")
        
        return result


# Global service instance for convenience
_tabs_service: Optional[TabsService] = None


def get_tabs_service() -> TabsService:
    """Get the global tabs service instance."""
    global _tabs_service
    
    if _tabs_service is None:
        _tabs_service = TabsService()
    
    return _tabs_service


def reset_tabs_service() -> None:
    """Reset the global tabs service instance (useful for testing)."""
    global _tabs_service
    _tabs_service = None