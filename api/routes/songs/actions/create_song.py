import uuid
from fastapi import UploadFile, HTTPException

from api.services.storage import FileStorageService
from api.features.tabs.service import TabsService
from api.infrastructure.logging import get_logger
from ..dto import CreateSongResponse


logger = get_logger(__name__)


async def create_new_song_action(
    file: UploadFile,
    storage_service: FileStorageService,
    tabs_service: TabsService
) -> CreateSongResponse:
    """
    Action to create a new song by uploading a Guitar Pro file.
    
    This action:
    1. Accepts a file upload (Guitar Pro format expected)
    2. Saves the file using the configured storage service
    3. Creates a new tab entry in the tabs collection
    
    Args:
        file: The uploaded Guitar Pro file
        storage_service: File storage service instance
        tabs_service: Tabs service instance
        
    Returns:
        CreateSongResponse with creation status and IDs
    """
    try:
        logger.info(f"Processing new song upload: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file extension (basic validation)
        allowed_extensions = {'.gp3', '.gp4', '.gp5', '.gpx', '.gtp'}
        file_extension = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            logger.warning(f"Invalid file extension: {file_extension} for file: {file.filename}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique identifier for the song
        song_id = str(uuid.uuid4())
        
        # Create file path with song ID
        file_path = f"songs/{song_id}/{file.filename}"
        
        # Save file using storage service
        logger.debug(f"Saving file to: {file_path}")
        file_reference = await storage_service.save_file(file_path, file.file)
        
        if not file_reference:
            logger.error(f"Failed to save file: {file.filename}")
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        logger.info(f"File saved successfully: {file_reference}")
        
        # Create tab entry
        logger.debug(f"Creating tab entry for song: {song_id}")
        create_tab_result = await tabs_service.create_tab(file=file_reference, tab_id=song_id)
        
        if not create_tab_result.success:
            logger.error(f"Failed to create tab entry: {create_tab_result.error}")
            # Try to clean up the uploaded file
            try:
                await storage_service.delete_file(file_reference)
                logger.info(f"Cleaned up uploaded file after tab creation failure: {file_reference}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup file after tab creation failure: {cleanup_error}")
            
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to create tab entry: {create_tab_result.error}"
            )
        
        logger.info(f"Successfully created song and tab - Song ID: {song_id}, Tab ID: {create_tab_result.tab_id}")
        
        return CreateSongResponse(
            success=True,
            message="Song created successfully",
            song_id=song_id,
            tab_id=create_tab_result.tab_id,
            file_reference=file_reference
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.exception(f"Unexpected error creating song: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")