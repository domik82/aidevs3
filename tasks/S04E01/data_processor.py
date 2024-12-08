import asyncio
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Dict
import logging


from tasks.S04E01.task import (
    get_photo_details,
    extract_and_download_images,
    describe_and_pick_tool,
    return_tool_based_on_description,
)


class ImageStatus(Enum):
    NEW = "NEW"
    NEEDS_ASSESSMENT = "NEEDS_ASSESSMENT"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FINAL = "FINAL"


class ProcessingTool(Enum):
    REPAIR = "REPAIR"
    DARKEN = "DARKEN"
    BRIGHTEN = "BRIGHTEN"
    NONE = "NONE"


@dataclass
class Image:
    path: str
    status: ImageStatus = ImageStatus.NEW
    description: str = ""
    required_tool: ProcessingTool = ProcessingTool.NONE
    parent_image: Optional[str] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ImageProcessor:
    def __init__(self, max_workers: int = 3):
        self.queue = asyncio.Queue()
        self.images = {}  # Storage for image metadata
        self.max_workers = max_workers
        self.workers = []
        self.logger = logging.getLogger(__name__)

    async def add_image(self, image_path: str):
        """Initial addition of new image to the system"""
        image = Image(path=image_path, status=ImageStatus.NEEDS_ASSESSMENT)
        self.images[image_path] = image
        await self.queue.put(image_path)
        self.logger.info(f"Added new image: {image_path}")

    async def assess_image(self, image_path: str):
        """Assessment of image based on its metadata and description"""
        image = self.images[image_path]
        self.logger.info(f"image {image} {image_path}")
        if image.status == ImageStatus.NEEDS_ASSESSMENT:
            await asyncio.sleep(0.5)  # Mock assessment time

            directory = os.path.dirname(image_path)
            description = describe_and_pick_tool(directory, image_path)
            needed_tool = return_tool_based_on_description(description)
            final_description = description + "\n" + needed_tool

            self.logger.info(f"image.description {description}")
            self.logger.info(f"image.required_tool {needed_tool}")

            await self.add_description(image_path, final_description)

            if not image.description:
                image.description = f"Analysis results for {image_path}"

            # Change status to PROCESSING if tool is assigned
            if image.required_tool != ProcessingTool.NONE:
                image.status = ImageStatus.PROCESSING
                await self.queue.put(image_path)
            else:
                image.status = ImageStatus.FINAL
                self.logger.info(f"Image {image_path} marked as FINAL")

    async def add_processed_image(self, original_path: str, new_image_path: str):
        """Adds externally created image to the processing system"""
        if original_path not in self.images:
            self.logger.error(f"Parent image {original_path} not found in system")
            return

        # Create new image entry with external path
        new_image = Image(
            path=new_image_path,
            status=ImageStatus.NEEDS_ASSESSMENT,
            parent_image=original_path,
        )

        # Add to image storage
        self.images[new_image_path] = new_image

        # Update parent status
        parent_image = self.images[original_path]
        parent_image.status = ImageStatus.PROCESSED

        # Put new image for assessment
        await self.queue.put(new_image_path)
        self.logger.info(f"Added external processed image: {new_image_path}")

    async def process_image(self, image_path: str):
        """Process image based on its required_tool"""
        image = self.images[image_path]

        if image.required_tool == ProcessingTool.NONE:
            return None

        # Mock processing
        await asyncio.sleep(1)

        # Generate new image name
        # fixed_image = f"{image_path.split('.')[0]}_{uuid.uuid4().hex[:4]}.PNG"
        # ask LLM what is next image
        image_name = Path(image.path).name
        query = f"{image.required_tool.value} {image_name}"
        self.logger.info(f"Executing query to centrala: {query}")
        centrala_response = get_photo_details(query)
        self.logger.info(f"centrala_response: {centrala_response}")

        img_list = extract_and_download_images(centrala_response["message"])

        self.logger.info(f"img_list: {img_list}")
        if len(img_list) == 1:
            fixed_image = img_list[0]
        else:
            return None

        # Create new image entry that needs assessment
        new_image = Image(
            path=fixed_image,
            status=ImageStatus.NEEDS_ASSESSMENT,
            parent_image=image_path,
        )

        # Update statuses
        image.status = ImageStatus.PROCESSED
        self.images[fixed_image] = new_image

        # Put new image for assessment
        await self.queue.put(fixed_image)

        return fixed_image

    async def add_description(self, image_path: str, description: str):
        """External method to add description to image"""
        if image_path in self.images:
            image = self.images[image_path]
            image.description = description
            await self.analyze_description(image_path)
            self.logger.info(f"Added description to {image_path}: {description}")

    async def analyze_description(self, image_path: str):
        """Analyzes description and automatically selects appropriate tool"""
        image = self.images[image_path]

        if "<action>repair</action>" in image.description.lower():
            image.required_tool = ProcessingTool.REPAIR
        elif "<action>darken</action>" in image.description.lower():
            image.required_tool = ProcessingTool.DARKEN
        elif "<action>brighten</action>" in image.description.lower():
            image.required_tool = ProcessingTool.BRIGHTEN
        elif "<action>none</action>" in image.description.lower():
            image.required_tool = ProcessingTool.NONE
            image.status = ImageStatus.FINAL
            self.logger.info(f"Image {image_path} marked as FINAL")
            return
        else:
            image.required_tool = ProcessingTool.NONE
            image.status = ImageStatus.FINAL
            self.logger.info(
                f"Image {image_path} marked as FINAL based on lack of tool in description"
            )
            self.logger.info(f"Image description: {image.description}")
            return

        image.status = ImageStatus.PROCESSING
        await self.queue.put(image_path)
        self.logger.info(
            f"Selected tool {image.required_tool.value} based on description"
        )

    async def worker(self, worker_id: str):
        while True:
            image_path = await self.queue.get()
            if image_path is None:
                self.queue.task_done()  # there is bug somewhere where empty item is added
                if self.queue.qsize() > 0:
                    self.logger.info(
                        f"queue.qsize() {self.queue.qsize()}, image_path {image_path} "
                    )
                    continue
                else:
                    break

            try:
                image = self.images[image_path]

                if image.status == ImageStatus.NEEDS_ASSESSMENT:
                    self.logger.info(f"[{worker_id}] Assessing: {image_path}")
                    await self.assess_image(image_path)

                elif image.status == ImageStatus.PROCESSING:
                    self.logger.info(
                        f"[{worker_id}] Processing: {image_path} with {image.required_tool.value}"
                    )
                    new_image_path = await self.process_image(image_path)
                    if new_image_path:
                        self.logger.info(f"Created new image: {new_image_path}")

            except Exception as e:
                self.logger.error(f"Error in {worker_id}: {e}")
            finally:
                self.queue.task_done()

    async def start(self):
        self.workers = [
            asyncio.create_task(self.worker(f"worker-{i}"))
            for i in range(self.max_workers)
        ]

    async def stop(self):
        self.logger.info("Initiating stop sequence")

        # Wait for queue to be empty and all processing to complete
        await self.queue.join()

        # Now we can safely stop the workers
        for _ in range(self.max_workers):
            await self.queue.put(None)

        if self.workers:
            await asyncio.gather(*self.workers)

        self.logger.info("All workers stopped")

    async def update_image_tool(self, image_path: str, tool: ProcessingTool):
        """External method to update image processing requirements"""
        if image_path in self.images:
            image = self.images[image_path]
            image.required_tool = tool
            if image.status == ImageStatus.NEEDS_ASSESSMENT:
                await self.queue.put(image_path)
                self.logger.info(f"Updated {image_path} with tool {tool.value}")
