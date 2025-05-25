from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel, Field
import tempfile
import os
import cv2
import numpy as np
from moviepy import VideoFileClip, AudioFileClip
import soundfile as sf
from datetime import datetime

from api.abstractions.storage import FileReference
from api.services.storage import FileStorageService
from api.infrastructure.logging import get_logger
from ...models import ParsedTabData, SerializableMeasureInfo


class VideoExportCommand(BaseModel):
    """Command to export a metronome video from parsed tab data."""
    
    song_id: str = Field(..., description="ID of the song being exported")
    parsed_data: ParsedTabData = Field(..., description="Parsed tab data to generate video from")
    output_format: str = Field("mp4", description="Output video format")
    resolution: tuple = Field((1920, 1080), description="Video resolution (width, height)")
    fps: int = Field(30, description="Frames per second")
    duration_per_measure: Optional[float] = Field(None, description="Override duration per measure in seconds")
    count_in_measures: int = Field(0, description="Number of count-in measures before the song starts")
    filename: Optional[str] = Field(None, description="Original filename of the tab file")


class VideoExportResult(BaseModel):
    """Result of video export operation."""
    
    success: bool = Field(..., description="Whether the export was successful")
    video_file: Optional[FileReference] = Field(None, description="Reference to the exported video file")
    duration_seconds: float = Field(0, description="Total video duration in seconds")
    total_measures: int = Field(0, description="Total number of measures in the video")
    error_message: Optional[str] = Field(None, description="Error message if export failed")


class VideoExportHandler(ABC):
    """Abstract handler for video export operations."""
    
    @abstractmethod
    async def handle(self, command: VideoExportCommand) -> VideoExportResult:
        """Handle the video export command."""
        pass


