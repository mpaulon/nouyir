import logging

from pathlib import Path

import requests

logger = logging.getLogger(__name__)

def get_config_from_pad(pad_url, current_time):
    logger.info(f"Downloading config from {pad_url}")
    r = requests.get(pad_url)
    configs_folder = Path("configs")
    configs_folder.mkdir(exist_ok=True, parents=True)
    with open(configs_folder / f"{current_time}.yml", "wb") as config:
        config.write(r.content)
    return configs_folder / f"{current_time}.yml"