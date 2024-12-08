import asyncio
import logging
import os
import shutil
from pathlib import Path

from src.common_aidevs.files_read_write_download import read_txt_file, save_file
from tasks.S04E01.data_processor import ImageProcessor, ImageStatus
from tasks.S04E01.task import (
    get_photo_details,
    extract_and_download_images,
    describe_barbara,
)


async def process_multiple_images():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S"
    )

    processor = ImageProcessor(max_workers=1)
    await processor.start()

    # Get initial images
    response = get_photo_details("START")
    initial_images = extract_and_download_images(response["message"])

    # Add initial images
    for img in initial_images:
        await processor.add_image(img)

    # Wait for all processing to complete
    await processor.queue.join()
    await processor.stop()

    # Collect final images
    final_images = [
        path
        for path, image in processor.images.items()
        if image.status == ImageStatus.FINAL
    ]

    # Print final status of all images
    print("\nFinal Image Statuses:")
    print("\nOriginal Images:")
    for path, image in processor.images.items():
        if not image.parent_image:
            print(f"\nImage: {path}")
            print(f"Status: {image.status.value}")
            print(f"Description: {image.description}")
            print(f"Tool: {image.required_tool.value}")

    print("\nProcessed Images:")
    for path, image in processor.images.items():
        if image.parent_image:
            print(f"\nImage: {path}")
            print(f"Status: {image.status.value}")
            print(f"Description: {image.description}")
            print(f"Tool: {image.required_tool.value}")
            print(f"Parent: {image.parent_image}")

    print("\nFinal Images:")
    for path in final_images:
        print(f"- {path}")

    return final_images


def copy_final_images(final_images: list, destination_folder: str):
    """Copy all final images to the specified destination folder"""

    # Create destination directory if it doesn't exist
    Path(destination_folder).mkdir(parents=True, exist_ok=True)

    for image_path in final_images:
        # Get the filename from the path
        filename = os.path.basename(image_path)
        # Create destination path
        destination_path = os.path.join(destination_folder, filename)

        try:
            shutil.copy2(image_path, destination_path)
            print(f"Copied {filename} to {destination_folder}")
        except FileNotFoundError:
            print(f"Source file not found: {image_path}")
        except Exception as e:
            print(f"Error copying {filename}: {str(e)}")


async def main():
    # Run single image example
    print("=== process_multiple_images START === \n\n")
    final_folder = "final_images"
    await asyncio.sleep(1)  # Non-blocking sleep
    # final_image_list = await process_multiple_images()
    # copy_final_images(final_image_list, final_folder)
    # description = ""
    base_path = os.getcwd()
    images_path = os.path.join(base_path, final_folder)
    # for image_file in os.listdir(images_path):
    #     if '.png' in image_file.lower():
    #         img_file = os.path.join(images_path, image_file)
    #         description = description + describe_barbara_images(images_path, img_file)

    final_description = ""
    for image_file in os.listdir(images_path):
        if ".txt" in image_file.lower():
            img_description = read_txt_file(os.path.join(images_path, image_file))

            final_description = (
                final_description + "\n\n" + f"{image_file}" + "\n\n" + img_description
            )

    barbara_description = describe_barbara(final_description)
    print(f"barbara_description {barbara_description}")

    save_file(barbara_description, os.path.join(base_path, "barbara_description.txt"))

    print("=== process_multiple_images END === \n\n")
    await asyncio.sleep(1)  # Non-blocking sleep

    # Add proper async sleep
    print("Pausing between examples...\n")
    await asyncio.sleep(1)  # Non-blocking sleep


if __name__ == "__main__":
    asyncio.run(main())
