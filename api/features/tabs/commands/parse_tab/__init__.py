from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel, Field
import io
import guitarpro

from api.abstractions.storage import FileReference
from api.services.storage import FileStorageService
from api.infrastructure.logging import get_logger
from ...models import (
    ParsedTabData,
    SerializableSongInfo,
    SerializableTrack,
    SerializableTrackSettings,
    SerializableStringTuning
)

logger = get_logger(__name__)


class ParseTabCommand(BaseModel):
    """Command to parse a Guitar Pro tab file."""

    file_reference: FileReference = Field(..., description="Reference to the tab file")


class ParseTabResult(BaseModel):
    """Result of parsing a tab file."""

    success: bool
    parsed_data: Optional[ParsedTabData] = None
    error: Optional[str] = None


class ParseTabHandler(ABC):
    """Abstract handler for parsing tab files."""

    @abstractmethod
    async def handle(self, command: ParseTabCommand) -> ParseTabResult:
        """Handle the parse tab command."""
        pass


class ParseTabHandlerImpl(ParseTabHandler):
    """Implementation of parse tab handler."""

    def __init__(self, storage_service: FileStorageService):
        """Initialize the handler with dependencies."""
        self.storage_service = storage_service
        self.logger = get_logger(__name__)

    async def handle(self, command: ParseTabCommand) -> ParseTabResult:
        """Handle the parse tab command."""
        try:
            self.logger.debug(f"Parsing tab file: {command.file_reference}")

            # Get file data from storage
            file_data = await self.storage_service.get_file(command.file_reference)
            if not file_data:
                error_msg = f"File not found: {command.file_reference}"
                self.logger.error(error_msg)
                return ParseTabResult(
                    success=False,
                    error=error_msg
                )

            # Parse with PyGuitarPro
            song = guitarpro.parse(io.BytesIO(file_data))

            # Convert to serializable format
            parsed_data = self._convert_song_to_serializable(song)

            self.logger.info(f"Successfully parsed tab file: {command.file_reference}")
            return ParseTabResult(
                success=True,
                parsed_data=parsed_data
            )

        except Exception as e:
            error_msg = f"Failed to parse tab file: {str(e)}"
            self.logger.exception(error_msg)
            return ParseTabResult(
                success=False,
                error=error_msg
            )

    def _convert_song_to_serializable(self, song: guitarpro.Song) -> ParsedTabData:
        """Convert PyGuitarPro Song to serializable format."""

        # Helper function to safely convert to string
        def safe_str(value, default=''):
            if isinstance(value, str):
                return value
            elif isinstance(value, list):
                return '\n'.join(str(item) for item in value) if value else default
            elif value is None:
                return default
            else:
                return str(value)

        # Extract song info with safe string conversion
        song_info = SerializableSongInfo(
            title=safe_str(getattr(song, 'title', '')),
            subtitle=safe_str(getattr(song, 'subtitle', '')),
            artist=safe_str(getattr(song, 'artist', '')),
            album=safe_str(getattr(song, 'album', '')),
            music=safe_str(getattr(song, 'music', '')),
            words=safe_str(getattr(song, 'words', '')),
            copyright=safe_str(getattr(song, 'copyright', '')),
            tab=safe_str(getattr(song, 'tab', '')),
            instructions=safe_str(getattr(song, 'instructions', '')),
            notice=safe_str(getattr(song, 'notice', '')),
            tempo=getattr(song, 'tempo', 120),
            tempo_name=safe_str(getattr(song, 'tempoName', ''))
        )

        # Extract tracks
        tracks = []
        for i, track in enumerate(song.tracks):
            serializable_track = self._convert_track_to_serializable(track, i)
            tracks.append(serializable_track)

        # Get measure count
        measure_count = len(getattr(song, 'measureHeaders', []))

        # Check for lyrics
        has_lyrics = bool(getattr(song, 'lyrics', None) and
                          getattr(song.lyrics, 'lines', []))

        # Get version info
        version = getattr(song, 'versionTuple', (5, 2, 0))
        version_str = f"{version[0]}.{version[1]}" if version else "Unknown"

        return ParsedTabData(
            song_info=song_info,
            tracks=tracks,
            measure_count=measure_count,
            has_lyrics=has_lyrics,
            version=version_str
        )

    def _convert_track_to_serializable(self, track: guitarpro.Track, index: int) -> SerializableTrack:
        """Convert PyGuitarPro Track to serializable format."""

        # Get track name
        name = getattr(track, 'name', f'Track {index + 1}')

        # Helper function to safely get integer values within range
        def safe_int(value, default, min_val, max_val):
            if value is None:
                return default
            try:
                int_val = int(value)
                return max(min_val, min(max_val, int_val))
            except (ValueError, TypeError):
                return default

        # Get track settings
        channel = getattr(track, 'channel', None)
        settings = SerializableTrackSettings(
            name=name,
            color=self._get_track_color(track),
            is_12_stringed=getattr(track, 'is12StringedGuitarTrack', False),
            is_acoustic=getattr(track, 'isAcousticTrack', False),
            is_bass=getattr(track, 'isBassTrack', False),
            is_drums=getattr(track, 'isPercussionTrack', False),
            is_muted=getattr(track, 'isMute', False),
            is_solo=getattr(track, 'isSolo', False),
            is_visible=getattr(track, 'isVisible', True),
            volume=safe_int(getattr(channel, 'volume', None) if channel else None, 64, 0, 127),
            pan=safe_int(getattr(channel, 'balance', None) if channel else None, 64, 0, 127),
            channel=safe_int(getattr(channel, 'channel1', None) if channel else None, 1, 1, 16)
        )

        # Get instrument info
        instrument = getattr(track, 'name', '')

        # Get string info
        strings = getattr(track, 'strings', [])
        string_count = len(strings) if strings else 6

        # Convert string tuning
        tuning = []
        for i, string in enumerate(strings):
            tuning.append(SerializableStringTuning(
                string_number=i + 1,
                value=getattr(string, 'value', 40 + i * 5)  # Default tuning
            ))

        # Get measure count for this track
        measures = getattr(track, 'measures', [])
        measure_count = len(measures)

        # Additional metadata
        metadata = {
            'channel_info': {
                'channel1': getattr(channel, 'channel1', 1) if channel else 1,
                'channel2': getattr(channel, 'channel2', 2) if channel else 2,
                'effectChannel1': getattr(channel, 'effectChannel1', 1) if channel else 1,
                'effectChannel2': getattr(channel, 'effectChannel2', 2) if channel else 2,
            } if channel else {},
            'port': getattr(track, 'port', 1),
            'nstrings': getattr(track, 'nstrings', string_count)
        }

        return SerializableTrack(
            name=name,
            index=index,
            settings=settings,
            instrument=instrument,
            string_count=string_count,
            tuning=tuning,
            measure_count=measure_count,
            metadata=metadata
        )

    def _get_track_color(self, track: guitarpro.Track) -> Optional[str]:
        """Extract track color as hex string."""
        color = getattr(track, 'color', None)
        if not color:
            return None

        # Convert Color object to hex if it has RGB values
        if hasattr(color, 'r') and hasattr(color, 'g') and hasattr(color, 'b'):
            r = getattr(color, 'r', 0)
            g = getattr(color, 'g', 0)
            b = getattr(color, 'b', 0)
            return f"#{r:02x}{g:02x}{b:02x}"

        return None