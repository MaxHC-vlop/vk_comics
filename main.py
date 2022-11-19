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

    comics_number = response_content['num']

    random_number = randrange(1, comics_number + 1)
    
    prefix = f'{random_number}/info.0.json'

    rand_url = urljoin(url, prefix)

    return rand_url


def get_comic_content(url):
    response = requests.get(url)
    response.raise_for_status()

    response_content = response.json()

    return response_content


def fetch_vk_server_url(url, api_key, group_id, vk_version):
    method = 'photos.getWallUploadServer'
    vk_url = urljoin(url, method)
    payload = {
        'access_token': api_key,
        'v': vk_version,
        'group_id': group_id
    }

    response = requests.get(vk_url, params=payload)
    response.raise_for_status()

    response_content = response.json()

    server_url = response_content['response']['upload_url']

    return server_url


def upload_image_vk_server(url, filename):
    with open(filename, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
    response.raise_for_status()

    server_response = response.json()

    return server_response


def save_image_vk_server(url, api_key, group_id, vk_version, photo, server, image_hash):
    method = 'photos.saveWallPhoto'
    data = {
        'access_token': api_key,
        'v': vk_version,
        'group_id': group_id,
        'photo': photo,
        'server': server,
        'hash': image_hash,
    }

    url = urljoin(url, method)

    response = requests.post(url, data=data)
    response.raise_for_status()

    server_response = response.json()

    response_content = server_response['response'][0]

    return response_content


def post_image_vk_group(url, api_key, group_id, vk_version, attachments, image_message):
    method = 'wall.post'
    owner_id = f'-{group_id}'
    from_group = 1

    data = {
        'access_token': api_key,
        'v': vk_version,
        'group_id': group_id,
        'from_group': from_group,
        'attachments': attachments,
        'message': image_message,
        'owner_id': owner_id
    }

    url = urljoin(url, method)

    response = requests.post(url, data=data)
    response.raise_for_status()


def main():
    env = Env()
    env.read_env()

    group_id = env.str('VK_GROUP_ID')
    api_key = env.str('VK_TOKEN')

    try:
        server_url = fetch_vk_server_url(
            VK_URL, api_key, group_id, VK_VERSION)

        comic_url = get_random_comic_url(IMG_URL)
        comic_content = get_comic_content(comic_url)

        image_url = comic_content['img']
        filename = get_filename(image_url)

        download_image(image_url, filename)

        server_response = upload_image_vk_server(server_url, filename)

        photo = server_response['photo']
        server = server_response['server']
        image_hash = server_response['hash']

        response_content = save_image_vk_server(
            VK_URL, api_key, group_id, VK_VERSION,
            photo, server, image_hash
        )

        owner_id = response_content['owner_id']
        media_id = response_content['id']
        attachments = f'photo{owner_id}_{media_id}'
        image_message = comic_content['alt']

        post_image_vk_group(
            VK_URL, api_key, group_id, VK_VERSION,
            attachments, image_message
            )

    except requests.exceptions.HTTPError as errh:
        logging.error(errh, exc_info=True)

    except requests.exceptions.ConnectionError as errc:
        logging.error(errc, exc_info=True)
        time.sleep(2)

    finally:
        os.remove(filename)


if __name__ == '__main__':
    main()