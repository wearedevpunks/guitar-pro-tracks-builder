# Video Export Feature

The video export feature generates metronome videos from Guitar Pro tabs to help bands practice songs together. The videos display visual and audio cues for timing, sections, and song structure.

## Features

### Visual Elements
- **Large measure counter** - Shows current measure number prominently
- **Section names** - Displays current song section (Intro, Verse, Chorus, etc.)
- **Beat counter** - Shows current beat within measure (1/4, 2/4, etc.)
- **Quarter note counter** - Shows quarter note position for timing
- **Visual metronome** - Animated pendulum that swings with the beat
- **Beat indicators** - Visual lights for each beat with emphasis on beat 1
- **Song information** - Title, artist, and tempo display
- **Tempo display** - Current BPM shown throughout

### Audio Elements
- **Metronome clicks** - Steady beat throughout the song
- **Beat 1 emphasis** - Higher pitch click (1000 Hz) on first beat of each measure
- **Other beats** - Lower pitch click (800 Hz) for beats 2-4
- **Customizable volume** - Adjustable click volume

### Song Structure Support
- **Section navigation** - Automatically shows section changes
- **Repeat markers** - Supports repeat sections and alternative endings
- **Measure counting** - Accurate measure progression with repetitions
- **Song timeline** - Complete playback structure understanding

## Implementation

### Command Structure (CQRS Pattern)

```python
from api.features.tabs.commands.video_export import VideoExportCommand, VideoExportResult

# Create export command
command = VideoExportCommand(
    parsed_data=parsed_tab_data,
    output_format="mp4",
    resolution=(1920, 1080),
    fps=30
)

# Execute export
tabs_service = get_tabs_service()
result = await tabs_service.export_video(parsed_data, resolution=(1280, 720))
```

### Service Integration

The video export is integrated into the main `TabsService`:

```python
async def export_video(self, parsed_data, **kwargs) -> VideoExportResult:
    """Export a metronome video from parsed tab data."""
```

### Video Specifications

**Default Settings:**
- Resolution: 1920x1080 (configurable)
- Frame rate: 30 fps (configurable)
- Format: MP4
- Audio: 44.1kHz WAV embedded

**Timing Calculation:**
- Based on song tempo (BPM)
- Supports 4/4 time signature
- Accurate beat subdivision
- Handles measure duration overrides

## Dependencies

The video export feature requires additional Python packages:

```bash
pip install -r video_export_requirements.txt
```

**Required packages:**
- `opencv-python` - Video frame generation
- `moviepy` - Video/audio composition
- `librosa` - Audio processing
- `soundfile` - Audio file I/O
- `numpy` - Numerical operations

## Usage Examples

### Basic Export

```python
# Parse a Guitar Pro file
parse_result = await tabs_service.parse_tab(file_reference)

if parse_result.success:
    # Export video
    video_result = await tabs_service.export_video(
        parse_result.parsed_data,
        resolution=(1280, 720),
        fps=24
    )
    
    if video_result.success:
        print(f"Video exported: {video_result.video_file.filename}")
        print(f"Duration: {video_result.duration_seconds} seconds")
```

### Custom Settings

```python
video_result = await tabs_service.export_video(
    parsed_data,
    output_format="mp4",
    resolution=(1920, 1080),
    fps=30,
    duration_per_measure=2.0  # Override measure duration
)
```

## File Structure

```
api/features/tabs/commands/video_export/
├── __init__.py                 # Main video export implementation
├── simple_test.py             # Test without video dependencies
└── README.md                  # This documentation

video_export_requirements.txt   # Additional dependencies
video_export_demo.py            # Demonstration script
```

## Video Layout

```
┌─────────────────────────────────────┐
│           Song Title                │
│                                     │
│            Measure 5                │  ← Large measure number
│          Section: Verse 1           │  ← Current section
│                                     │
│           Beat: 2/4                 │  ← Beat counter
│          Quarter: 2                 │  ← Quarter note counter
│                                     │
│              🎼                    │  ← Visual metronome
│             /                       │    (Animated pendulum)
│            O                        │
│                                     │
│        ● ○ ○ ○                     │  ← Beat indicators
│        1 2 3 4                     │    (Red = beat 1, green = current)
│                                     │
│   Tempo: 120 BPM                   │  ← Tempo display
└─────────────────────────────────────┘
```

## Band Practice Benefits

### For Musicians
- **Visual timing cues** - Easy to see current beat and measure
- **Section awareness** - Know which part of the song is playing
- **Consistent tempo** - Steady metronome prevents tempo drift
- **Practice structure** - Clear measure counting for rehearsal

### For Bands
- **Synchronized practice** - Everyone sees the same timing cues
- **Song structure** - Visual guide through song sections
- **Repeat handling** - Automatic navigation through repeats
- **Professional appearance** - Clean, readable display for rehearsals

## Technical Details

### Video Generation Process
1. **Parse timing** - Extract tempo and time signature from tab data
2. **Calculate frames** - Generate frame timeline based on song structure
3. **Render visuals** - Create video frames with measure/beat information
4. **Generate audio** - Create metronome click track with beat emphasis
5. **Compose final video** - Combine visual and audio into MP4 file

### Performance Considerations
- **Frame generation** - Efficient OpenCV rendering for smooth video
- **Audio synthesis** - Real-time generation of metronome clicks
- **Memory usage** - Streaming video generation for large songs
- **File size** - Optimized encoding for web delivery

## Current Status

✅ **Complete Implementation**
- Command/Query structure
- Service integration
- Video generation logic
- Audio metronome synthesis
- Section/repeat support
- Visual layout design

🔄 **Dependencies Required**
- Install video processing libraries
- Uncomment imports in service code
- Test with actual Guitar Pro files

## Demo

Run the demonstration to see the video concept:

```bash
python video_export_demo.py
```

This shows the video layout, timing calculations, and export specifications without requiring video dependencies.

## Future Enhancements

- **Multiple time signatures** - Support for 3/4, 6/8, etc.
- **Custom themes** - Different visual styles and colors
- **Chord display** - Show chord names from tab beat text
- **Loop sections** - Repeat specific sections for practice
- **Export formats** - Support for different video formats
- **Performance optimization** - Faster rendering for long songs