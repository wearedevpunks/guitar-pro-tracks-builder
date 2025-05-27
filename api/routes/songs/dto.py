from typing import Optional, Tuple
from pydantic import BaseModel, Field

from api.abstractions.storage import FileReference
from api.features.tabs.models import ParsedTabData


class SongCreateResponse(BaseModel):
    """Response model for song creation."""
    success: bool
    message: str
    song_id: Optional[str] = None
    tab_id: Optional[str] = None
    file_reference: Optional[FileReference] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Song created successfully",
                "song_id": "123e4567-e89b-12d3-a456-426614174000",
                "tab_id": "123e4567-e89b-12d3-a456-426614174000",
                "file_reference": {
                    "provider": "s3",
                    "reference": "songs/123e4567-e89b-12d3-a456-426614174000/master_of_puppets.gp5"
                }
            }
        }


class SongGetResponse(BaseModel):
    """Response model for getting a song by ID."""
    success: bool
    message: str
    song_id: Optional[str] = None
    tab_id: Optional[str] = None
    file_reference: Optional[FileReference] = None
    parsed_data: Optional[ParsedTabData] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Song retrieved successfully",
                "song_id": "123e4567-e89b-12d3-a456-426614174000",
                "tab_id": "123e4567-e89b-12d3-a456-426614174000",
                "file_reference": {
                    "provider": "s3",
                    "reference": "songs/123e4567-e89b-12d3-a456-426614174000/master_of_puppets.gp5"
                },
                "parsed_data": {
                    "song_info": {
                        "title": "Master of Puppets",
                        "artist": "Metallica",
                        "album": "Master of Puppets",
                        "tempo": 212
                    },
                    "tracks": [
                        {
                            "name": "Electric Guitar",
                            "index": 0,
                            "settings": {"name": "Electric Guitar", "volume": 8},
                            "instrument": "Electric Guitar",
                            "string_count": 6,
                            "tuning": [],
                            "measure_count": 32
                        }
                    ],
                    "measure_count": 32,
                    "has_lyrics": False,
                    "version": "5.2"
                }
            }
        }


class VideoExportRequest(BaseModel):
    """Request model for video export."""
    song_id: str = Field(..., description="ID of the song to export video for")
    output_format: str = Field("mp4", description="Output video format")
    resolution: Tuple[int, int] = Field((1920, 1080), description="Video resolution (width, height)")
    fps: int = Field(30, description="Frames per second", ge=15, le=60)
    duration_per_measure: Optional[float] = Field(None, description="Override duration per measure in seconds", gt=0)
    count_in_measures: int = Field(0, description="Number of count-in measures before the song starts", ge=0, le=8)
    use_dynamic_colors: bool = Field(False, description="Use random background colors that change every measure")
    
    class Config:
        json_schema_extra = {
            "example": {
                "song_id": "123e4567-e89b-12d3-a456-426614174000",
                "output_format": "mp4",
                "resolution": [1920, 1080],
                "fps": 30,
                "duration_per_measure": None,
                "count_in_measures": 2,
                "use_dynamic_colors": False
            }
        }


class VideoExportResponse(BaseModel):
    """Response model for video export."""
    success: bool = Field(..., description="Whether the export was successful")
    message: str = Field(..., description="Response message")
    song_id: Optional[str] = Field(None, description="ID of the exported song")
    video_file: Optional[FileReference] = Field(None, description="Reference to the exported video file")
    download_url: Optional[str] = Field(None, description="Download URL for the exported video file")
    duration_seconds: float = Field(0, description="Total video duration in seconds")
    total_measures: int = Field(0, description="Total number of measures in the video")
    export_settings: Optional[dict] = Field(None, description="Settings used for export")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Video exported successfully",
                "song_id": "123e4567-e89b-12d3-a456-426614174000",
                "video_file": {
                    "provider": "s3",
                    "reference": "videos/123e4567-e89b-12d3-a456-426614174000/master_of_puppets_metronome.mp4"
                },
                "download_url": "https://s3.amazonaws.com/bucket/videos/123e4567-e89b-12d3-a456-426614174000/master_of_puppets_metronome.mp4?AWSAccessKeyId=...",
                "duration_seconds": 240.5,
                "total_measures": 64,
                "export_settings": {
                    "resolution": [1920, 1080],
                    "fps": 30,
                    "tempo_bpm": 120,
                    "format": "mp4"
                }
            }
        }