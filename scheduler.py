import asyncio
from datetime import datetime
from storage import get_vacancy, update_vacancy_status
from handlers import publish_vacancy

scheduled_tasks = {}

def schedule_vacancy_publication(vacancy_id, publication_date):
    now = datetime.now()
    delay = (publication_date - now).total_seconds()
    
    if delay > 0:
        task = asyncio.create_task(delayed_publication(vacancy_id, delay))
        scheduled_tasks[vacancy_id] = task
    else:
        # Если дата публикации уже наступила, публикуем сразу
        asyncio.create_task(publish_vacancy(None, vacancy_id))

async def delayed_publication(vacancy_id, delay):
    await asyncio.sleep(delay)
    await publish_vacancy(None, vacancy_id)
    del scheduled_tasks[vacancy_id]

def cancel_scheduled_publication(vacancy_id):
    if vacancy_id in scheduled_tasks:
        scheduled_tasks[vacancy_id].cancel()
        del scheduled_tasks[vacancy_id]
        update_vacancy_status(vacancy_id, 'cancelled')

async def check_pending_publications():
    while True:
        now = datetime.now()
        vacancies = get_pending_vacancies()
        for vacancy in vacancies:
            publication_date = datetime.strptime(vacancy['publication_date'], "%d.%m.%Y")
            if publication_date <= now:
                await publish_vacancy(None, vacancy['id'])
        await asyncio.sleep(60)  # Проверяем каждую минуту

def start_scheduler():
    asyncio.create_task(check_pending_publications())

# Эту функцию нужно вызвать при запуске бота
def init_scheduler():
    start_scheduler()