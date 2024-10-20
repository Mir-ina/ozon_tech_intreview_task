from http import HTTPStatus
from time import sleep
import requests


class YaUploader:
    def __init__(self, token: str, path: str) -> None:
        self.__token = token
        self.__path = path

        response = requests.get(f"https://cloud-api.yandex.net/v1/disk/resources?path={self.__path}", headers=self.__auth_header)
        if response.status_code == HTTPStatus.NOT_FOUND.value:
            requests.put(
                f"https://cloud-api.yandex.net/v1/disk/resources?path={self.__path}",
                headers=self.__auth_header,
            ).raise_for_status()
            return
        response.raise_for_status()

    @property
    def __auth_header(self) -> dict[str, str]:
        return {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"OAuth {self.__token}"}

    def upload_photos_to_yd(self, url_file: str, name: str) -> None:
        """Сохраняет в яндекс директории файлы из интернета"""
        params = {"path": f"{self.__path}/{name}", "url": url_file}
        upload_response = requests.post(
            "https://cloud-api.yandex.net/v1/disk/resources/upload",
            headers=self.__auth_header,
            params=params,
        )
        upload_response.raise_for_status()
        for _ in range(10):
            operation_response = requests.get(
                upload_response.json()["href"],
                headers=self.__auth_header,
            )
            operation_response.raise_for_status()
            if operation_response.json()["status"] == "success":
                break
            sleep(1)
