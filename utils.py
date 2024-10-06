from telegram.constants import ParseMode

VACANCY_FIELDS_ORDER = [
    'должность',
    'требуемый опыт',
    'зарплату',
    'компанию',
    'краткое описание',
    'дату публикации (в формате ДД.ММ.ГГГГ)'
]

def format_vacancy_text(vacancy):
    return (
        f"📌 *{vacancy['position']}*\n"
        f"🏢 *Компания*: {vacancy['company']}\n"
        f"💼 *Опыт*: {vacancy['experience']}\n"
        f"💰 *Зарплата*: {vacancy['salary']}\n"
        f"📝 *Описание*: {vacancy['description']}\n"
    )

