import requests
import re
from typing import Any
import sys
from config import logger
import os

class WorkWithYD:
    """Класс, описывает методы для работы с апи яндекс диска"""

    def __init__(self, headers_for_api: dict, url: str, dir_on_disk: str):
        self.headers = headers_for_api
        self.resources_url = url
        self.dir_on_disk = dir_on_disk

    def load(self, abs_path_of_file: str) -> None:
        def get_link_for_load() -> Any | None:
            """Получает ссылку для загрузки файла"""
            request = f'{self.resources_url}/upload?path={self.dir_on_disk}/{os.path.basename(abs_path_of_file)}&overwrite=true'
            answer = requests.get(request, headers=self.headers)
            if answer.status_code == 200:
                return answer.json()['href']
            else:
                logger.error(f'Ошибка в получении ссылки для загрузки файла. {answer.json()["message"]}')
                return None

        link_for_load = get_link_for_load()
        if not link_for_load:
            return

        with open(abs_path_of_file, 'rb') as file:
            try:
                requests.put(link_for_load, data=file, headers=self.headers)
            except KeyError:
                logger.error('Ошибка при отправке файла на сервер')
            else:
                logger.info(f'Файл {file.name} загружен')

    def reload(self):
        pass
        # хоть в тз и был пункт об этом методе,
        # я в нем смысла не вижу по причине наличия флага overwrite,
        # в методе получения ссылки на загрузку load/get_link_for_load

    def delete(self, abs_path_of_file: str) -> None:
        filename = os.path.basename(abs_path_of_file)
        path_file = os.path.join(self.dir_on_disk, filename).replace('\\', '/')
        request = f'{self.resources_url}?path={path_file}'
        request = requests.delete(request, headers=self.headers)
        if request.status_code == 204:
            logger.info(f'Файл {abs_path_of_file} удален из облака')
        else:
            logger.error(f'Ошибка при удалении файла. {request.json()["message"]}')

    def get_info(self) -> str | dict[str, str]:
        """метод для получения словаря вида имя файла:хэш"""
        data = {}
        try:
            request = (requests.get(f'{self.resources_url}/last-uploaded', headers=self.headers))
            if request.status_code == 401:
                logger.error('Ошибка с подключением к Яндекс Диску, проверьте токен')
                return 'error'
            elif request.status_code == 404:
                logger.error('Ошибка с URL, проверьте адрес для запросов')
                return 'error'
            all_records = request.json()['items']
            for record in all_records:
                if re.search(f'{self.dir_on_disk}/', record['path']):
                    data[record['name']] = record['sha256']
            return data
        except requests.exceptions.MissingSchema:
            logger.info('Ошибка в базовом URL')
            sys.exit()
