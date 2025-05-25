from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SerializableTrackSettings(BaseModel):
    """Serializable track settings for frontend editing."""
    
    name: str = Field(..., description="Track name")
    color: Optional[str] = Field(None, description="Track color (hex)")
    is_12_stringed: bool = Field(False, description="Is 12-stringed guitar")
    is_acoustic: bool = Field(False, description="Is acoustic guitar")
    is_bass: bool = Field(False, description="Is bass guitar") 
    is_drums: bool = Field(False, description="Is drum track")
    is_muted: bool = Field(False, description="Is track muted")
    is_solo: bool = Field(False, description="Is track solo")
    is_visible: bool = Field(True, description="Is track visible")
    volume: int = Field(8, description="Track volume (0-15)", ge=0, le=15)
    pan: int = Field(8, description="Track pan (0-15)", ge=0, le=15)
    channel: int = Field(1, description="MIDI channel", ge=1, le=16)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Electric Guitar",
                "color": "#FF0000",
                "is_12_stringed": False,
                "is_acoustic": False,
                "is_bass": False,
                "is_drums": False,
                "is_muted": False,
                "is_solo": False,
                "is_visible": True,
                "volume": 8,
                "pan": 8,
                "channel": 1
            }
        }


class SerializableStringTuning(BaseModel):
    """Serializable guitar string tuning."""
    
    string_number: int = Field(..., description="String number (1-8)")
    value: int = Field(..., description="MIDI note value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "string_number": 1,
                "value": 64  # E4
            }
        }


class SerializableTrack(BaseModel):
    """Serializable track data for frontend editing."""
    
    # Basic track info
    name: str = Field(..., description="Track name")
    index: int = Field(..., description="Track index in song")
    
    # Settings
    settings: SerializableTrackSettings = Field(..., description="Track settings")
    
    # Instrument info
    instrument: str = Field("", description="Instrument name")
    string_count: int = Field(6, description="Number of strings", ge=1, le=8)
    tuning: List[SerializableStringTuning] = Field(default_factory=list, description="String tuning")
    
    # Additional metadata that might be useful for editing
    measure_count: int = Field(0, description="Number of measures in track")
    
    # Raw data for reconstruction (if needed)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Electric Guitar",
                "index": 0,
                "settings": {
                    "name": "Electric Guitar",
                    "color": "#FF0000",
                    "is_12_stringed": False,
                    "is_acoustic": False,
                    "is_bass": False,
                    "is_drums": False,
                    "is_muted": False,
                    "is_solo": False,
                    "is_visible": True,
                    "volume": 8,
                    "pan": 8,
                    "channel": 1
                },
                "instrument": "Electric Guitar",
                "string_count": 6,
                "tuning": [
                    {"string_number": 1, "value": 64},
                    {"string_number": 2, "value": 59},
                    {"string_number": 3, "value": 55},
                    {"string_number": 4, "value": 50},
                    {"string_number": 5, "value": 45},
                    {"string_number": 6, "value": 40}
                ],
                "measure_count": 32,
                "metadata": {}
            }
        }


class SerializableSongInfo(BaseModel):
    """Serializable song metadata."""
    
    title: str = Field("", description="Song title")
    subtitle: str = Field("", description="Song subtitle")
    artist: str = Field("", description="Artist name")
    album: str = Field("", description="Album name")
    music: str = Field("", description="Music composer")
    words: str = Field("", description="Lyrics author")
    copyright: str = Field("", description="Copyright notice")
    tab: str = Field("", description="Tab author")
    instructions: str = Field("", description="Performance instructions")
    notice: str = Field("", description="Notice text")
    tempo: int = Field(120, description="Tempo in BPM", ge=30, le=300)
    tempo_name: str = Field("", description="Tempo marking name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Master of Puppets",
                "subtitle": "",
                "artist": "Metallica",
                "album": "Master of Puppets",
                "music": "James Hetfield, Lars Ulrich",
                "words": "James Hetfield",
                "copyright": "1986 Metallica",
                "tab": "Tab transcribed by User",
                "instructions": "Tune down 1/2 step",
                "notice": "",
                "tempo": 212,
                "tempo_name": "Fast Rock"
            }
        }


class ParsedTabData(BaseModel):
    """Complete parsed tab data ready for frontend editing."""
    
    song_info: SerializableSongInfo = Field(..., description="Song metadata")
    tracks: List[SerializableTrack] = Field(..., description="List of tracks")
    measure_count: int = Field(0, description="Total number of measures")
    
    # Additional useful info
    has_lyrics: bool = Field(False, description="Song contains lyrics")
    version: str = Field("", description="Guitar Pro version")
    
    class Config:
        json_schema_extra = {
            "example": {
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