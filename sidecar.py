import logging
import requests
import time


class Sidecar:
    def __init__(self, node_name):
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(filename=f"{node_name}.log", level=logging.INFO,
                                format='%(asctime)s - %(levelname)s - %(message)s')

    def send(self, url, data, retries=3, delay=1):

        for attempt in range(retries):
            try:
                logging.info(f"Sending to {url}: {data}")
                response = requests.post(url, json=data)
                response.raise_for_status()
                logging.info(f"Response: {response.status_code}")
                return response
            except requests.RequestException as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)

        logging.error(f"All {retries} attempts failed for {url}")
        return None