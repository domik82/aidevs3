import os
from dotenv import load_dotenv
from icecream import ic

from common.files_read_write_download import download_file

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")


def main():
    dl_url = f"{AI_DEVS_CENTRALA_ADDRESS}/data/{AI_DEVS_CENTRALA_TOKEN}/robotid.json"
    success: bool = download_file(dl_url, retries=5, timeout=10)
    ic(success)


if __name__ == "__main__":
    main()
