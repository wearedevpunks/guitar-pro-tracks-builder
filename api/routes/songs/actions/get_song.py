from fastapi import HTTPException

from api.features.tabs.service import TabsService
from api.infrastructure.logging import get_logger
from ..dto import GetSongResponse


logger = get_logger(__name__)


async def get_song_by_id_action(
    song_id: str,
    tabs_service: TabsService
) -> GetSongResponse:
    """
    Action to get a song by its ID.
    
    This action retrieves a song's tab information including the tab ID and file reference.
    
    Args:
        song_id: The unique identifier of the song
        tabs_service: Tabs service instance
        
    Returns:
        GetSongResponse with song details or error
    """
    try:
        logger.info(f"Getting song by ID: {song_id}")
        
        # Get the tab using the song ID (which should be the same as tab ID)
        get_tab_result = await tabs_service.get_tab(song_id)
        
        if not get_tab_result.success:
            logger.warning(f"Song not found: {song_id}")
            raise HTTPException(
                status_code=404, 
                detail=f"Song with ID {song_id} not found"
            )
        
        tab = get_tab_result.tab
        if not tab:
            logger.error(f"Tab result success but no tab data for ID: {song_id}")
            raise HTTPException(status_code=500, detail="Internal server error")
        
        logger.info(f"Successfully retrieved song: {song_id}")
        
        return GetSongResponse(
            success=True,
            message="Song retrieved successfully",
            song_id=song_id,
            tab_id=tab.id,
            file_reference=tab.file
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.exception(f"Unexpected error getting song {song_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")