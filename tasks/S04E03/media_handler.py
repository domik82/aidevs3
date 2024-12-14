import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any
from urllib.parse import urljoin, urlparse
import logging
import aiohttp
from crawlee.beautifulsoup_crawler import BeautifulSoupCrawlingContext

logger = logging.getLogger(__name__)


@dataclass
class MediaConfig:
    chunk_size: int = 8192
    media_elements: Dict[str, List[str]] = None

    def __post_init__(self):
        if self.media_elements is None:
            self.media_elements = {
                "img": ["src", "data-src", "srcset"],
                "audio": ["src", "data-src"],
                "source": ["src", "data-src"],
                "video": ["src", "data-src"],
            }


class MediaHandler:
    def __init__(self, crawler, config: MediaConfig = None):
        self.crawler = crawler
        self.config = config or MediaConfig()

    async def process_media(
        self, context: BeautifulSoupCrawlingContext, page_dir: Path
    ) -> None:
        tasks = []
        for tag, attributes in self.config.media_elements.items():
            elements = context.soup.find_all(tag)
            for element in elements:
                tasks.append(
                    self._handle_element(element, attributes, context, page_dir)
                )
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _handle_element(
        self,
        element: Any,
        attributes: List[str],
        context: BeautifulSoupCrawlingContext,
        page_dir: Path,
    ) -> None:
        for attr in attributes:
            url = element.get(attr)
            if not url:
                continue

            urls = self._parse_srcset(url) if attr == "srcset" else [url]
            download_tasks = [
                self._download_media(media_url, context, page_dir, element, attr)
                for media_url in urls
            ]
            await asyncio.gather(*download_tasks, return_exceptions=True)

    @staticmethod
    def _parse_srcset(srcset: str) -> List[str]:
        return [src.strip().split()[0] for src in srcset.split(",")]

    async def _download_media(
        self,
        media_url: str,
        context: BeautifulSoupCrawlingContext,
        page_dir: Path,
        element: Any,
        attr: str,
    ) -> None:
        full_url = urljoin(context.request.url, media_url)
        relative_path = self._get_relative_path(media_url)

        if not relative_path:
            return

        target_path = page_dir / relative_path
        await self._ensure_session()

        try:
            await self._download_and_save(full_url, target_path)
            if attr != "srcset":
                element[attr] = str(Path(relative_path))
        except Exception as e:
            logger.error(f"Failed to download {full_url}: {str(e)}")

    @staticmethod
    def _get_relative_path(url: str) -> str:
        return urlparse(url).path.lstrip("/")

    async def _ensure_session(self) -> None:
        if not self.crawler.session:
            self.crawler.session = aiohttp.ClientSession()

    async def _download_and_save(self, url: str, target_path: Path) -> None:
        target_path.parent.mkdir(parents=True, exist_ok=True)

        async with self.crawler.session.get(url) as response:
            if response.status != 200:
                raise ValueError(f"HTTP {response.status} for {url}")

            with open(target_path, "wb") as f:
                async for chunk in response.content.iter_chunked(
                    self.config.chunk_size
                ):
                    f.write(chunk)
