import asyncio
import logging
import random

from tasks.S04E01.data_processor import ImageProcessor, ImageStatus


async def single_image_example():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S"
    )

    processor = ImageProcessor(max_workers=1)
    await processor.start()

    # 1. Load initial image
    initial_image = "IMG_559.PNG"
    await processor.add_image(initial_image)
    await asyncio.sleep(0.5)

    # 2. Add description for initial image
    await processor.add_description(
        initial_image,
        "Image is corrupted and needs to be fixed. <action>REPAIR</action>",
    )
    await asyncio.sleep(0.5)

    # 3. Instead of letting it process automatically, add manual fix
    external_image = "IMG_559_MANUAL_FIX.PNG"
    await processor.add_processed_image(initial_image, external_image)
    await asyncio.sleep(1.5)

    # 4. Add description for manual fix
    await processor.add_description(
        external_image,
        "Image is too bright and needs to be darkened a bit. <action>DARKEN</action>",
    )
    await asyncio.sleep(1.5)

    # 5. Let the final processing happen automatically
    final_image = next(
        path
        for path, img in processor.images.items()
        if img.parent_image == external_image
    )
    await processor.add_description(
        final_image, "Image looks good, no further processing needed"
    )
    await asyncio.sleep(1.5)

    # Print final status of all images
    print("\nFinal Image Statuses:")
    for path, image in processor.images.items():
        print(f"\nImage: {path}")
        print(f"Status: {image.status.value}")
        print(f"Description: {image.description}")
        print(f"Tool: {image.required_tool.value}")
        print(f"Parent: {image.parent_image}")

    await processor.queue.join()
    await processor.stop()


async def process_multiple_images():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S"
    )

    processor = ImageProcessor(max_workers=3)
    await processor.start()

    descriptions = [
        "Image is corrupted and needs to be fixed",
        "Image is too bright and needs to be darkened a bit",
        "Image is too dark and needs to be brighted up",
        "Image is ok",
        "",
    ]

    initial_images = [f"IMG_{i:03d}.PNG" for i in range(1, 11)]

    for img in initial_images:
        await processor.add_image(img)

    async def process_single_image(image_path: str):
        description = random.choice(descriptions)
        if description:
            await processor.add_description(image_path, description)

            # Add external image injection for IMG_001.PNG
            if image_path == "IMG_001.PNG" and "corrupted" in description.lower():
                external_image = f"{image_path.split('.')[0]}_MANUAL_FIX.PNG"
                await processor.add_processed_image(image_path, external_image)
                await processor.add_description(
                    external_image,
                    random.choice([desc for desc in descriptions if desc]),
                )

        while True:
            child_images = [
                path
                for path, img in processor.images.items()
                if img.parent_image == image_path
            ]

            if child_images:
                for child in child_images:
                    if processor.images[child].status == ImageStatus.NEEDS_ASSESSMENT:
                        new_description = random.choice(descriptions)
                        if new_description:
                            await processor.add_description(child, new_description)

            if all(
                processor.images[img].status
                in [ImageStatus.FINAL, ImageStatus.PROCESSED]
                for img in [image_path] + child_images
            ):
                break

            await asyncio.sleep(0.5)

    tasks = [process_single_image(img) for img in initial_images]
    await asyncio.gather(*tasks)
    await processor.queue.join()

    # For multiple images version:
    print("\nFinal Image Statuses:")
    print("\nOriginal Images:")
    for path, image in processor.images.items():
        if not image.parent_image:  # Original images
            print(f"\nImage: {path}")
            print(f"Status: {image.status.value}")
            print(f"Description: {image.description}")
            print(f"Tool: {image.required_tool.value}")

    print("\nProcessed Images:")
    for path, image in processor.images.items():
        if image.parent_image:  # Processed images
            print(f"\nImage: {path}")
            print(f"Status: {image.status.value}")
            print(f"Description: {image.description}")
            print(f"Tool: {image.required_tool.value}")
            print(f"Parent: {image.parent_image}")

    await processor.stop()


async def main():
    # Run single image example
    print("=== Single Image Processing Example START === \n\n")
    await asyncio.sleep(1)  # Non-blocking sleep
    await single_image_example()
    print("=== Single Image Processing Example END === \n\n")
    await asyncio.sleep(1)  # Non-blocking sleep

    # Add proper async sleep
    print("Pausing between examples...\n")
    await asyncio.sleep(1)  # Non-blocking sleep

    print("\n=== Multiple Images Processing Example START === \n\n")
    await asyncio.sleep(1)  # Non-blocking sleep
    await process_multiple_images()
    print("\n=== Multiple Images Processing Example END === \n\n")


if __name__ == "__main__":
    asyncio.run(main())
