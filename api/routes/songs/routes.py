from fastapi import APIRouter, UploadFile, File, Depends

from api.services.storage import FileStorageService, get_storage_service
from api.features.tabs.service import TabsService, get_tabs_service
from .dto import CreateSongResponse, GetSongResponse
from .actions import create_new_song_action, get_song_by_id_action


router = APIRouter(prefix="/api/songs", tags=["songs"])


@router.post("/new", response_model=CreateSongResponse, operation_id="songCreate")
async def create_new_song(
    file: UploadFile = File(..., description="Guitar Pro file to upload"),
    storage_service: FileStorageService = Depends(get_storage_service),
    tabs_service: TabsService = Depends(get_tabs_service)
) -> CreateSongResponse:
    """
    Create a new song by uploading a Guitar Pro file.
    
    This endpoint accepts a Guitar Pro file, saves it using the configured storage service,
    and creates a new tab entry in the tabs collection.
    """
    return await create_new_song_action(file, storage_service, tabs_service)


@router.get("/{song_id}", response_model=GetSongResponse)
async def get_song_by_id(
    song_id: str,
    tabs_service: TabsService = Depends(get_tabs_service)
) -> GetSongResponse:
    """
    Get a song by its ID.
    
    This endpoint retrieves a song's tab information including the tab ID and file reference.
    """
    return await get_song_by_id_action(song_id, tabs_service)
