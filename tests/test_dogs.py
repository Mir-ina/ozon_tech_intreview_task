import os
import pytest
import requests

from http import HTTPStatus
from time import sleep

from service import get_sub_breeds, u

YA_DISK_RESOURCES = "https://cloud-api.yandex.net/v1/disk/resources"


@pytest.fixture
def token():
    return os.getenv("API_TOKEN")


@pytest.fixture
def ya_headers(token):
    assert token, "Token не задан"
    return {"Content-Type": "application/json", "Accept": "application/json", "Authorization": token}


@pytest.fixture
def ya_path():
    return os.getenv("YA_DIR")


@pytest.fixture
def setup(ya_headers, ya_path):
    assert ya_path, "Директория не задана"
    meta_dir_info = requests.get(f"{YA_DISK_RESOURCES}?path={ya_path}", headers=ya_headers)
    assert meta_dir_info.status_code == HTTPStatus.NOT_FOUND.value, f"Тестовая директория {ya_path} уже существует либо запрос к диску не успешен"

    yield

    delete_response = requests.delete(f"{YA_DISK_RESOURCES}?path={ya_path}&permanently=true", headers=ya_headers)
    delete_response.raise_for_status()

    for _ in range(10):
        operation_response = requests.get(
            delete_response.json()["href"],
            headers=ya_headers,
        )
        operation_response.raise_for_status()
        if operation_response.json()["status"] == "success":
            break
        sleep(1)


@pytest.mark.parametrize("breed", ["doberman", "bulldog"])
def test_proverka_upload_dog(token, ya_headers, ya_path, setup, breed):
    """Проверяет программу загрузки фото собак на яндекс диск"""
    u(breed)

    # проверка
    response = requests.get(f"{YA_DISK_RESOURCES}?path={ya_path}", headers=ya_headers)
    assert response.status_code == 200, "Запрос о статусе директории не успешен"
    assert response.json()["type"] == "dir", "Тип объекта не директория"

    for item in response.json()["_embedded"]["items"]:
        assert item["type"] == "file", "Директория содержит что-то кроме файлов"
        assert item["name"].startswith(breed), "Директория содержит файл с неизвестным именем"

    sub_breeds = get_sub_breeds(breed)
    if sub_breeds:
        assert len(response.json()["_embedded"]["items"]) == len(sub_breeds), "Количество файлов отличается от ожидаемого"
    else:
        assert len(response.json()["_embedded"]["items"]) == 1, "Количество файлов отличается от ожидаемого"
