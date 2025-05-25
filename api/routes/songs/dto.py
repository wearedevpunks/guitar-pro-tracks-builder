from typing import Optional
from pydantic import BaseModel

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