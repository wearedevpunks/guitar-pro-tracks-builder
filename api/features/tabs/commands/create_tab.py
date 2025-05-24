from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel

from api.collections.redis.tabs_collection import Tab, TabsCollection
from api.abstractions.storage import FileReference
from api.infrastructure.logging import get_logger


class CreateTabCommand(BaseModel):
    """Command to create a new tab."""
    
    file: FileReference
    tab_id: Optional[str] = None


class CreateTabResult(BaseModel):
    """Result of creating a tab."""
    
    tab_id: str
    success: bool
    error: Optional[str] = None


class CreateTabHandler(ABC):
    """Abstract handler for creating tabs."""
    
    @abstractmethod
    async def handle(self, command: CreateTabCommand) -> CreateTabResult:
        """Handle the create tab command."""
        pass


class CreateTabHandlerImpl(CreateTabHandler):
    """Implementation of create tab handler."""
    
    def __init__(self, tabs_collection: TabsCollection):
        """Initialize the handler with dependencies."""
        self.tabs_collection = tabs_collection
        self.logger = get_logger(__name__)
    
    async def handle(self, command: CreateTabCommand) -> CreateTabResult:
        """Handle the create tab command."""
        try:
            self.logger.debug(f"Creating tab with file reference: {command.file}")
            
            # Check if tab with same file reference already exists
            existing_tab = await self.tabs_collection.get_tab_by_file_reference(
                command.file.provider, 
                command.file.reference
            )
            
            if existing_tab:
                error_msg = f"Tab with file reference {command.file} already exists"
                self.logger.warning(error_msg)
                return CreateTabResult(
                    tab_id=existing_tab.id,
                    success=False,
                    error=error_msg
                )
            
            # Create the tab
            tab = Tab(
                id=command.tab_id or "",  # Will be generated if empty
                file=command.file
            )
            
            # Create in collection
            tab_id = await self.tabs_collection.create_with_timestamps(tab, command.tab_id)
            
            self.logger.info(f"Successfully created tab: {tab_id}")
            return CreateTabResult(
                tab_id=tab_id,
                success=True
            )
            
        except Exception as e:
            error_msg = f"Failed to create tab: {str(e)}"
            self.logger.exception(error_msg)
            return CreateTabResult(
                tab_id="",
                success=False,
                error=error_msg
            )