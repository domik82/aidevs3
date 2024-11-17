from __future__ import annotations
import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

import whisper
from whisper.utils import get_writer
from whisper import Whisper
from pydub import AudioSegment

from src.tools.find_project_root import find_project_root


@dataclass
class TranscriptionResult:
    text: str
    segments: List[Dict[str, Any]]
    output_files: Dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.text


class AudioTranscriber:
    def __init__(
        self,
        model_size: str = "base",
        language: str = "en",
    ) -> None:
        """
        Initialize the AudioTranscriber with model and language settings.

        Args:
            model_size: Size of the Whisper model to use (e.g., "base", "small", "medium")
            language: Language code for transcription (e.g., "en" for English)
        """
        self.model: Whisper = whisper.load_model(model_size)
        self.language = language

    def transcribe_audio(
        self,
        audio_path: str,
        output_dir: Optional[str] = None,
        output_filename: Optional[str] = None,
        save_formats: Optional[List[str]] = None,
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe an audio file and optionally save in specified formats.

        Args:
            audio_path: Path to the audio file
            output_dir: Directory where transcription files will be saved
            output_filename: Name for the output files (without extension)
            save_formats: List of format types to save (e.g., ["txt", "srt", "vtt"])
        Returns:
            TranscriptionResult object or None if transcription fails
        """
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            result = self.model.transcribe(
                audio=audio_path, language=self.language, verbose=True
            )

            transcription_result = TranscriptionResult(
                result["text"], result["segments"]
            )

            if save_formats and output_dir:
                os.makedirs(output_dir, exist_ok=True)
                output_files = self._save_transcription(
                    result, output_dir, save_formats, output_filename or "transcription"
                )
                transcription_result.output_files = output_files

            return transcription_result

        except Exception as e:
            print(f"An error occurred during transcription: {str(e)}")
            return None

    def _save_transcription(
        self, result: Dict[str, Any], output_dir: str, formats: List[str], filename: str
    ) -> Dict[str, str]:
        """
        Save transcription results in specified formats.

        Returns:
            Dictionary mapping format to full output path
        """
        output_files = {}

        for format_type in formats:
            writer = get_writer(format_type, output_dir)
            output_file = os.path.join(output_dir, f"{filename}.{format_type}")
            writer(result, output_file)
            output_files[format_type] = output_file

        return output_files

    def process_long_audio(
        self,
        audio_path: str,
        segment_length_minutes: int = 10,
        save_temp_files: bool = False,
    ) -> Optional[TranscriptionResult]:
        """
        Process long audio files by splitting them into segments.

        Args:
            audio_path: Path to the audio file
            segment_length_minutes: Length of each segment in minutes
            save_temp_files: Whether to save temporary segment files
        Returns:
            TranscriptionResult object or None if processing fails
        """
        try:
            temp_dir = self.output_dir if save_temp_files else None
            temp_file = (
                os.path.join(temp_dir, "temp_segment.mp3")
                if temp_dir
                else os.path.join(os.getcwd(), "temp_segment.mp3")
            )

            audio = AudioSegment.from_mp3(audio_path)
            segment_length = (
                segment_length_minutes * 60 * 1000
            )  # Convert to milliseconds
            segments: List[str] = []
            all_segment_data: List[Dict[str, Any]] = []

            for start in range(0, len(audio), segment_length):
                segment = audio[start : start + segment_length]
                segment.export(temp_file, format="mp3")

                result = self.transcribe_audio(temp_file)
                if result:
                    segments.append(result.text)
                    all_segment_data.extend(result.segments)

            # Clean up temporary file if not saving
            if not save_temp_files and os.path.exists(temp_file):
                os.remove(temp_file)

            if segments:
                return TranscriptionResult(
                    text=" ".join(segments), segments=all_segment_data
                )
            return None

        except Exception as e:
            print(f"An error occurred during long audio processing: {str(e)}")
            return None


def main() -> None:
    resources_path = os.path.join(find_project_root(__file__), "resources")
    output_path = os.path.join(find_project_root(__file__), "output")
    sample_file_name = "sample.mp3"
    sample_file = os.path.join(resources_path, sample_file_name)
    # Initialize transcriber with model settings
    transcriber = AudioTranscriber(model_size="small", language="en")

    # Transcribe with file output
    result = transcriber.transcribe_audio(
        audio_path=sample_file,
        output_dir=output_path,
        output_filename="sample_transcription",
        save_formats=["txt", "srt"],
    )

    if result:
        print(f"\n\nTranscription text: {result.text}")
        print(f"\n\nSaved files: {result.output_files}")

        # Access specific file path
        txt_path = result.output_files.get("txt")
        if txt_path:
            with open(txt_path, "r") as f:
                print(f"\n\nContent of txt file: {f.read()}")


if __name__ == "__main__":
    main()
