import asyncio
from time import sleep

from crawlee.beautifulsoup_crawler import (
    BeautifulSoupCrawler,
    BeautifulSoupCrawlingContext,
)

from datetime import timedelta

from crawlee.storages import RequestQueue


async def crawl_url(url: str, extract_content: bool = False):
    rq = await RequestQueue.open(name="my_rq")
    crawler = BeautifulSoupCrawler(
        max_requests_per_crawl=10,
        request_handler_timeout=timedelta(seconds=30),
        request_provider=rq,
    )

    results = []

    @crawler.router.default_handler
    async def handler(context: BeautifulSoupCrawlingContext):
        context.log.info(f"Processing {context.request.url} ...")
        print(context.session.cookies)
        result = {
            "url": context.request.url,
            "title": context.soup.title.string if context.soup.title else None,
            "links": [a["href"] for a in context.soup.find_all("a", href=True)],
        }
        print(context.session.cookies)
        if extract_content:
            result["content"] = str(context.soup)

        results.append(result)

    await crawler.run([url])
    await rq.drop()  # solution to running crawler 2x without issues
    return results


async def main():
    url = "https://softo.ag3nts.org"

    print("First crawl:")
    first_results = await crawl_url(url, extract_content=False)
    print(first_results)
    sleep(5)
    print("\nSecond crawl:")
    second_results = await crawl_url(url, extract_content=True)
    print(second_results)


if __name__ == "__main__":
    asyncio.run(main())
