from fastapi import APIRouter, UploadFile, File, Depends

from api.services.storage import FileStorageService, get_storage_service
from api.features.tabs.service import TabsService, get_tabs_service
from .dto import SongCreateResponse, SongGetResponse, VideoExportRequest, VideoExportResponse
from .actions import create_new_song_action, get_song_by_id_action, export_song_video_action


router = APIRouter(prefix="/api/songs", tags=["songs"])


@router.post("/new", operation_id="songCreate", response_model=SongCreateResponse)
async def create_new_song(
    file: UploadFile = File(..., description="Guitar Pro file to upload"),
    storage_service: FileStorageService = Depends(get_storage_service),
    tabs_service: TabsService = Depends(get_tabs_service)
) -> SongCreateResponse:
    """
    Create a new song by uploading a Guitar Pro file.
    
    This endpoint accepts a Guitar Pro file, saves it using the configured storage service,
    and creates a new tab entry in the tabs collection.
    """
    return await create_new_song_action(file, storage_service, tabs_service)


@router.get("/{song_id}", operation_id="songGet", response_model=SongGetResponse)
async def get_song_by_id(
    song_id: str,
    tabs_service: TabsService = Depends(get_tabs_service)
) -> SongGetResponse:
    """
    Get a song by its ID.
    
    This endpoint retrieves a song's tab information including the tab ID and file reference.
    """
    return await get_song_by_id_action(song_id, tabs_service)


@router.post("/export-video", operation_id="songExportVideo", response_model=VideoExportResponse)
async def export_song_video(
    request: VideoExportRequest,
    tabs_service: TabsService = Depends(get_tabs_service)
) -> VideoExportResponse:
    """
    Export a metronome video for a song.
    
    This endpoint takes a song ID and export settings, retrieves the song's tab data,
    and generates a metronome video with visual timing cues for band practice.
    
    The video includes:
    - Large measure counter
    - Current section names (Intro, Verse, Chorus, etc.)
    - Beat indicators with emphasis on beat 1
    - Quarter note counter
    - Visual metronome pendulum
    - Audio metronome with different sounds for beat 1
    """
    return await export_song_video_action(request, tabs_service)
