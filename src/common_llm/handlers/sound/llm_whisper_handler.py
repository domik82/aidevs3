from __future__ import annotations

import os
from typing import List, Optional, Dict, Any

import whisper
from whisper.utils import get_writer
from whisper import Whisper
from pydub import AudioSegment

from src.tools.find_project_root import find_project_root


class TranscriptionResult:
    def __init__(self, text: str, segments: List[Dict[str, Any]]) -> None:
        self.text = text
        self.segments = segments

    def __str__(self) -> str:
        return self.text


class AudioTranscriber:
    def __init__(
        self,
        model_size: str = "base",
        language: str = "en",
        output_dir: Optional[str] = None,
    ) -> None:
        self.model: Whisper = whisper.load_model(model_size)
        self.language = language
        self.output_dir = output_dir or os.path.join(os.getcwd(), "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def transcribe_audio(
        self,
        audio_path: str,
        save_formats: Optional[List[str]] = None,
        prefix: Optional[str] = "transcription",
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe an audio file and optionally save in specified formats.

        Args:
            audio_path: Path to the audio file
            save_formats: List of format types to save (e.g., ["txt", "srt", "vtt"])
            prefix: specify a prefix to use when saving the file
        Returns:
            TranscriptionResult object or None if transcription fails

        """
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            result = self.model.transcribe(
                audio=audio_path, language=self.language, verbose=True
            )

            if save_formats:
                self._save_transcription(result, save_formats, prefix)

            return TranscriptionResult(result["text"], result["segments"])

        except Exception as e:
            print(f"An error occurred during transcription: {str(e)}")
            return None

    def _save_transcription(
        self, result: Dict[str, Any], formats: List[str], prefix: str = "transcription"
    ) -> None:
        """Save transcription results in specified formats.
        :param prefix:
        """
        for format_type in formats:
            writer = get_writer(format_type, self.output_dir)

            output_file = os.path.join(self.output_dir, f"{prefix}.{format_type}")
            writer(result, output_file)

    def process_long_audio(
        self, audio_path: str, segment_length_minutes: int = 10
    ) -> Optional[str]:
        """
        Process long audio files by splitting them into segments.

        Args:
            audio_path: Path to the audio file
            segment_length_minutes: Length of each segment in minutes

        Returns:
            Combined transcription text or None if processing fails
        """
        try:
            temp_file = os.path.join(self.output_dir, "temp_segment.mp3")
            audio = AudioSegment.from_mp3(audio_path)

            segment_length = (
                segment_length_minutes * 60 * 1000
            )  # Convert to milliseconds
            segments: List[str] = []

            for start in range(0, len(audio), segment_length):
                segment = audio[start : start + segment_length]
                segment.export(temp_file, format="mp3")

                result = self.transcribe_audio(temp_file)
                if result:
                    segments.append(result.text)

            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)

            return " ".join(segments) if segments else None

        except Exception as e:
            print(f"An error occurred during long audio processing: {str(e)}")
            return None


def main() -> None:
    resources_path = os.path.join(find_project_root(__file__), "resources")
    output_path = os.path.join(find_project_root(__file__), "output")
    sample_file_name = "sample.mp3"
    sample_file = os.path.join(resources_path, sample_file_name)

    transcriber = AudioTranscriber(
        model_size="large", language="en", output_dir=output_path
    )

    # Single file transcription with multiple output formats
    result = transcriber.transcribe_audio(
        audio_path=sample_file,
        save_formats=["txt", "srt", "vtt"],
        prefix="sample_transcription",
    )

    if result:
        print("Transcription result:", result)
    else:
        print("Transcription failed")


if __name__ == "__main__":
    main()
