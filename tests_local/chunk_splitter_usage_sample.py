import os
import json
import asyncio
from typing import List, TypedDict

from tabulate import tabulate

from src.tools.find_project_root import find_project_root
from src.tools.text_splitter import TextSplitter


class Report(TypedDict):
    file: str
    avgChunkSize: str
    medianChunkSize: int
    minChunkSize: int
    maxChunkSize: int
    totalChunks: int


async def process_file(file_path: str) -> Report:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Initialize splitter and process text
    splitter = TextSplitter()
    chunks = await splitter.split(text, 1000)

    # Save output
    output_filename = f"output_{os.path.basename(file_path).split('.')[0]}_chunks.json"
    output_path = os.path.join(os.path.dirname(file_path), output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    # Calculate statistics
    chunk_sizes = [chunk["metadata"]["tokens"] for chunk in chunks]
    avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
    min_chunk_size = min(chunk_sizes) if chunk_sizes else 0
    max_chunk_size = max(chunk_sizes) if chunk_sizes else 0
    sorted_sizes = sorted(chunk_sizes)
    median_chunk_size = sorted_sizes[len(sorted_sizes) // 2] if chunk_sizes else 0

    return {
        "file": os.path.basename(file_path),
        "avgChunkSize": f"{avg_chunk_size:.2f}",
        "medianChunkSize": median_chunk_size,
        "minChunkSize": min_chunk_size,
        "maxChunkSize": max_chunk_size,
        "totalChunks": len(chunk_sizes),
    }


async def main() -> None:
    # List of files to process
    files = [
        "resources/text_splitter/example_article.md",
        "resources/text_splitter/lorem_ipsum.md",
        "resources/text_splitter/youtube_transcript.md",
    ]

    reports: List[Report] = []
    base_path = find_project_root(__file__)
    print(f"\n\n base_path in: {base_path}")

    for file_path in files:
        try:
            process_file_path = os.path.join(base_path, file_path)
            print(process_file_path)
            print(f"\nProcessing: {process_file_path}")
            report = await process_file(process_file_path)
            reports.append(report)
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

    # Display results
    if reports:
        print("\nProcessing Results:")
        headers = reports[0].keys() if reports else []
        rows = [report.values() for report in reports]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

        # Save summary report
        summary_path = os.path.join(
            base_path, "resources", "text_splitter", "processing_summary.json"
        )
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(reports, f, indent=2)
        print(f"\nSummary saved to: {summary_path}")


if __name__ == "__main__":
    asyncio.run(main())
