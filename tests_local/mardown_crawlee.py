import asyncio
from datetime import datetime, timedelta
from crawlee.beautifulsoup_crawler import (
    BeautifulSoupCrawler,
    BeautifulSoupCrawlingContext,
)
from urllib.parse import urljoin, urlparse
from pathlib import Path
import aiohttp
from markdownify import markdownify as md

from pathvalidate import sanitize_filename


def url_to_foldername(url: str, max_length: int = 50) -> str:
    """Convert URL to a valid folder name"""
    parsed = urlparse(url)
    # Combine domain and path, remove common extensions
    name_parts = []

    # Add domain without TLD
    domain = parsed.netloc.split(":")[0]  # Remove port if present
    domain = domain.split(".")[:-1]  # Remove TLD
    name_parts.extend(domain)

    # Add path parts
    path = parsed.path.strip("/")
    if path:
        # Remove common file extensions
        path = path.replace(".html", "").replace(".htm", "")
        path_parts = path.split("/")
        name_parts.extend(path_parts)

    # Join parts with underscores
    folder_name = "_".join(name_parts)

    # Sanitize and limit length
    folder_name = sanitize_filename(folder_name)

    # Truncate if too long, but keep the last part
    if len(folder_name) > max_length:
        folder_name = folder_name[: max_length - 3] + "..."

    return folder_name or "index"  # fallback to 'index' if empty


class WebCrawler:
    def __init__(self):
        self.output_dir = Path("./output")
        self.folders = {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico"],
            "audio": [".mp3", ".wav", ".ogg", ".m4a", ".aac"],
            "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".html", ".md"],
            "videos": [".mp4", ".webm", ".avi"],
            "other": [],
        }
        self.setup_folders()
        self.session = None

    def setup_folders(self):
        for folder in self.folders:
            folder_path = self.output_dir / folder
            folder_path.mkdir(parents=True, exist_ok=True)

    def html_to_markdown(
        self,
        html_content: str,
        title: str = None,
        url: str = None,
        base_path: Path = None,
    ) -> str:
        """Convert HTML to Markdown maintaining relative paths"""
        try:
            # Convert HTML to Markdown
            markdown_content = md(html_content, heading_style="ATX", bullets="*")

            # Add metadata
            metadata = "---\n"
            if title:
                metadata += f"title: {title}\n"
            if url:
                metadata += f"url: {url}\n"
            metadata += f"date: {datetime.now().isoformat()}\n"
            metadata += "---\n\n"

            return metadata + markdown_content
        except Exception as e:
            print(f"Failed to convert HTML to Markdown: {str(e)}")
            return None

    async def download_file(self, url: str, target_path: Path) -> None:
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return

                # Create parent directories if they don't exist
                target_path.parent.mkdir(parents=True, exist_ok=True)

                with open(target_path, "wb") as f:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)

        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")

    async def run(self, start_url: str):
        crawler = BeautifulSoupCrawler(
            max_request_retries=3,
            request_handler_timeout=timedelta(seconds=30),
            max_requests_per_crawl=50,
        )

        @crawler.router.default_handler
        async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
            context.log.info(f"Processing {context.request.url} ...")

            # Generate readable folder name from URL
            base_filename = url_to_foldername(context.request.url)

            # Create document directory for this page
            page_dir = self.output_dir / "documents" / base_filename
            page_dir.mkdir(parents=True, exist_ok=True)

            # Save HTML version
            html_path = page_dir / "index.html"
            html_content = str(context.soup)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Process media elements before creating markdown
            media_elements = {
                "img": ["src", "data-src", "srcset"],
                "audio": ["src", "data-src"],
                "source": ["src", "data-src"],
                "video": ["src", "data-src"],
            }

            for tag, attributes in media_elements.items():
                for element in context.soup.find_all(tag):
                    for attr in attributes:
                        url = element.get(attr)
                        if not url:
                            continue

                        if attr == "srcset":
                            urls = [src.strip().split()[0] for src in url.split(",")]
                        else:
                            urls = [url]

                        for media_url in urls:
                            full_url = urljoin(context.request.url, media_url)
                            parsed_url = urlparse(media_url)

                            # Maintain original path structure
                            relative_path = parsed_url.path.lstrip("/")
                            if not relative_path:
                                continue

                            # Create target path maintaining original structure
                            target_path = page_dir / relative_path

                            # Download the file
                            await self.download_file(full_url, target_path)

                            # Update element's source to use relative path
                            if attr != "srcset":
                                element[attr] = str(Path(relative_path))

            # Convert and save Markdown version with updated paths
            title = context.soup.title.string if context.soup.title else "Untitled"
            markdown_content = self.html_to_markdown(
                str(context.soup),
                title=title,
                url=context.request.url,
                base_path=page_dir,
            )

            if markdown_content:
                md_path = page_dir / "index.md"
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)

            await context.push_data(
                {
                    "url": context.request.url,
                    "title": title,
                    "text_content": context.soup.get_text(strip=True),
                }
            )

        try:
            await crawler.run([start_url])
        finally:
            if self.session:
                await self.session.close()


# Usage in the crawler:
# Replace:
# url_hash = hashlib.md5(context.request.url.encode()).hexdigest()[:8]
# base_filename = f'page_{url_hash}'

# With:
# base_filename = url_to_foldername(context.request.url)


async def main():
    crawler = WebCrawler()
    await crawler.run("https://centrala.ag3nts.org/dane/arxiv-draft.html")


if __name__ == "__main__":
    asyncio.run(main())
