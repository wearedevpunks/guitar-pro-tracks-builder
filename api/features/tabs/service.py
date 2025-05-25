from typing import Optional

from api.db.redis.tabs_collection import TabsCollection, get_tabs_collection
from api.abstractions.storage import FileReference
from api.services.storage import FileStorageService, get_storage_service
from api.infrastructure.logging import get_logger

from .commands.create_tab import CreateTabHandler, CreateTabHandlerImpl, CreateTabCommand, CreateTabResult
from .commands.parse_tab import ParseTabHandler, ParseTabHandlerImpl, ParseTabCommand, ParseTabResult
from .queries.get_tab import GetTabHandler, GetTabHandlerImpl, GetTabQuery, GetTabResult


class TabsService:
    """Service for managing tabs using CQRS pattern with dependency injection."""
    
    def __init__(
        self,
        create_tab_handler: Optional[CreateTabHandler] = None,
        get_tab_handler: Optional[GetTabHandler] = None,
        parse_tab_handler: Optional[ParseTabHandler] = None,
        tabs_collection: Optional[TabsCollection] = None,
        storage_service: Optional[FileStorageService] = None
    ):
        """Initialize the service with dependency injection.
        
        Args:
            create_tab_handler: Handler for create tab commands
            get_tab_handler: Handler for get tab queries
            parse_tab_handler: Handler for parse tab commands
            tabs_collection: Tabs collection instance
            storage_service: File storage service instance
        """
        self.logger = get_logger(__name__)
        
        # Use dependency injection with fallback to default implementations
        self._tabs_collection = tabs_collection or get_tabs_collection()
        self._storage_service = storage_service or get_storage_service()
        self._create_tab_handler = create_tab_handler or CreateTabHandlerImpl(self._tabs_collection)
        self._get_tab_handler = get_tab_handler or GetTabHandlerImpl(self._tabs_collection)
        self._parse_tab_handler = parse_tab_handler or ParseTabHandlerImpl(self._storage_service)
        
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
    
    async def parse_tab(self, file_reference: FileReference) -> ParseTabResult:
        """Parse a tab file and extract serializable data.
        
        Args:
            file_reference: Reference to the tab file to parse
            
        Returns:
            ParseTabResult with parsed data or error
        """
        self.logger.debug(f"Parsing tab file: {file_reference}")
        
        command = ParseTabCommand(file_reference=file_reference)
        result = await self._parse_tab_handler.handle(command)
        
        if result.success:
            self.logger.debug(f"Tab parsed successfully: {file_reference}")
        else:
            self.logger.warning(f"Tab parsing failed: {result.error}")
        
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