from markdown_crawler import md_crawl

url = "https://centrala.ag3nts.org/dane/arxiv-draft.html"
md_crawl(url, max_depth=3, num_threads=5, base_dir="markdown")

# failure


#   File "....\Lib\site-packages\markdown_crawler\__init__.py", line 255, in worker
#     child_urls = crawl(
#                  ^^^^^^
#   File ""....\Lib\site-packages\markdown_crawler\__init__.py", line 141, in crawl
#     f.write(output)
#   File "...\Python311\Lib\encodings\cp1250.py", line 19, in encode
#     return codecs.charmap_encode(input,self.errors,encoding_table)[0]
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# UnicodeEncodeError: 'charmap' codec can't encode characters in position 1640-1810: character maps to <undefined>
# INFO:markdown_crawler:🏁 All threads have finished

# from markdown_crawler import md_crawl
# url = 'https://rickandmorty.fandom.com/wiki/Evil_Morty'
# print(f'🕸️ Starting crawl of {url}')
# md_crawl(
#     url,
#     max_depth=3,
#     num_threads=5,
#     base_dir='markdown',
#     valid_paths=['/wiki'],
#     target_content=['div#content'],
#     is_domain_match=True,
#     is_base_path_match=False,
#     is_debug=True
# )

# max_depth to 3. We will crawl the base URL and 3 levels of children
# num_threads to 5. We will use 5 parallel(ish) threads to crawl the website
# base_dir to markdown. We will save the markdown files in the markdown directory
# valid_paths an array of valid relative URL paths. We will only crawl pages that are in this list and base path
# target_content to div#content. We will only crawl pages that have this HTML element using CSS target selectors. You can provide multiple and it will concatenate the results
# is_domain_match to False. We will only crawl pages that are in the same domain as the base URL
# is_base_path_match to False. We will include all URLs in the same domain, even if they don't begin with the base url
# is_debug to True. We will print out verbose logging
