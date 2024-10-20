import os
import requests

from lib.ya_uploader import YaUploader


def get_sub_breeds(breed) -> list[str]:
    """Возвращает список подпород"""
    response = requests.get(f"https://dog.ceo/api/breed/{breed}/list")
    response.raise_for_status()
    return response.json().get("message", [])


def get_urls(breed, sub_breeds) -> list[str]:
    """Возвращает список url для заданной пароды и подпороды"""
    url_images = []
    if sub_breeds:
        for sub_breed in sub_breeds:
            response = requests.get(f"https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random")
            response.raise_for_status()
            sub_breed_urls = response.json().get("message")
            url_images.append(sub_breed_urls)
    else:
        response = requests.get(f"https://dog.ceo/api/breed/{breed}/images/random")
        response.raise_for_status()
        url_images.append(response.json().get("message"))
    return url_images


def u(breed):
    """Загружает случайные фото породы и подпород, если существуют"""
    token = os.getenv("API_TOKEN")
    assert token
    path = os.getenv("YA_DIR")
    assert path
    sub_breeds = get_sub_breeds(breed)
    urls = get_urls(breed, sub_breeds)
    yandex_client = YaUploader(token=token, path=path)
    for url in urls:
        part_name = url.split("/")
        assert len(part_name) > 2
        name = "_".join([part_name[-2], part_name[-1]])
        yandex_client.upload_photos_to_yd(url_file=url, name=name)
