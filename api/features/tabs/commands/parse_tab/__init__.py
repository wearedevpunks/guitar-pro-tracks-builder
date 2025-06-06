from abc import ABC, abstractmethod
from typing import Optional, Dict, List
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
    SerializableStringTuning,
    SerializableMeasure,
    SerializableBeat,
    SerializableVoice,
    SerializableNote,
    SerializableTimeSignature,
    SerializableKeySignature,
    SerializableMarker
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
            tempo_name=safe_str(getattr(song, 'tempoName', '')),
            hide_tempo=getattr(song, 'hideTempo', False)
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

        # Extract song-level measures with section names from first track
        measures = self._extract_song_measures(song, tracks)

        return ParsedTabData(
            song_info=song_info,
            tracks=tracks,
            measure_count=measure_count,
            measures=measures,
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

        # Parse measures for this track
        track_measures = getattr(track, 'measures', [])
        measure_count = len(track_measures)
        song_measure_headers = getattr(track.song, 'measureHeaders', [])
        
        # Convert measures to serializable format
        serializable_measures = []
        for i, measure in enumerate(track_measures):
            serializable_measure = self._convert_measure_to_serializable(
                measure, i + 1, song_measure_headers[i] if i < len(song_measure_headers) else None
            )
            serializable_measures.append(serializable_measure)

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
            measures=serializable_measures,
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
    
    def _convert_measure_to_serializable(self, measure, measure_number: int, header=None) -> SerializableMeasure:
        """Convert PyGuitarPro Measure to serializable format."""
        
        # Parse beats/voices in this measure
        beats = []
        voices = getattr(measure, 'voices', [])
        
        for voice in voices:
            voice_beats = getattr(voice, 'beats', [])
            for beat in voice_beats:
                serializable_beat = self._convert_beat_to_serializable(beat, voice)
                beats.append(serializable_beat)
        
        # Helper function to safely extract integer from time signature components
        def safe_time_sig_int(value, default=4):
            if value is None:
                return default
            if isinstance(value, int):
                return value
            # Handle Duration objects or other complex types
            if hasattr(value, 'value'):
                return getattr(value, 'value', default)
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # Get time signature (from header or measure)
        time_sig = None
        if header and hasattr(header, 'timeSignature'):
            ts = header.timeSignature
            time_sig = SerializableTimeSignature(
                numerator=safe_time_sig_int(getattr(ts, 'numerator', 4)),
                denominator=safe_time_sig_int(getattr(ts, 'denominator', 4))
            )
        elif hasattr(measure, 'timeSignature') and measure.timeSignature:
            ts = measure.timeSignature
            time_sig = SerializableTimeSignature(
                numerator=safe_time_sig_int(getattr(ts, 'numerator', 4)),
                denominator=safe_time_sig_int(getattr(ts, 'denominator', 4))
            )
        
        # Helper function to safely extract integer from key signature
        def safe_key_int(value, default=0):
            if value is None:
                return default
            if isinstance(value, int):
                return value
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # Get key signature
        key_sig = None
        if hasattr(measure, 'keySignature') and measure.keySignature:
            ks = measure.keySignature
            key_sig = SerializableKeySignature(
                key=safe_key_int(getattr(ks, 'key', 0)),
                is_minor=bool(getattr(ks, 'isMinor', False))
            )
        
        # Get marker
        marker = None
        if hasattr(measure, 'marker') and measure.marker:
            m = measure.marker
            marker = SerializableMarker(
                title=getattr(m, 'title', ''),
                color=self._convert_marker_color(m)
            )
        
        # Check for tempo changes (future extension - not currently in pyguitarpro)
        tempo_change = None
        # Note: pyguitarpro doesn't currently expose per-measure tempo changes
        # This field is added for future compatibility if the library is extended
        
        # Additional measure effects (double bar from header)
        double_bar = getattr(header, 'hasDoubleBar', False) if header else False
        
        # Extract repetition information (prioritize header over measure)
        repeat_open = getattr(header, 'isRepeatOpen', False) if header else getattr(measure, 'isRepeatOpen', False)
        repeat_close = getattr(header, 'repeatClose', 0) if header else getattr(measure, 'repeatClose', 0)
        repeat_alternative = getattr(header, 'repeatAlternative', 0) if header else 0
        
        # Handle repeat close value (-1 means no repeat in guitarpro)
        if repeat_close == -1:
            repeat_close = 0
        
        return SerializableMeasure(
            number=measure_number,
            beats=beats,
            time_signature=time_sig,
            key_signature=key_sig,
            marker=marker,
            tempo_change=tempo_change,
            repeat_open=repeat_open,
            repeat_close=repeat_close,
            repeat_alternative=repeat_alternative,
            double_bar=double_bar
        )
    
    def _convert_beat_to_serializable(self, beat, voice=None) -> SerializableBeat:
        """Convert PyGuitarPro Beat to serializable format."""
        
        # Parse notes in this beat
        notes = getattr(beat, 'notes', [])
        serializable_notes = []
        
        for note in notes:
            if hasattr(note, 'string') and hasattr(note, 'value'):
                serializable_note = self._convert_note_to_serializable(note)
                serializable_notes.append(serializable_note)
        
        # Get tuplet information using improved extraction
        tuplet = self._get_tuplet_info(beat, voice)
        
        # Create voice for these notes
        serializable_voice = SerializableVoice(
            notes=serializable_notes,
            duration=self._get_duration_string(beat),
            tuplet=tuplet,
            is_rest=len(serializable_notes) == 0
        )
        
        # Get beat effects
        effect = getattr(beat, 'effect', None)
        
        # Get stroke direction if available  
        stroke_direction = None
        stroke = getattr(effect, 'stroke', None) if effect else None
        if stroke:
            direction = getattr(stroke, 'direction', None)
            if direction:
                # Convert stroke direction enum to string
                stroke_direction = str(direction).lower() if hasattr(direction, 'name') else str(direction).lower()
        
        # Extract beat text (could be from text, chord, or other annotations)
        beat_text = self._get_beat_text(beat, effect)
        
        return SerializableBeat(
            voices=[serializable_voice],
            start_time=getattr(beat, 'start', 0),
            duration=self._get_duration_string(beat),
            text=beat_text,
            fade_in=getattr(effect, 'fadeIn', False) if effect else False,
            fade_out=getattr(effect, 'fadeOut', False) if effect else False,
            volume_swell=getattr(effect, 'volumeSwell', False) if effect else False,
            tremolo_picking=getattr(effect, 'tremoloPicking', False) if effect else False,
            stroke_direction=stroke_direction
        )
    
    def _convert_note_to_serializable(self, note) -> SerializableNote:
        """Convert PyGuitarPro Note to serializable format."""
        
        # Helper function to safely extract integer values
        def safe_note_int(value, default, min_val=None, max_val=None):
            if value is None:
                return default
            try:
                int_val = int(value)
                if min_val is not None:
                    int_val = max(min_val, int_val)
                if max_val is not None:
                    int_val = min(max_val, int_val)
                return int_val
            except (ValueError, TypeError):
                return default
        
        # Get note effects
        effect = getattr(note, 'effect', None)
        
        return SerializableNote(
            string=safe_note_int(getattr(note, 'string', 1), 1, 1, 8),
            fret=safe_note_int(getattr(note, 'value', 0), 0, 0, 24),
            value=safe_note_int(getattr(note, 'realValue', 40), 40, 0, 127),  # MIDI value
            velocity=safe_note_int(getattr(note, 'velocity', 95), 95, 0, 127),
            tied=bool(getattr(note, 'isTiedNote', False)),
            muted=getattr(note, 'type', None) == 'muted' if hasattr(note, 'type') else False,
            ghost=getattr(note, 'type', None) == 'ghost' if hasattr(note, 'type') else False,
            accent=bool(getattr(effect, 'accentuatedNote', False)) if effect else False,
            heavy_accent=bool(getattr(effect, 'heavyAccentuatedNote', False)) if effect else False,
            harmonic=getattr(effect, 'harmonic', None) is not None if effect else False,
            palm_mute=bool(getattr(effect, 'palmMute', False)) if effect else False,
            staccato=bool(getattr(effect, 'staccato', False)) if effect else False,
            let_ring=bool(getattr(effect, 'letRing', False)) if effect else False,
            bend_value=self._get_bend_value(effect) if effect else None,
            slide_type=self._get_slide_type(effect) if effect else None,
            vibrato=bool(getattr(effect, 'vibrato', False)) if effect else False,
            
            # Legato techniques
            hammer_on=self._is_hammer_on(effect) if effect else False,
            pull_off=self._is_pull_off(effect) if effect else False,
            
            # Advanced techniques  
            trill=bool(getattr(effect, 'trill', False)) if effect else False,
            tremolo_picking=bool(getattr(effect, 'tremoloPicking', False)) if effect else False,
            grace_note=bool(getattr(effect, 'grace', False)) if effect else False,
            grace_note_type=self._get_grace_note_type(effect) if effect else None,
            
            # Fingering
            left_hand_finger=self._get_left_hand_finger(effect) if effect else None,
            right_hand_finger=self._get_right_hand_finger(effect) if effect else None
        )
    
    def _get_duration_string(self, beat) -> str:
        """Convert beat duration to string representation."""
        duration = getattr(beat, 'duration', None)
        if not duration:
            return "quarter"
        
        # Map duration values to string names
        duration_map = {
            1: "whole",
            2: "half", 
            4: "quarter",
            8: "eighth",
            16: "sixteenth",
            32: "thirty-second",
            64: "sixty-fourth"
        }
        
        value = getattr(duration, 'value', 4)
        return duration_map.get(value, "quarter")
    
    def _get_bend_value(self, effect) -> Optional[float]:
        """Extract bend value from note effect."""
        if hasattr(effect, 'bend') and effect.bend:
            bend = effect.bend
            if hasattr(bend, 'value'):
                return getattr(bend, 'value', 0) / 100.0  # Convert to semitones
        return None
    
    def _get_slide_type(self, effect) -> Optional[str]:
        """Extract slide type from note effect."""
        if hasattr(effect, 'slides') and effect.slides:
            slides = effect.slides
            if slides:
                return str(slides[0]) if slides else None
        return None
    
    def _convert_marker_color(self, marker) -> Optional[str]:
        """Convert marker color to hex string."""
        color = getattr(marker, 'color', None)
        if not color:
            return None
        
        if hasattr(color, 'r') and hasattr(color, 'g') and hasattr(color, 'b'):
            r = getattr(color, 'r', 0)
            g = getattr(color, 'g', 0) 
            b = getattr(color, 'b', 0)
            return f"#{r:02x}{g:02x}{b:02x}"
        
        return None
    
    def _is_hammer_on(self, effect) -> bool:
        """Check if note is a hammer-on."""
        hammer = getattr(effect, 'hammer', None)
        if not hammer:
            return False
        
        # In guitarpro, hammer-on is typically when origin note is lower than destination
        origin = getattr(hammer, 'originValue', None)
        destination = getattr(hammer, 'destinationValue', None)
        
        if origin is not None and destination is not None:
            return destination > origin
        
        # Fallback: just check if hammer effect exists
        return True
    
    def _is_pull_off(self, effect) -> bool:
        """Check if note is a pull-off."""
        hammer = getattr(effect, 'hammer', None)
        if not hammer:
            return False
        
        # In guitarpro, pull-off is typically when origin note is higher than destination  
        origin = getattr(hammer, 'originValue', None)
        destination = getattr(hammer, 'destinationValue', None)
        
        if origin is not None and destination is not None:
            return destination < origin
        
        return False
    
    def _get_grace_note_type(self, effect) -> Optional[str]:
        """Get grace note type."""
        grace = getattr(effect, 'grace', None)
        if not grace:
            return None
        
        # Check if grace note is before or on beat
        is_on_beat = getattr(grace, 'isOnBeat', False)
        return "on_beat" if is_on_beat else "before_beat"
    
    def _get_left_hand_finger(self, effect) -> Optional[int]:
        """Get left hand finger number."""
        finger = getattr(effect, 'leftHandFinger', None)
        if finger is None:
            return None
        
        # Convert finger enum/value to integer (1-4)
        if hasattr(finger, 'value'):
            finger_val = getattr(finger, 'value', 0)
        else:
            finger_val = finger
        
        try:
            finger_int = int(finger_val)
            return finger_int if 1 <= finger_int <= 4 else None
        except (ValueError, TypeError):
            return None
    
    def _get_right_hand_finger(self, effect) -> Optional[str]:
        """Get right hand finger character."""
        finger = getattr(effect, 'rightHandFinger', None)
        if finger is None:
            return None
        
        # Convert finger enum/value to character
        if hasattr(finger, 'value'):
            finger_val = getattr(finger, 'value', '')
        elif hasattr(finger, 'name'):
            finger_val = getattr(finger, 'name', '')
        else:
            finger_val = str(finger)
        
        # Map common finger values
        finger_map = {
            'thumb': 'p',
            'index': 'i', 
            'middle': 'm',
            'ring': 'a',
            'little': 'c'
        }
        
        finger_str = str(finger_val).lower()
        if finger_str in finger_map:
            return finger_map[finger_str]
        elif finger_str in ['p', 'i', 'm', 'a', 'c']:
            return finger_str
        
        return None
    
    def _get_tuplet_info(self, beat, voice=None) -> Optional[Dict[str, int]]:
        """Extract tuplet information from beat or voice."""
        tuplet = None
        
        # First try to get tuplet from beat
        beat_tuplet = getattr(beat, 'tuplet', None)
        if beat_tuplet:
            tuplet = beat_tuplet
        
        # If no tuplet on beat, try voice level  
        if not tuplet and voice:
            voice_tuplet = getattr(voice, 'tuplet', None)
            if voice_tuplet:
                tuplet = voice_tuplet
        
        # Also check if beat has duration that implies tuplet
        if not tuplet:
            duration = getattr(beat, 'duration', None)
            if duration and hasattr(duration, 'tuplet'):
                tuplet = getattr(duration, 'tuplet', None)
        
        if tuplet:
            enters = getattr(tuplet, 'enters', 3)
            times = getattr(tuplet, 'times', 2)
            
            # Only return tuplet info if it's not the default 1:1 ratio
            if enters != 1 or times != 1:
                return {
                    'enters': int(enters),
                    'times': int(times)
                }
        
        return None
    
    def _get_beat_text(self, beat, effect=None) -> str:
        """Extract text information from beat."""
        text_parts = []
        
        # Check for direct text attribute
        if hasattr(beat, 'text') and beat.text:
            text_parts.append(str(beat.text))
        
        # Check for chord information in effect
        if effect and hasattr(effect, 'chord'):
            chord = getattr(effect, 'chord', None)
            if chord:
                chord_name = getattr(chord, 'name', None) or getattr(chord, 'root', None)
                if chord_name:
                    text_parts.append(str(chord_name))
        
        # Check for chord directly on beat
        if hasattr(beat, 'chord'):
            chord = getattr(beat, 'chord', None)
            if chord:
                chord_name = getattr(chord, 'name', None) or getattr(chord, 'root', None)
                if chord_name:
                    text_parts.append(str(chord_name))
        
        # Check for any annotation or text properties
        for attr_name in ['annotation', 'textMarker', 'displayText']:
            if hasattr(beat, attr_name):
                attr_value = getattr(beat, attr_name, None)
                if attr_value:
                    text_parts.append(str(attr_value))
        
        return ' '.join(text_parts) if text_parts else ''
    
    def _extract_time_signature_safely(self, time_sig) -> 'SerializableTimeSignature':
        """Extract time signature, handling Duration objects for denominator."""
        from ...models import SerializableTimeSignature
        
        numerator = getattr(time_sig, 'numerator', 4)
        denominator_value = getattr(time_sig, 'denominator', 4)
        
        # Handle Duration object for denominator
        if hasattr(denominator_value, 'value'):
            denominator_value = denominator_value.value
            
        return SerializableTimeSignature(
            numerator=numerator,
            denominator=denominator_value
        )
    
    def _extract_song_measures(self, song, tracks) -> List:
        """Extract song-level measures with section names from first track beat text."""
        from ...models import SerializableMeasureInfo, SerializableTimeSignature
        
        measures = []
        
        # Get measure count
        measure_count = len(getattr(song, 'measureHeaders', []))
        
        # Initialize current tempo and time signature from song defaults
        current_tempo = getattr(song, 'tempo', 120)
        current_time_sig = None  # Will be set from first measure header or default to 4/4
        
        # Pre-scan for tempo changes from beat-level mix table changes
        tempo_changes = {}  # measure_number -> tempo_bpm
        for track in getattr(song, 'tracks', []):
            for measure in getattr(track, 'measures', []):
                measure_number = getattr(getattr(measure, 'header', None), 'number', 0)
                if measure_number > 0:
                    for voice in getattr(measure, 'voices', []):
                        for beat in getattr(voice, 'beats', []):
                            effect = getattr(beat, 'effect', None)
                            if effect:
                                mtc = getattr(effect, 'mixTableChange', None)
                                if mtc and hasattr(mtc, 'tempo') and mtc.tempo:
                                    tempo_value = getattr(mtc.tempo, 'value', None)
                                    if tempo_value and tempo_value > 0:
                                        # Store the first tempo change found in this measure
                                        if measure_number not in tempo_changes:
                                            tempo_changes[measure_number] = tempo_value
        
        # If no tracks, just create basic measures without section names but with repetition info
        if not tracks:
            song_measure_headers = getattr(song, 'measureHeaders', [])
            for i in range(measure_count):  # First case: no tracks
                # Still get repetition info from headers even without tracks
                repeat_open = False
                repeat_close = 0
                repeat_alternative = 0
                double_bar = False
                
                if i < len(song_measure_headers):
                    header = song_measure_headers[i]
                    repeat_open = getattr(header, 'isRepeatOpen', False)
                    repeat_close = getattr(header, 'repeatClose', 0)
                    repeat_alternative = getattr(header, 'repeatAlternative', 0)
                    double_bar = getattr(header, 'hasDoubleBar', False)
                    
                    # Update tempo if there's a tempo change (header or beat-level)
                    if hasattr(header, 'tempo') and header.tempo > 0:
                        current_tempo = header.tempo
                    elif (i + 1) in tempo_changes:
                        current_tempo = tempo_changes[i + 1]
                    
                    # Update time signature if available
                    if hasattr(header, 'timeSignature') and header.timeSignature:
                        current_time_sig = self._extract_time_signature_safely(header.timeSignature)
                    elif current_time_sig is None:
                        # Default to 4/4 if no time signature found yet
                        current_time_sig = SerializableTimeSignature(numerator=4, denominator=4)
                    
                    if repeat_close == -1:
                        repeat_close = 0
                
                measures.append(SerializableMeasureInfo(
                    number=i + 1,
                    section_name="",
                    tempo_bpm=current_tempo,
                    time_signature=current_time_sig if current_time_sig else SerializableTimeSignature(numerator=4, denominator=4),
                    repeat_open=repeat_open,
                    repeat_close=repeat_close,
                    repeat_alternative=repeat_alternative,
                    double_bar=double_bar
                ))
            return measures  # No tracks case
        
        # Use first track to extract section names from beat text
        first_track = song.tracks[0] if song.tracks else None
        if not first_track:
            # Fallback: create measures without section names but with repetition info
            song_measure_headers = getattr(song, 'measureHeaders', [])
            for i in range(measure_count):  # Second case: no first track
                repeat_open = False
                repeat_close = 0
                repeat_alternative = 0
                double_bar = False
                
                if i < len(song_measure_headers):
                    header = song_measure_headers[i]
                    repeat_open = getattr(header, 'isRepeatOpen', False)
                    repeat_close = getattr(header, 'repeatClose', 0)
                    repeat_alternative = getattr(header, 'repeatAlternative', 0)
                    double_bar = getattr(header, 'hasDoubleBar', False)
                    
                    # Update tempo if there's a tempo change (header or beat-level)
                    if hasattr(header, 'tempo') and header.tempo > 0:
                        current_tempo = header.tempo
                    elif (i + 1) in tempo_changes:
                        current_tempo = tempo_changes[i + 1]
                    
                    # Update time signature if available
                    if hasattr(header, 'timeSignature') and header.timeSignature:
                        current_time_sig = self._extract_time_signature_safely(header.timeSignature)
                    elif current_time_sig is None:
                        # Default to 4/4 if no time signature found yet
                        current_time_sig = SerializableTimeSignature(numerator=4, denominator=4)
                    
                    if repeat_close == -1:
                        repeat_close = 0
                
                measures.append(SerializableMeasureInfo(
                    number=i + 1,
                    section_name="",
                    tempo_bpm=current_tempo,
                    time_signature=current_time_sig if current_time_sig else SerializableTimeSignature(numerator=4, denominator=4),
                    repeat_open=repeat_open,
                    repeat_close=repeat_close,
                    repeat_alternative=repeat_alternative,
                    double_bar=double_bar
                ))
            return measures  # No first track case
        
        # Extract section names and repetition info from first track measures and song headers
        track_measures = getattr(first_track, 'measures', [])
        song_measure_headers = getattr(song, 'measureHeaders', [])
        
        for measure_idx in range(measure_count):
            measure_number = measure_idx + 1
            section_name = ""
            
            # Get repetition information from measure header
            repeat_open = False
            repeat_close = 0
            repeat_alternative = 0
            double_bar = False
            
            if measure_idx < len(song_measure_headers):
                header = song_measure_headers[measure_idx]
                repeat_open = getattr(header, 'isRepeatOpen', False)
                repeat_close = getattr(header, 'repeatClose', 0)
                repeat_alternative = getattr(header, 'repeatAlternative', 0)
                double_bar = getattr(header, 'hasDoubleBar', False)
                
                # Update tempo if there's a tempo change (header or beat-level)
                if hasattr(header, 'tempo') and header.tempo > 0:
                    current_tempo = header.tempo
                elif measure_number in tempo_changes:
                    current_tempo = tempo_changes[measure_number]
                
                # Update time signature if available
                if hasattr(header, 'timeSignature') and header.timeSignature:
                    current_time_sig = self._extract_time_signature_safely(header.timeSignature)
                elif current_time_sig is None:
                    # Default to 4/4 if no time signature found yet
                    current_time_sig = SerializableTimeSignature(numerator=4, denominator=4)
                
                # Handle repeat close value (-1 means no repeat in guitarpro)
                if repeat_close == -1:
                    repeat_close = 0
            elif current_time_sig is None:
                # Ensure we have a default time signature even if no headers
                current_time_sig = SerializableTimeSignature(numerator=4, denominator=4)
            
            # Get the corresponding measure from first track for section name
            if measure_idx < len(track_measures):
                measure = track_measures[measure_idx]
                voices = getattr(measure, 'voices', [])
                
                # Look for text in the first voice's first beat
                for voice in voices:
                    voice_beats = getattr(voice, 'beats', [])
                    if voice_beats:
                        first_beat = voice_beats[0]
                        # Extract text from this beat
                        beat_text = self._get_beat_text(first_beat, getattr(first_beat, 'effect', None))
                        if beat_text.strip():
                            section_name = beat_text.strip()
                            break
                    if section_name:
                        break
            
            measures.append(SerializableMeasureInfo(
                number=measure_number,
                section_name=section_name,
                tempo_bpm=current_tempo,
                time_signature=current_time_sig,
                repeat_open=repeat_open,
                repeat_close=repeat_close,
                repeat_alternative=repeat_alternative,
                double_bar=double_bar
            ))
        
        return measures