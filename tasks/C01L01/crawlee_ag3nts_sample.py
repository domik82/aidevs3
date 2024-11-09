from queue import Queue
from crawlee.playwright_crawler import PlaywrightCrawler

import asyncio

# Create a queue to store the extracted question
question_queue = Queue()


async def handle_page(context):
    page = context.page
    # Wait for the element with id "human-question" to be visible
    await page.wait_for_selector("#human-question")

    # Extract the question text
    question_element = await page.query_selector("#human-question")
    question_text = await question_element.inner_text()

    print(f"Extracted question: {question_text}")

    # Put the extracted question into the queue
    question_queue.put(question_text)


def process_question(question):
    # This function will process the extracted question
    print(f"Processing question: {question}")
    # Add your processing logic here


async def process_site(site):
    # Configure the crawler
    # Run in headless mode
    crawler = PlaywrightCrawler()

    # Define the default request handler
    @crawler.router.default_handler
    async def default_handler(context):
        await handle_page(context)

    # Run the crawler with the target URL
    await crawler.run([site])


async def crawler_return_extracted_data(page_address):
    await process_site(page_address)
    extracted_question = None
    # After crawling is done, process the extracted question
    if not question_queue.empty():
        extracted_question = question_queue.get()

        process_question(extracted_question)
        return extracted_question


async def main():
    page_address = "https://xyz.ag3nts.org/"
    question = await crawler_return_extracted_data(page_address)
    print(f"After processing {question}")


if __name__ == "__main__":
    asyncio.run(main())
