"""Common utils for module."""

import requests
import logging
from PIL import Image, UnidentifiedImageError
from urllib.parse import urlparse


def get_image_from_url(url):
    """Fetch image from an url.

    :param url: url address of the image
    :return : PIL image of the url
    """
    try:
        img = Image.open(requests.get(url, stream=True).raw)
        if img.mode != "RGB":
            img = img.convert("RGB")
    except UnidentifiedImageError as e:
        logging.error("URL invalid %s", url)
        raise Exception("Unable to decode image from the url " + url, e)
    return img

def get_image_from_path(url):
    """Fetch image from an path.

    :param path: path address of the image
    :return : PIL image of the path
    """
    try:
        parsed_url = urlparse(url)
        path = parsed_url.path.lstrip('/')
        img = Image.open("/data/" + path)
        if img.mode != "RGB":
            img = img.convert("RGB")
    except UnidentifiedImageError as e:
        logging.error("URL invalid %s", url)
        raise Exception("Unable to decode image from the url " + url, e)
    return img


def get_buffer_image_from_url(url):
    """Fetch image from an url.

    :param url: url address of the image
    :return : buffer image of the url
    """
    try:
        res = requests.get(url, stream=True)
        img = res.content
    except UnidentifiedImageError as e:
        logging.error("URL invalid %s", url)
        raise Exception("Unable to decode image from the url " + url, e)
    return img
