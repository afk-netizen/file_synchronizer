import hashlib
import time
import dotenv
import logging
import os.path
import threading
from sys import exit
from yandex_api_module import WorkWithYD
from config import logger
class Checker(threading.Thread):
    """Поток, с заданной периодичностью синхронизирует локальную и удаленную папку"""

    def __init__(self, logger: logging.Logger, exc_for_YD: 'WorkWithYD'):
        super().__init__()
        self.logger = logger
        self.work_with_yd = exc_for_YD

    def run(self) -> None:
        while True:
            logger.info('Синхронизация папок')
            view_of_the_local_folder = generate_view_of_the_local_folder(synced_dir)
            view_of_the_remote_folder = self.work_with_yd.get_info()
            if view_of_the_local_folder == 'error' or view_of_the_remote_folder == 'error':
                break

            comparison_of_local_and_remote_folder(view_of_the_local_folder, view_of_the_remote_folder,
                                                  self.work_with_yd)
            logger.info('Синхронизация окончена')
            time.sleep(int(timeout))



def generate_view_of_the_local_folder(path) -> dict[str, str]:
    """Генерирует представление о локальных файлов в виде словаря name:hash"""
    try:
        data_for_local_files = dict()
        for obj in os.scandir(path):
            if obj.is_file():
                sha256 = hashlib.new('sha256')
                with open(obj.path, 'rb') as file:
                    sha256.update(file.read())
                data_for_local_files[obj.path] = sha256.hexdigest()
        return data_for_local_files
    except FileNotFoundError as error:
        logger.info(error)


def comparison_of_local_and_remote_folder(local_data, remote_data, work_with_yd) -> None:
    """метод сравнивает имена и хэши локальных и удаленных файлов"""
    remote_names = remote_data.keys()
    local_names = [os.path.basename(file) for file in local_data.keys()]

    # проверка на добавление файлов
    for local_file, hash_256 in local_data.items():
        local_name = os.path.basename(local_file)
        if local_name in remote_names and hash_256 != remote_data[local_name]:
            work_with_yd.load(local_file)
        elif local_name not in remote_names:  # для логического разделения вынес условия в отдельный elif
            work_with_yd.load(local_file)

    # проверка на удаление файлов
    files_to_delete = [file for file in remote_data.keys() if file not in local_names]
    for file_to_delete in files_to_delete:
        work_with_yd.delete(os.path.join(synced_dir, file_to_delete))


if __name__ == '__main__':
    dotenv.load_dotenv()
    config = dotenv.dotenv_values()
    try:
        url, synced_dir, token, dir_on_disk, timeout = config['URL'], config['synced_dir'], config['TOKEN'], config[
            'dir_on_disk'], config['timeout']
        headers_for_api = {'Authorization': f'OAuth {token}',
                           'Accept': 'application/json'}
    except (KeyError, NameError) as error:
        logger.info(str(error) + ' переменная не обнаружена')
        exit()

    logger.info(f'Программа начинает работу с директорией {synced_dir}')

    exc_for_yd = WorkWithYD(dir_on_disk=dir_on_disk, url=url, headers_for_api=headers_for_api)
    check_the_dir_thread = Checker(logger, exc_for_yd)
    check_the_dir_thread.start()
    check_the_dir_thread.join()
