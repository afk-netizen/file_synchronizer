import logging
format = "%(asctime)s %(message)s"
file_handler = logging.FileHandler('logs.log')
console_handler = logging.StreamHandler()
logging.basicConfig(handlers=(file_handler, console_handler), level='INFO', format=format,
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
