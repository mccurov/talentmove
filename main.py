import os
import signal
import logging
import asyncio
from telegram.ext import ApplicationBuilder
from dotenv import load_dotenv

from storage import init_db
from handlers import register_handlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID'))
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))
TARGET_GROUP_ID = int(os.getenv('TARGET_GROUP_ID'))

# Глобальная переменная для управления циклом бота
should_restart = False

def signal_handler(signum, frame):
    global should_restart
    logger.info("Получен сигнал для перезапуска. Подготовка к перезапуску бота...")
    should_restart = True

async def run_bot():
    global should_restart
    while True:
        should_restart = False
        
        # Инициализация базы данных
        init_db()

        # Создание приложения
        application = ApplicationBuilder().token(TOKEN).build()

        # Регистрация обработчиков
        register_handlers(application, ADMIN_USER_ID, ADMIN_CHAT_ID, TARGET_GROUP_ID)

        # Установка обработчика сигнала
        signal.signal(signal.SIGUSR1, signal_handler)

        logger.info("Бот запущен. Для перезапуска отправьте сигнал SIGUSR1")

        # Запуск бота
        try:
            await application.initialize()
            await application.start()
            await application.updater.start_polling()

            while not should_restart:
                await asyncio.sleep(1)

            logger.info("Получен запрос на перезапуск. Останавливаем бота...")
            await application.stop()
            await application.shutdown()
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}")
        
        if should_restart:
            logger.info("Перезапуск бота...")
        else:
            break

if __name__ == '__main__':
    asyncio.run(run_bot())