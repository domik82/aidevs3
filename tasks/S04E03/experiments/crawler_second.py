import asyncio
from crawlee.beautifulsoup_crawler import (
    BeautifulSoupCrawler,
    BeautifulSoupCrawlingContext,
)


async def main() -> None:
    # initialize the crawler
    crawler = BeautifulSoupCrawler()

    # define how to handle each request's response
    @crawler.router.default_handler
    async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
        url = context.request.url
        context.log.info(f"\nCrawling URL: {url}")

        # Extract Info from Blog Links
        blog_link_els = context.soup.select("#content>div a.shadow-card")
        context.log.info(f"Found {len(blog_link_els)} Blogs")
        for el in blog_link_els:
            await context.push_data(
                {
                    "url": el.get("href"),
                    "title": el.select_one("h4").text,
                    "author": el.select_one("strong").text,
                    "date": el.select_one("time").get("datetime"),
                }
            )

        # Add more pages to the queue
        await context.enqueue_links(selector="ul.paging a")

    # Start the crawler with a URL
    await crawler.run(["https://www.scrapingbee.com/blog/"])


if __name__ == "__main__":
    asyncio.run(main())
