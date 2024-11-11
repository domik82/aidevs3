import os
import time
from datetime import datetime

from dotenv import load_dotenv
from icecream import ic

from common.files_read_write_download import download_file

load_dotenv()
AI_DEVS_CENTRALA_ADDRESS = os.getenv("AI_DEVS_CENTRALA_ADDRESS")
AI_DEVS_CENTRALA_TOKEN = os.getenv("AI_DEVS_CENTRALA_TOKEN")


def main():
    dl_url = f"{AI_DEVS_CENTRALA_ADDRESS}/data/{AI_DEVS_CENTRALA_TOKEN}/cenzura.txt"
    counter = 0
    while True:
        counter += 1
        timestamp_ms = int(datetime.now().timestamp() * 1000)
        filename_ts = f"cenzura_{timestamp_ms}.txt"
        success: bool = download_file(
            dl_url, retries=5, timeout=10, file_name=filename_ts
        )
        ic(success)

        if counter >= 10:
            break
        time.sleep(60)


if __name__ == "__main__":
    main()
