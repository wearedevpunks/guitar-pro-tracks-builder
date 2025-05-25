from typing import List, Optional, Dict, Any, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    pass


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
    volume: int = Field(64, description="Track volume (0-127)", ge=0, le=127)
    pan: int = Field(64, description="Track pan (0-127)", ge=0, le=127)
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
                "volume": 64,
                "pan": 64,
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


class SerializableNote(BaseModel):
    """Serializable note data."""
    
    string: int = Field(..., description="String number (1-based)")
    fret: int = Field(..., description="Fret number")
    value: int = Field(..., description="MIDI note value")
    velocity: int = Field(95, description="Note velocity (0-127)", ge=0, le=127)
    tied: bool = Field(False, description="Is note tied")
    muted: bool = Field(False, description="Is note muted")
    ghost: bool = Field(False, description="Is ghost note")
    accent: bool = Field(False, description="Has accent")
    heavy_accent: bool = Field(False, description="Has heavy accent")
    harmonic: bool = Field(False, description="Is harmonic")
    palm_mute: bool = Field(False, description="Has palm mute")
    staccato: bool = Field(False, description="Is staccato")
    let_ring: bool = Field(False, description="Let ring")
    
    # Additional effects
    bend_value: Optional[float] = Field(None, description="Bend value in semitones")
    slide_type: Optional[str] = Field(None, description="Slide type")
    vibrato: bool = Field(False, description="Has vibrato")
    
    # Legato techniques
    hammer_on: bool = Field(False, description="Is hammer-on")
    pull_off: bool = Field(False, description="Is pull-off")
    
    # Advanced techniques
    trill: bool = Field(False, description="Has trill")
    tremolo_picking: bool = Field(False, description="Has tremolo picking")
    grace_note: bool = Field(False, description="Is grace note")
    grace_note_type: Optional[str] = Field(None, description="Grace note type (before/on beat)")
    
    # Fingering
    left_hand_finger: Optional[int] = Field(None, description="Left hand finger (1-4)", ge=1, le=4)
    right_hand_finger: Optional[str] = Field(None, description="Right hand finger (p,i,m,a,c)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "string": 1,
                "fret": 12,
                "value": 64,
                "velocity": 95,
                "tied": False,
                "muted": False,
                "ghost": False,
                "accent": False,
                "heavy_accent": False,
                "harmonic": False,
                "palm_mute": False,
                "staccato": False,
                "let_ring": False,
                "bend_value": None,
                "slide_type": None,
                "vibrato": False,
                "hammer_on": False,
                "pull_off": False,
                "trill": False,
                "tremolo_picking": False,
                "grace_note": False,
                "grace_note_type": None,
                "left_hand_finger": None,
                "right_hand_finger": None
            }
        }


class SerializableVoice(BaseModel):
    """Serializable voice data."""
    
    notes: List[SerializableNote] = Field(default_factory=list, description="Notes in this voice")
    duration: str = Field("quarter", description="Note duration (whole, half, quarter, eighth, sixteenth, etc.)")
    tuplet: Optional[Dict[str, int]] = Field(None, description="Tuplet information (enters, times)")
    is_rest: bool = Field(False, description="Is this voice a rest")
    
    class Config:
        json_schema_extra = {
            "example": {
                "notes": [
                    {
                        "string": 1,
                        "fret": 12,
                        "value": 64,
                        "velocity": 95
                    }
                ],
                "duration": "quarter",
                "tuplet": None,
                "is_rest": False
            }
        }


class SerializableBeat(BaseModel):
    """Serializable beat data."""
    
    voices: List[SerializableVoice] = Field(default_factory=list, description="Voices in this beat")
    start_time: int = Field(0, description="Start time in ticks")
    duration: str = Field("quarter", description="Beat duration")
    
    # Beat text/annotations
    text: str = Field("", description="Beat text or chord annotation")
    
    # Beat effects
    fade_in: bool = Field(False, description="Has fade in")
    fade_out: bool = Field(False, description="Has fade out")
    volume_swell: bool = Field(False, description="Has volume swell")
    tremolo_picking: bool = Field(False, description="Has tremolo picking")
    
    # Stroke effects
    stroke_direction: Optional[str] = Field(None, description="Stroke direction (up/down)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "voices": [
                    {
                        "notes": [{"string": 1, "fret": 12, "value": 64}],
                        "duration": "quarter",
                        "is_rest": False
                    }
                ],
                "start_time": 0,
                "duration": "quarter",
                "text": "",
                "fade_in": False,
                "fade_out": False,
                "volume_swell": False,
                "tremolo_picking": False,
                "stroke_direction": None
            }
        }


class SerializableTimeSignature(BaseModel):
    """Serializable time signature."""
    
    numerator: int = Field(4, description="Time signature numerator")
    denominator: int = Field(4, description="Time signature denominator")
    
    class Config:
        json_schema_extra = {
            "example": {
                "numerator": 4,
                "denominator": 4
            }
        }


