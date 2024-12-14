import os

from emmetify import Emmetifier
import requests
from crawler_file_handler import CrawlerFileHandler

emmetifier = Emmetifier()
html = requests.get("https://softo.ag3nts.org").text
emmet = emmetifier.emmetify(html)
print(emmet)
path = os.getcwd()
cr = CrawlerFileHandler("./")
cr.save_html(emmet["result"], None)
