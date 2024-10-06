import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO):
    """Функция для настройки логгера"""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')

    # Создаем директорию для логов, если она не существует
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # Добавляем вывод в консоль
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger

# Создаем логгеры для разных модулей
main_logger = setup_logger('main', 'logs/main.log')
handlers_logger = setup_logger('handlers', 'logs/handlers.log')
storage_logger = setup_logger('storage', 'logs/storage.log')
conversation_logger = setup_logger('conversation', 'logs/conversation.log')
scheduler_logger = setup_logger('scheduler', 'logs/scheduler.log')