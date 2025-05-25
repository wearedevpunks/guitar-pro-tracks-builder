from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel, Field
import tempfile
import os
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip
import librosa
import soundfile as sf

from api.abstractions.storage import FileReference
from api.services.storage import FileStorageService
from api.infrastructure.logging import get_logger
from ...models import ParsedTabData, SerializableMeasureInfo


class VideoExportCommand(BaseModel):
    """Command to export a metronome video from parsed tab data."""
    
    parsed_data: ParsedTabData = Field(..., description="Parsed tab data to generate video from")
    output_format: str = Field("mp4", description="Output video format")
    resolution: tuple = Field((1920, 1080), description="Video resolution (width, height)")
    fps: int = Field(30, description="Frames per second")
    duration_per_measure: Optional[float] = Field(None, description="Override duration per measure in seconds")


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
            
            seconds_per_measure = seconds_per_beat * time_signature_num
            if command.duration_per_measure:
                seconds_per_measure = command.duration_per_measure
            
            total_measures = command.parsed_data.measure_count
            total_duration = seconds_per_measure * total_measures
            
            self.logger.info(f"Generating video: {total_measures} measures, {tempo_bpm} BPM, {total_duration:.1f}s")
            
            # Generate video
            video_path = await self._generate_video(
                command.parsed_data,
                command.resolution,
                command.fps,
                tempo_bpm,
                time_signature_num,
                seconds_per_measure,
                total_duration
            )
            
            # Store the video file
            video_file_ref = await self.storage_service.store_file(
                video_path,
                f"{command.parsed_data.song_info.title or 'metronome'}_video.{command.output_format}"
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
        tempo_bpm: int,
        time_signature_num: int,
        seconds_per_measure: float,
        total_duration: float
    ) -> str:
        """Generate the actual video file."""
        
        width, height = resolution
        total_frames = int(total_duration * fps)
        
        # Create temporary video file
        temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_video.close()
        
        # Video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(temp_video.name, fourcc, fps, (width, height))
        
        try:
            # Generate metronome audio
            audio_path = await self._generate_metronome_audio(
                tempo_bpm, time_signature_num, total_duration
            )
            
            # Generate video frames
            for frame_num in range(total_frames):
                current_time = frame_num / fps
                frame = self._create_frame(
                    parsed_data, width, height, current_time, 
                    tempo_bpm, time_signature_num, seconds_per_measure
                )
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
    
    def _create_frame(
        self,
        parsed_data: ParsedTabData,
        width: int,
        height: int,
        current_time: float,
        tempo_bpm: int,
        time_signature_num: int,
        seconds_per_measure: float
    ) -> np.ndarray:
        """Create a single video frame."""
        
        # Create black background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Calculate current position
        current_measure = int(current_time / seconds_per_measure) + 1
        time_in_measure = current_time % seconds_per_measure
        current_beat = int(time_in_measure / (seconds_per_measure / time_signature_num)) + 1
        current_quarter = current_beat  # For 4/4 time, beat = quarter note
        
        # Get current section name
        current_section = self._get_current_section(parsed_data.measures, current_measure)
        
        # Define colors
        white = (255, 255, 255)
        green = (0, 255, 0)
        red = (0, 0, 255)
        yellow = (0, 255, 255)
        
        # Font settings
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Title
        title = parsed_data.song_info.title or "Metronome"
        cv2.putText(frame, title, (width//2 - len(title)*20, 100), 
                   font, 2, white, 3, cv2.LINE_AA)
        
        # Tempo
        tempo_text = f"Tempo: {tempo_bpm} BPM"
        cv2.putText(frame, tempo_text, (50, height - 50), 
                   font, 1, white, 2, cv2.LINE_AA)
        
        # Current measure (large, centered)
        measure_text = f"Measure {current_measure}"
        cv2.putText(frame, measure_text, (width//2 - 150, height//2 - 100), 
                   font, 3, green, 4, cv2.LINE_AA)
        
        # Current section
        section_text = f"Section: {current_section}"
        cv2.putText(frame, section_text, (width//2 - len(section_text)*15, height//2 - 20), 
                   font, 2, yellow, 3, cv2.LINE_AA)
        
        # Beat counter
        beat_text = f"Beat: {current_beat}/{time_signature_num}"
        cv2.putText(frame, beat_text, (width//2 - 100, height//2 + 60), 
                   font, 2, white, 3, cv2.LINE_AA)
        
        # Quarter note counter (same as beat for 4/4)
        quarter_text = f"Quarter: {current_quarter}"
        cv2.putText(frame, quarter_text, (width//2 - 120, height//2 + 120), 
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
        center_y = height // 2 + 200
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
    
    async def _generate_metronome_audio(self, tempo_bpm: int, time_signature_num: int, 
                                       duration: float) -> str:
        """Generate metronome audio with emphasis on beat 1."""
        
        sample_rate = 44100
        total_samples = int(duration * sample_rate)
        audio = np.zeros(total_samples)
        
        seconds_per_beat = 60.0 / tempo_bpm
        samples_per_beat = int(seconds_per_beat * sample_rate)
        
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
        
        # Place clicks in audio
        current_beat = 1
        for sample_idx in range(0, total_samples, samples_per_beat):
            if sample_idx + click_samples <= total_samples:
                if current_beat == 1:
                    audio[sample_idx:sample_idx + click_samples] += beat_1_click
                else:
                    audio[sample_idx:sample_idx + click_samples] += other_beat_click
                
                current_beat = (current_beat % time_signature_num) + 1
        
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
            
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile(temp_final.name, codec='libx264', audio_codec='aac')
            
            video_clip.close()
            audio_clip.close()
            final_clip.close()
            
            return temp_final.name
            
        except Exception as e:
            if os.path.exists(temp_final.name):
                os.unlink(temp_final.name)
            raise e