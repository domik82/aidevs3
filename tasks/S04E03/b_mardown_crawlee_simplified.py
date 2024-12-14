"""
Web Crawler Module
A high-performance asynchronous web crawler that downloads and processes web content,
including media files, and converts pages to markdown format.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

import aiohttp
from crawlee import Request
from crawlee.beautifulsoup_crawler import (
    BeautifulSoupCrawler,
    BeautifulSoupCrawlingContext,
)
from urllib.parse import urljoin, urlparse

from media_handler import MediaHandler, MediaConfig
from crawler_file_handler import CrawlerFileHandler

from utils import url_to_foldername, html_to_markdown

from dataclasses import dataclass
from typing import List


logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    url: str
    links: List[str]
    content: Optional[str] = None
    title: Optional[str] = None


class SpecializedWebCrawler:
    """
    Asynchronous web crawler that processes web pages, downloads media, and saves content
    in both HTML and Markdown formats.

    Attributes:
        output_dir (Path): Directory for storing crawled content
        max_depth (int): Maximum depth for recursive crawling
        session (Optional[aiohttp.ClientSession]): Async HTTP session
        visited_urls (Set[str]): Set of processed URLs to avoid duplicates
    """

    def __init__(
        self,
        max_depth: int = 5,
        output_dir: str = "./output",
        save_to_disk: bool = True,
    ):
        """
        Initialize the WebCrawler with configuration parameters.

        Args:
            max_depth: Maximum crawling depth (default: 5)
            output_dir: Base directory for output files (default: "./output")
        """
        self.output_dir = Path(output_dir)
        self.max_depth = max_depth
        self.session: Optional[aiohttp.ClientSession] = None
        # Initialize empty sets for each instance
        self.visited_urls = set()
        self.crawl_results = []
        self.media_config = MediaConfig()
        self.media_handler = MediaHandler(self, self.media_config)
        self.file_handler = CrawlerFileHandler(self.output_dir)
        self.save_to_disk = save_to_disk
        if save_to_disk:
            self._initialize_storage()

    def _initialize_storage(self) -> None:
        """Create necessary directory structure for storing crawled content."""
        storage_dirs = ["images", "audio", "documents", "videos", "other"]
        for folder in storage_dirs:
            (self.output_dir / folder).mkdir(parents=True, exist_ok=True)

    async def run(
        self, start_url: str, extract_content: bool = False
    ) -> List[CrawlResult]:
        """
        Start the crawling process from a given URL.

        Args:
            start_url: Initial URL to begin crawling
            extract_content: If True, extracts and returns page content as markdown

        Returns:
            List[CrawlResult]: List of crawl results containing URLs and optionally content
        """
        print("run")
        self.visited_urls.clear()
        self.crawl_results.clear()

        async with aiohttp.ClientSession() as self.session:
            crawler = self._setup_crawler(extract_content)
            await crawler.run([start_url])

            rq = await crawler.get_request_provider()
            await rq.drop()  # Clean storage so that second execution would work
            return self.crawl_results

    def _setup_crawler(self, extract_content: bool) -> BeautifulSoupCrawler:
        """
        Configure and return a BeautifulSoupCrawler instance with custom settings.

        Returns:
            BeautifulSoupCrawler: Configured crawler instance
        """
        crawler = BeautifulSoupCrawler(
            max_request_retries=3,
            request_handler_timeout=timedelta(seconds=30),
            max_requests_per_crawl=1000,
        )
        print("_setup_crawler")

        @crawler.router.default_handler
        async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
            print("request_handler")
            if context.request.url in self.visited_urls:
                return

            self.visited_urls.add(context.request.url)
            context.log.info(f"Processing {context.request.url} ...")

            # Extract links
            base_url = context.request.url
            base_domain = urlparse(base_url).netloc
            links = context.soup.find_all("a", href=True)
            extracted_links = [
                urljoin(base_url, link["href"])
                for link in links
                if self._is_valid_link(urljoin(base_url, link["href"]), base_domain)
            ]

            # Create crawl result
            result = CrawlResult(
                url=context.request.url,
                links=extracted_links,
                title=context.soup.title.string if context.soup.title else "Untitled",
            )

            # Extract content if requested
            if extract_content:
                html_content = str(context.soup)
                metadata = {
                    "title": result.title,
                    "url": context.request.url,
                    "date": datetime.now().isoformat(),
                }
                result.content = html_to_markdown(html_content, metadata)

            self.crawl_results.append(result)

            # Continue crawling if within depth limit
            current_depth = context.request.user_data.get("depth", 0)
            if current_depth < self.max_depth:
                await self._process_links(context, current_depth)

            # Save to disk if enabled
            if self.save_to_disk:
                await self._process_page_content(context)
                await self._track_page_data(context)

        return crawler

    async def _process_links(
        self, context: BeautifulSoupCrawlingContext, current_depth: int
    ) -> None:
        """
        Extract and process links from the current page.

        Args:
            context: Current crawling context
            current_depth: Current crawling depth
        """
        base_url = context.request.url
        base_domain = urlparse(base_url).netloc
        links = context.soup.find_all("a", href=True)

        requests = [
            Request.from_url(
                url=urljoin(base_url, link["href"]),
                user_data={"depth": current_depth + 1},
            )
            for link in links
            if self._is_valid_link(urljoin(base_url, link["href"]), base_domain)
        ]

        if requests:
            await context.add_requests(requests)

    def _is_valid_link(self, absolute_url: str, base_domain: str) -> bool:
        return (
            absolute_url not in self.visited_urls
            and urlparse(absolute_url).netloc == base_domain
        )

    async def _process_page_content(self, context: BeautifulSoupCrawlingContext):
        base_filename = url_to_foldername(context.request.url)
        page_dir = self.output_dir / "documents" / base_filename
        page_dir.mkdir(parents=True, exist_ok=True)

        # Save HTML
        html_content = str(context.soup)
        self.file_handler.save_html(html_content, page_dir)

        # Process media
        await self.media_handler.process_media(context, page_dir)

        # Save Markdown with proper error handling
        try:
            title = context.soup.title.string if context.soup.title else "Untitled"
            metadata = {
                "title": title,
                "url": context.request.url,
                "date": datetime.now().isoformat(),
            }
            markdown_content = html_to_markdown(html_content, metadata)
            if markdown_content:
                self.file_handler.save_markdown(markdown_content, page_dir)
        except Exception as e:
            logging.error(
                f"Failed to save markdown for {context.request.url}: {str(e)}"
            )

    async def _track_page_data(self, context: BeautifulSoupCrawlingContext) -> None:
        """
        Track crawled page metadata.

        Args:
            context: Current crawling context
        """
        await context.push_data(
            {
                "url": context.request.url,
                "title": context.soup.title.string
                if context.soup.title
                else "Untitled",
                "text_content": context.soup.get_text(strip=True),
                "timestamp": datetime.now().isoformat(),
            }
        )


def write_jsonl(filename, data):
    with open(filename, "w") as f:
        json_line = json.dumps(data, ensure_ascii=True, indent=4)
        f.write(json_line + "\n")


async def main():
    url = "https://softo.ag3nts.org"

    # First crawl
    crawler1 = SpecializedWebCrawler(max_depth=0, save_to_disk=True)
    results1 = await crawler1.run(url, extract_content=True)
    print("First crawl results:", results1)

    # Second crawl - Create completely new crawler instance
    crawler2 = SpecializedWebCrawler(max_depth=1, save_to_disk=False)
    # Create new session
    results2 = await crawler2.run(url, extract_content=True)
    # Convert results to JSON
    json_results = [
        {
            "url": result.url,
            "title": result.title,
            "links": result.links,
            "content": result.content,
        }
        for result in results2
    ]

    write_jsonl("dumps.json", json_results)
    print("Second crawl results:", json_results)


if __name__ == "__main__":
    asyncio.run(main())