class VideoExportHandlerImpl(VideoExportHandler):
    """Implementation of video export handler."""
    
    def __init__(self, storage_service: Optional[FileStorageService] = None):
        self.storage_service = storage_service or FileStorageService()
        self.logger = get_logger(__name__)
    
    async def handle(self, command: VideoExportCommand) -> VideoExportResult:
        """Generate a metronome video from parsed tab data."""
        try:
            # Calculate timing
            tempo_bpm = command.parsed_data.song_info.tempo
            beats_per_second = tempo_bpm / 60.0
            seconds_per_beat = 60.0 / tempo_bpm
            
            # Get time signature (assume 4/4 if not specified)
            time_signature_num = 4  # Default to 4/4
            if command.parsed_data.tracks and command.parsed_data.tracks[0].measures:
                first_measure = command.parsed_data.tracks[0].measures[0]
                if first_measure.time_signature:
                    time_signature_num = first_measure.time_signature.numerator
            
            # Calculate total video duration with dynamic tempo changes including count-in
            total_duration = 0
            current_tempo = tempo_bpm
            
            # Add count-in duration first
            if command.count_in_measures > 0:
                if command.duration_per_measure:
                    count_in_duration = command.duration_per_measure * command.count_in_measures
                else:
                    seconds_per_beat = 60.0 / current_tempo
                    count_in_duration = seconds_per_beat * time_signature_num * command.count_in_measures
                total_duration += count_in_duration
            
            # Add song measures duration
            for measure in command.parsed_data.measures:
                # Get tempo for this measure
                measure_tempo = measure.tempo_bpm if measure.tempo_bpm else current_tempo
                measure_time_sig_num = measure.time_signature.numerator if measure.time_signature else time_signature_num
                
                # Calculate duration for this measure
                if command.duration_per_measure:
                    measure_duration = command.duration_per_measure
                else:
                    seconds_per_beat = 60.0 / measure_tempo
                    measure_duration = seconds_per_beat * measure_time_sig_num
                
                total_duration += measure_duration
                current_tempo = measure_tempo
            
            total_measures = command.parsed_data.measure_count + command.count_in_measures
            
            # Calculate average values for logging
            avg_seconds_per_measure = total_duration / total_measures if total_measures > 0 else 60.0 / tempo_bpm * time_signature_num
            
            self.logger.info(f"Generating video: {total_measures} measures, {tempo_bpm} BPM, {total_duration:.1f}s")
            
            # Generate video with dynamic tempo and time signature handling
            video_path = await self._generate_video(
                command.parsed_data,
                command.resolution,
                command.fps,
                tempo_bpm,  # Initial values for fallback
                time_signature_num,
                avg_seconds_per_measure,
                total_duration,
                command.count_in_measures,
                command
            )
            
            # Store the video file with timestamp in songs folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{command.parsed_data.song_info.title or 'metronome'}_video_{timestamp}.{command.output_format}"
            file_path = f"songs/{command.song_id}/{filename}"
            
            with open(video_path, 'rb') as video_file:
                video_file_ref = await self.storage_service.save_file(
                    file_path,
                    video_file
                )
            
            # Clean up temporary file
            os.unlink(video_path)
            
            return VideoExportResult(
                success=True,
                video_file=video_file_ref,
                duration_seconds=total_duration,
                total_measures=total_measures
            )
            
        except Exception as e:
            self.logger.error(f"Video export failed: {str(e)}")
            return VideoExportResult(
                success=False,
                error_message=str(e)
            )
    
    async def _generate_video(
        self,
        parsed_data: ParsedTabData,
        resolution: tuple,
        fps: int,
        initial_tempo_bpm: int,
        initial_time_signature_num: int,
        initial_seconds_per_measure: float,
        total_duration: float,
        count_in_measures: int = 0,
        command: VideoExportCommand = None
    ) -> str:
        """Generate the actual video file with dynamic tempo and time signature changes."""
        
        width, height = resolution
        total_frames = int(total_duration * fps)
        
        # Create temporary video file
        temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_video.close()
        
        # Video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(temp_video.name, fourcc, fps, (width, height))
        
        try:
            # Generate metronome audio with dynamic tempo changes
            audio_path = await self._generate_metronome_audio(parsed_data, total_duration, count_in_measures)
            
            # Generate video frames
            for frame_num in range(total_frames):
                current_time = frame_num / fps
                frame = self._create_frame(parsed_data, width, height, current_time, count_in_measures, command)
                video_writer.write(frame)
            
            video_writer.release()
            
            # Combine video with audio
            final_video_path = await self._combine_video_audio(temp_video.name, audio_path)
            
            # Clean up temporary files
            os.unlink(temp_video.name)
            os.unlink(audio_path)
            
            return final_video_path
            
        except Exception as e:
            video_writer.release()
            if os.path.exists(temp_video.name):
                os.unlink(temp_video.name)
            raise e
    
    def _get_tempo_and_time_sig_at_time(self, parsed_data: ParsedTabData, current_time: float, count_in_measures: int = 0) -> tuple:
        """Get the current tempo and time signature at a specific time in the song."""
        
        current_tempo = parsed_data.song_info.tempo  # Default from song
        current_time_sig_num = 4  # Default to 4/4
        
        # Calculate count-in duration
        count_in_duration = 0
        if count_in_measures > 0:
            seconds_per_beat = 60.0 / current_tempo
            count_in_duration = seconds_per_beat * current_time_sig_num * count_in_measures
        
        # If we're still in count-in phase, return initial values
        if current_time < count_in_duration:
            return current_tempo, current_time_sig_num
        
        # Calculate which measure we're in based on cumulative time (after count-in)
        cumulative_time = count_in_duration
        adjusted_time = current_time
        
        for measure in parsed_data.measures:
            # Get tempo and time signature for this measure
            measure_tempo = measure.tempo_bpm if measure.tempo_bpm else current_tempo
            measure_time_sig = measure.time_signature.numerator if measure.time_signature else current_time_sig_num
            
            # Calculate duration of this measure
            seconds_per_beat = 60.0 / measure_tempo
            seconds_per_measure = seconds_per_beat * measure_time_sig
            
            # Check if current_time falls within this measure
            if adjusted_time <= cumulative_time + seconds_per_measure:
                return measure_tempo, measure_time_sig
            
            # Update for next iteration
            cumulative_time += seconds_per_measure
            current_tempo = measure_tempo
            current_time_sig_num = measure_time_sig
        
        # If we're past all measures, return the last known values
        return current_tempo, current_time_sig_num
    
    def _get_current_measure_and_position(self, parsed_data: ParsedTabData, current_time: float, count_in_measures: int = 0) -> tuple:
        """Get the current measure number and position within that measure."""
        
        current_tempo = parsed_data.song_info.tempo
        
        # Calculate count-in duration
        count_in_duration = 0
        if count_in_measures > 0:
            seconds_per_beat = 60.0 / current_tempo
            count_in_duration = seconds_per_beat * 4 * count_in_measures  # Assume 4/4 for count-in
        
        # If we're in count-in phase
        if current_time < count_in_duration:
            seconds_per_beat = 60.0 / current_tempo
            seconds_per_measure = seconds_per_beat * 4  # Assume 4/4 for count-in
            count_in_measure = int(current_time / seconds_per_measure) + 1
            
            time_in_measure = current_time % seconds_per_measure
            beat_position = time_in_measure / seconds_per_beat
            current_beat = int(beat_position) + 1
            current_quarter = int(beat_position) + 1
            
            # Return negative measure number to indicate count-in
            return -count_in_measure, current_beat, current_quarter, seconds_per_measure
        
        # We're in the actual song measures
        cumulative_time = count_in_duration
        
        for measure in parsed_data.measures:
            measure_tempo = measure.tempo_bpm if measure.tempo_bpm else current_tempo
            measure_time_sig_num = measure.time_signature.numerator if measure.time_signature else 4
            
            seconds_per_beat = 60.0 / measure_tempo
            seconds_per_measure = seconds_per_beat * measure_time_sig_num
            
            if current_time <= cumulative_time + seconds_per_measure:
                # We're in this measure
                time_in_measure = current_time - cumulative_time
                beat_position = (time_in_measure / seconds_per_beat) % measure_time_sig_num
                current_beat = int(beat_position) + 1
                current_quarter = int(beat_position) + 1  # Same as beat for 4/4
                
                return measure.number, current_beat, current_quarter, seconds_per_measure
            
            cumulative_time += seconds_per_measure
            current_tempo = measure_tempo
        
        # Default if past all measures
        return len(parsed_data.measures), 1, 1, 60.0 / current_tempo * 4
    
    def _create_frame(
        self,
        parsed_data: ParsedTabData,
        width: int,
        height: int,
        current_time: float,
        count_in_measures: int = 0,
        command: VideoExportCommand = None
    ) -> np.ndarray:
        """Create a single video frame with dynamic tempo and time signature."""
        
        # Create black background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Get dynamic tempo and time signature for current time
        tempo_bpm, time_signature_num = self._get_tempo_and_time_sig_at_time(parsed_data, current_time, count_in_measures)
        current_measure, current_beat, current_quarter, seconds_per_measure = self._get_current_measure_and_position(parsed_data, current_time, count_in_measures)
        
        # Define colors
        white = (255, 255, 255)
        green = (0, 255, 0)
        red = (0, 0, 255)
        yellow = (0, 255, 255)
        orange = (0, 165, 255)  # For count-in
        
        # Font settings
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Title - use filename if available, otherwise song title, otherwise "Metronome"
        if command and command.filename:
            # Remove file extension and use filename
            title = command.filename.rsplit('.', 1)[0] if '.' in command.filename else command.filename
        else:
            title = parsed_data.song_info.title or "Metronome"
        cv2.putText(frame, title, (width//2 - len(title)*20, 80), 
                   font, 2, white, 3, cv2.LINE_AA)
        
        # Tempo
        tempo_text = f"Tempo: {tempo_bpm} BPM"
        cv2.putText(frame, tempo_text, (50, height - 50), 
                   font, 1, white, 2, cv2.LINE_AA)
        
        # Check if we're in count-in phase
        if current_measure < 0:
            # Count-in phase
            count_in_number = abs(current_measure)
            
            # Count-in measure number
            if count_in_measures > 2:
                measure_text = f"Count-in {count_in_number}"
            else:
                measure_text = f"Count-in {count_in_number}"
            cv2.putText(frame, measure_text, (width//2 - 180, height//2 - 140), 
                       font, 3, orange, 4, cv2.LINE_AA)
            
            # Current section (disabled during count-in)
            section_text = "Ready to start..."
            cv2.putText(frame, section_text, (width//2 - len(section_text)*15, height//2 - 60), 
                       font, 2, orange, 3, cv2.LINE_AA)
        else:
            # Regular song measures
            # Get current section name
            current_section = self._get_current_section(parsed_data.measures, current_measure)
            
            # Current measure (large, centered)
            measure_text = f"Measure {current_measure}"
            cv2.putText(frame, measure_text, (width//2 - 150, height//2 - 140), 
                       font, 3, green, 4, cv2.LINE_AA)
            
            # Current section
            section_text = f"Section: {current_section}"
            cv2.putText(frame, section_text, (width//2 - len(section_text)*15, height//2 - 60), 
                       font, 2, yellow, 3, cv2.LINE_AA)
        
        # Beat counter
        beat_text = f"Beat: {current_beat}/{time_signature_num}"
        cv2.putText(frame, beat_text, (width//2 - 100, height//2 + 40), 
                   font, 2, white, 3, cv2.LINE_AA)
        
        # Visual metronome
        self._draw_metronome(frame, width, height, current_time, tempo_bpm, time_signature_num)
        
        # Beat indicators
        self._draw_beat_indicators(frame, width, height, current_beat, time_signature_num)
        
        return frame
    
    def _get_current_section(self, measures: List[SerializableMeasureInfo], current_measure: int) -> str:
        """Get the section name for the current measure."""
        current_section = ""
        for measure in measures:
            if measure.number <= current_measure and measure.section_name:
                current_section = measure.section_name
        return current_section or "Main"
    
    def _draw_metronome(self, frame: np.ndarray, width: int, height: int, 
                       current_time: float, tempo_bpm: int, time_signature_num: int):
        """Draw visual metronome pendulum."""
        
        seconds_per_beat = 60.0 / tempo_bpm
        beat_progress = (current_time % seconds_per_beat) / seconds_per_beat
        
        # Metronome pendulum
        center_x = width // 2
        center_y = height // 2 + 250  # Moved down by 50 pixels
        pendulum_length = 150
        
        # Calculate pendulum angle (swings back and forth)
        max_angle = 0.5  # radians
        angle = max_angle * np.sin(beat_progress * 2 * np.pi)
        
        end_x = int(center_x + pendulum_length * np.sin(angle))
        end_y = int(center_y - pendulum_length * np.cos(angle))
        
        # Draw pendulum
        cv2.line(frame, (center_x, center_y), (end_x, end_y), (255, 255, 255), 5)
        cv2.circle(frame, (end_x, end_y), 20, (255, 255, 255), -1)
        cv2.circle(frame, (center_x, center_y), 10, (255, 255, 255), -1)
    
    def _draw_beat_indicators(self, frame: np.ndarray, width: int, height: int, 
                            current_beat: int, time_signature_num: int):
        """Draw beat indicator lights."""
        
        indicator_y = height - 150
        indicator_spacing = 80
        start_x = width // 2 - (time_signature_num * indicator_spacing) // 2
        
        for beat_num in range(1, time_signature_num + 1):
            x = start_x + (beat_num - 1) * indicator_spacing
            color = (0, 255, 0) if beat_num == current_beat else (50, 50, 50)
            if beat_num == 1:  # Emphasize beat 1
                color = (0, 0, 255) if beat_num == current_beat else (50, 0, 0)
            
            cv2.circle(frame, (x, indicator_y), 25, color, -1)
            cv2.putText(frame, str(beat_num), (x-8, indicator_y+8), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    async def _generate_metronome_audio(self, parsed_data: ParsedTabData, duration: float, count_in_measures: int = 0) -> str:
        """Generate metronome audio with dynamic tempo changes and emphasis on beat 1."""
        
        sample_rate = 44100
        total_samples = int(duration * sample_rate)
        audio = np.zeros(total_samples)
        
        # Generate click sounds
        beat_1_freq = 1000  # Higher pitch for beat 1
        other_beat_freq = 800  # Lower pitch for other beats
        click_duration = 0.1  # 100ms clicks
        click_samples = int(click_duration * sample_rate)
        
        # Generate sine wave clicks
        t_click = np.linspace(0, click_duration, click_samples)
        
        beat_1_click = np.sin(2 * np.pi * beat_1_freq * t_click) * 0.5
        other_beat_click = np.sin(2 * np.pi * other_beat_freq * t_click) * 0.3
        
        # Apply envelope to avoid clicks
        envelope = np.exp(-t_click * 10)
        beat_1_click *= envelope
        other_beat_click *= envelope
        
        # Generate beats by iterating through measures and beats
        current_time = 0
        current_tempo = parsed_data.song_info.tempo
        
        # First, generate count-in measures
        if count_in_measures > 0:
            seconds_per_beat = 60.0 / current_tempo
            time_signature_num = 4  # Assume 4/4 for count-in
            
            for count_in_measure in range(count_in_measures):
                for beat_num in range(1, time_signature_num + 1):
                    sample_idx = int(current_time * sample_rate)
                    
                    # Add click if within audio bounds
                    if sample_idx + click_samples <= total_samples:
                        if beat_num == 1:  # Always beat 1 of measure gets high pitch
                            audio[sample_idx:sample_idx + click_samples] += beat_1_click
                        else:
                            audio[sample_idx:sample_idx + click_samples] += other_beat_click
                    
                    # Advance to next beat
                    current_time += seconds_per_beat
                    
                    # Stop if we've exceeded the duration
                    if current_time >= duration:
                        break
                
                # Stop if we've exceeded the duration
                if current_time >= duration:
                    break
        
        # Then generate song measures
        for measure in parsed_data.measures:
            # Get tempo and time signature for this measure
            measure_tempo = measure.tempo_bpm if measure.tempo_bpm else current_tempo
            measure_time_sig_num = measure.time_signature.numerator if measure.time_signature else 4
            
            # Calculate beat timing for this measure
            seconds_per_beat = 60.0 / measure_tempo
            
            # Generate beats for this measure
            for beat_num in range(1, measure_time_sig_num + 1):
                sample_idx = int(current_time * sample_rate)
                
                # Add click if within audio bounds
                if sample_idx + click_samples <= total_samples:
                    if beat_num == 1:  # Always beat 1 of measure gets high pitch
                        audio[sample_idx:sample_idx + click_samples] += beat_1_click
                    else:
                        audio[sample_idx:sample_idx + click_samples] += other_beat_click
                
                # Advance to next beat
                current_time += seconds_per_beat
                
                # Stop if we've exceeded the duration
                if current_time >= duration:
                    break
            
            # Update current tempo for next measure
            current_tempo = measure_tempo
            
            # Stop if we've exceeded the duration
            if current_time >= duration:
                break
        
        # Save audio file
        temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_audio.close()
        
        sf.write(temp_audio.name, audio, sample_rate)
        return temp_audio.name
    
    async def _combine_video_audio(self, video_path: str, audio_path: str) -> str:
        """Combine video and audio using moviepy."""
        
        temp_final = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_final.close()
        
        try:
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            
            final_clip = video_clip.with_audio(audio_clip)
            final_clip.write_videofile(temp_final.name, codec='libx264', audio_codec='aac')
            
            video_clip.close()
            audio_clip.close()
            final_clip.close()
            
            return temp_final.name
            
        except Exception as e:
            if os.path.exists(temp_final.name):
                os.unlink(temp_final.name)
            raise e