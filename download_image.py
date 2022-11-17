import os

from urllib.parse import urlsplit

import requests


def download_image(url, filename, payload=None):
    response = requests.get(url, params=payload)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)


def get_filename(url):
    url = urlsplit(url)
    image_folder, image_name = os.path.split(url.path)

    return image_name