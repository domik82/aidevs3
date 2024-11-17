import os

from src.common_aidevs.files_read_write_download import build_filename, read_file
from src.common_llm.handlers.sound.llm_whisper_handler import AudioTranscriber


def convert_mp3_to_txt(
    file_path="", output_dir="", prefix="", suffix="", overwrite=False, language="en"
):
    print(f"Convert mp3 to txt for: {file_path}")

    save_format = "txt"
    # Get filename with extension
    filename = os.path.basename(file_path)
    # Get filename without extension
    filename_no_ext = os.path.splitext(os.path.basename(filename))[0]
    output_file_pattern = build_filename(filename_no_ext, prefix, suffix)
    if output_dir == "":
        output_dir = os.getcwd()

    # Check if output dir exists and create it otherwise
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get output file path with extension
    save_file_path = os.path.join(output_dir, f"{output_file_pattern}.{save_format}")

    if os.path.exists(save_file_path):
        if overwrite is True:
            os.remove(save_file_path)
        else:
            return read_file(save_file_path)

    # Initialize transcriber with model settings
    transcriber = AudioTranscriber(model_size="large", language=language)

    # Transcribe with file output
    result = transcriber.transcribe_audio(
        audio_path=file_path,
        output_dir=output_dir,
        output_filename=output_file_pattern,
        save_formats=[save_format],
    )

    if result:
        print("\nTranscription:\n", result.text)
        return result.text
    else:
        print("Transcription failed")