class SerializableKeySignature(BaseModel):
    """Serializable key signature."""
    
    key: int = Field(0, description="Key signature (-7 to +7)")
    is_minor: bool = Field(False, description="Is minor key")
    
    class Config:
        json_schema_extra = {
            "example": {
                "key": 0,  # C major / A minor
                "is_minor": False
            }
        }


class SerializableMarker(BaseModel):
    """Serializable marker data."""
    
    title: str = Field("", description="Marker title")
    color: Optional[str] = Field(None, description="Marker color (hex)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Chorus",
                "color": "#FF0000"
            }
        }


class SerializableMeasure(BaseModel):
    """Serializable measure data."""
    
    number: int = Field(1, description="Measure number (1-based)")
    beats: List[SerializableBeat] = Field(default_factory=list, description="Beats in this measure")
    
    # Measure properties
    time_signature: Optional[SerializableTimeSignature] = Field(None, description="Time signature (if changed)")
    key_signature: Optional[SerializableKeySignature] = Field(None, description="Key signature (if changed)")
    marker: Optional[SerializableMarker] = Field(None, description="Marker at this measure")
    
    # Tempo changes (if any at this measure)
    tempo_change: Optional[int] = Field(None, description="Tempo change in BPM (if changed at this measure)", ge=30, le=300)
    
    # Repeat properties
    repeat_open: bool = Field(False, description="Is repeat open")
    repeat_close: int = Field(0, description="Repeat close count (0 = no repeat)")
    repeat_alternative: int = Field(0, description="Alternative ending number (0 = no alternative)")
    
    # Additional properties
    double_bar: bool = Field(False, description="Has double bar line")
    
    class Config:
        json_schema_extra = {
            "example": {
                "number": 1,
                "beats": [
                    {
                        "voices": [
                            {
                                "notes": [{"string": 1, "fret": 0, "value": 40}],
                                "duration": "quarter"
                            }
                        ],
                        "start_time": 0,
                        "duration": "quarter"
                    }
                ],
                "time_signature": {"numerator": 4, "denominator": 4},
                "key_signature": {"key": 0, "is_minor": False},
                "marker": None,
                "tempo_change": None,
                "repeat_open": False,
                "repeat_close": 0,
                "repeat_alternative": 0,
                "double_bar": False
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
    
    # Measures data
    measures: List[SerializableMeasure] = Field(default_factory=list, description="Measures in this track")
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
    hide_tempo: bool = Field(False, description="Hide tempo from display")
    
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
                "tempo_name": "Fast Rock",
                "hide_tempo": False
            }
        }


class SerializableMeasureInfo(BaseModel):
    """Song-level measure information with section names and repetitions."""
    
    number: int = Field(..., description="Measure number (1-based)")
    section_name: str = Field("", description="Section name from first track beat text")
    
    # Tempo and time signature information
    tempo_bpm: Optional[int] = Field(None, description="Current tempo BPM at this measure")
    time_signature: Optional[SerializableTimeSignature] = Field(None, description="Current time signature at this measure")
    
    # Repetition information
    repeat_open: bool = Field(False, description="Has repeat start marker")
    repeat_close: int = Field(0, description="Repeat end count (0 = no repeat end)")
    repeat_alternative: int = Field(0, description="Alternative ending number (0 = no alternative)")
    double_bar: bool = Field(False, description="Has double bar line")
    
    class Config:
        json_schema_extra = {
            "example": {
                "number": 1,
                "section_name": "Intro",
                "tempo_bpm": 120,
                "time_signature": {
                    "numerator": 4,
                    "denominator": 4
                },
                "repeat_open": False,
                "repeat_close": 0,
                "repeat_alternative": 0,
                "double_bar": False
            }
        }


class ParsedTabData(BaseModel):
    """Complete parsed tab data ready for frontend editing."""
    
    song_info: SerializableSongInfo = Field(..., description="Song metadata")
    tracks: List[SerializableTrack] = Field(..., description="List of tracks")
    measure_count: int = Field(0, description="Total number of measures")
    measures: List[SerializableMeasureInfo] = Field(default_factory=list, description="Song-level measure information with section names")
    
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
                        "settings": {"name": "Electric Guitar", "volume": 64},
                        "instrument": "Electric Guitar",
                        "string_count": 6,
                        "tuning": [],
                        "measure_count": 32
                    }
                ],
                "measure_count": 32,
                "measures": [
                    {"number": 1, "section_name": "Intro"},
                    {"number": 5, "section_name": "Verse 1"},
                    {"number": 13, "section_name": "Chorus"},
                    {"number": 21, "section_name": "Verse 2"}
                ],
                "has_lyrics": False,
                "version": "5.2"
            }
        }
