"""Video export action for songs."""

from api.features.tabs.service import TabsService
from api.infrastructure.logging import get_logger
from ..dto import VideoExportRequest, VideoExportResponse


async def export_song_video_action(
    request: VideoExportRequest,
    tabs_service: TabsService
) -> VideoExportResponse:
    """Export a metronome video for a song.
    
    Args:
        request: Video export request containing song_id and export settings
        tabs_service: Tabs service for retrieving song data and exporting video
        
    Returns:
        VideoExportResponse with video file reference or error message
    """
    logger = get_logger(__name__)
    
    try:
        logger.info(f"Starting video export for song: {request.song_id}")
        
        # First, get the song data
        song_result = await tabs_service.get_tab(request.song_id)
        
        if not song_result.success:
            logger.warning(f"Failed to retrieve song {request.song_id}: {song_result.error}")
            return VideoExportResponse(
                success=False,
                message=f"Failed to retrieve song: {song_result.error}",
                song_id=request.song_id
            )
        
        # Check if we have parsed data
        if not song_result.tab or not song_result.tab.file:
            logger.warning(f"No file reference found for song: {request.song_id}")
            return VideoExportResponse(
                success=False,
                message="Song file not found",
                song_id=request.song_id
            )
        
        # Parse the tab file to get structured data
        logger.info(f"Parsing tab file for song: {request.song_id}")
        parse_result = await tabs_service.parse_tab(song_result.tab.file)
        
        if not parse_result.success:
            logger.warning(f"Failed to parse tab for song {request.song_id}: {parse_result.error}")
            return VideoExportResponse(
                success=False,
                message=f"Failed to parse song file: {parse_result.error}",
                song_id=request.song_id
            )
        
        # Export video with the provided settings
        logger.info(f"Exporting video for song: {request.song_id}")
        
        # Extract filename from file reference
        import os
        filename = os.path.basename(song_result.tab.file.reference) if song_result.tab.file else None
        
        export_kwargs = {
            "output_format": request.output_format,
            "resolution": request.resolution,
            "fps": request.fps,
            "count_in_measures": request.count_in_measures,
            "filename": filename,
            "use_dynamic_colors": request.use_dynamic_colors
        }
        
        if request.duration_per_measure:
            export_kwargs["duration_per_measure"] = request.duration_per_measure
        
        video_result = await tabs_service.export_video(
            request.song_id,
            parse_result.parsed_data, 
            **export_kwargs
        )
        
        if not video_result.success:
            error_msg = video_result.error_message or "Unknown error during video export"
            logger.exception(f"Video export failed for song {request.song_id}: {error_msg}")
            return VideoExportResponse(
                success=False,
                message=f"Video export failed: {error_msg}",
                song_id=request.song_id
            )
        
        # Create export settings summary
        export_settings = {
            "resolution": list(request.resolution),
            "fps": request.fps,
            "tempo_bpm": parse_result.parsed_data.song_info.tempo,
            "format": request.output_format,
            "song_title": parse_result.parsed_data.song_info.title,
            "total_measures": parse_result.parsed_data.measure_count,
            "count_in_measures": request.count_in_measures,
            "use_dynamic_colors": request.use_dynamic_colors
        }
        
        if request.duration_per_measure:
            export_settings["duration_per_measure"] = request.duration_per_measure
        
        logger.info(f"Video export completed successfully for song: {request.song_id}")
        
        return VideoExportResponse(
            success=True,
            message="Video exported successfully",
            song_id=request.song_id,
            video_file=video_result.video_file,
            duration_seconds=video_result.duration_seconds,
            total_measures=video_result.total_measures,
            export_settings=export_settings
        )
        
    except Exception as e:
        logger.exception(f"Unexpected error during video export for song {request.song_id}: {str(e)}")
        return VideoExportResponse(
            success=False,
            message=f"Internal server error: {str(e)}",
            song_id=request.song_id
        )