import os
import logging
import time

from random import randrange
from urllib.parse import urljoin

from download_image import download_image, get_filename

import requests

from environs import Env


IMG_URL = 'https://xkcd.com/'

VK_URL = 'https://api.vk.com/method/'

VK_VERSION = '5.131'


def get_random_comic_url(url):
    current_comic = 'info.0.json'
    current_url = urljoin(url, current_comic)
    response = requests.get(current_url)
    response.raise_for_status()

    response_content = response.json()

    count_comic = response_content['num']

    random_number = randrange(1, count_comic + 1)
    
    prefix = f'{random_number}/info.0.json'

    rand_url = urljoin(url, prefix)

    return rand_url


def get_comic_content(url):
    response = requests.get(url)
    response.raise_for_status()

    response_content = response.json()

    return response_content


def fetch_vk_server_url(url, payload):
    method = 'photos.getWallUploadServer'
    vk_url = urljoin(url, method)

    response = requests.get(vk_url, params=payload)
    response.raise_for_status()

    response_content = response.json()

    server_url = response_content['response']['upload_url']

    return server_url


def download_image_vk_server(url, filename):
    with open(filename, 'rb') as file:
        files = {
            'photo': file,
        }

    response = requests.post(url, files=files)
    response.raise_for_status()

    server_response = response.json()

    return server_response


def save_image_vk_server(url, payload, download_serv):
    method = 'photos.saveWallPhoto'
    server_payload = {
        'photo': download_serv['photo'],
        'server': download_serv['server'],
        'hash': download_serv['hash'],
    }

    data = payload | server_payload

    url = urljoin(url, method)

    response = requests.post(url, data=data)
    response.raise_for_status()

    server_response = response.json()

    response_content = server_response['response'][0]

    return response_content


def post_image_vk_group(url, payload, response_content):
    method = 'wall.post'
    
    owner_id = response_content['owner_id']
    id = response_content['id']

    attachments = f'photo{owner_id}_{id}'
    from_group = 1

    post_data = {
        'from_group': from_group,
        'attachments': attachments,
    }
    data = payload | post_data

    url = urljoin(url, method)

    response = requests.post(url, data=data)
    response.raise_for_status()


def main():
    env = Env()
    env.read_env()

    group_id = env.str('GROUP_ID')
    api_key = env.str('VK_TOKEN')

    payload = {
        'access_token': api_key,
        'v': VK_VERSION,
        'group_id': group_id
    }

    while True:
        try:
            server_url = fetch_vk_server_url(VK_URL, payload)

            comic_url = get_random_comic_url(IMG_URL)
            comic_content = get_comic_content(comic_url)

            image_url = comic_content['img']
            filename = get_filename(image_url)

            download_image(image_url, filename)

            server_response = download_image_vk_server(server_url, filename)

            response_content = save_image_vk_server(VK_URL, payload, server_response)

            image_message = comic_content['alt']
            payload['message'] = image_message
            payload['owner_id'] = f'-{group_id}'
            post_image_vk_group(VK_URL, payload, response_content)

            os.remove(filename)

            break

        except requests.exceptions.HTTPError as errh:
            logging.error(errh, exc_info=True)

        except requests.exceptions.ConnectionError as errc:
            logging.error(errc, exc_info=True)
            time.sleep(2)
            continue


if __name__ == '__main__':
    main()