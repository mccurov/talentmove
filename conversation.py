from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    filters
)
from storage import save_vacancy
from utils import format_vacancy_text

# Определяем состояния разговора
POSITION, COMPANY, EXPERIENCE, SALARY, DESCRIPTION, CONFIRM = range(6)

async def start_vacancy(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Давайте создадим новую вакансию. Введите название позиции:")
    return POSITION

async def position(update: Update, context: CallbackContext) -> int:
    context.user_data['position'] = update.message.text
    await update.message.reply_text("Отлично! Теперь введите название компании:")
    return COMPANY

async def company(update: Update, context: CallbackContext) -> int:
    context.user_data['company'] = update.message.text
    await update.message.reply_text("Хорошо. Укажите требуемый опыт работы:")
    return EXPERIENCE

async def experience(update: Update, context: CallbackContext) -> int:
    context.user_data['experience'] = update.message.text
    await update.message.reply_text("Теперь укажите зарплату:")
    return SALARY

async def salary(update: Update, context: CallbackContext) -> int:
    context.user_data['salary'] = update.message.text
    await update.message.reply_text("Отлично. Теперь введите краткое описание вакансии:")
    return DESCRIPTION

async def description(update: Update, context: CallbackContext) -> int:
    context.user_data['description'] = update.message.text
    
    # Формируем вакансию из собранных данных
    vacancy = {
        'user_id': update.effective_user.id,
        'username': update.effective_user.username,
        **context.user_data
    }
    
    # Отображаем собранную информацию пользователю для подтверждения
    vacancy_text = format_vacancy_text(vacancy)
    await update.message.reply_text(
        f"Вот данные вашей вакансии:\n\n{vacancy_text}\n\nВсё верно? (да/нет)"
    )
    return CONFIRM

async def confirm(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == 'да':
        # Сохраняем вакансию
        vacancy = {
            'user_id': update.effective_user.id,
            'username': update.effective_user.username,
            **context.user_data
        }
        vacancy_id = save_vacancy(vacancy)
        
        await update.message.reply_text("Спасибо! Ваша вакансия отправлена на модерацию.")
        # Здесь можно добавить логику отправки вакансии на модерацию
        return ConversationHandler.END
    elif update.message.text.lower() == 'нет':
        await update.message.reply_text("Давайте начнем заново. Введите название позиции:")
        return POSITION
    else:
        await update.message.reply_text("Пожалуйста, ответьте 'да' или 'нет'.")
        return CONFIRM

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Ввод вакансии отменен.")
    return ConversationHandler.END

def get_vacancy_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('vacancy', start_vacancy)],
        states={
            POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, position)],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, company)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience)],
            SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, salary)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )