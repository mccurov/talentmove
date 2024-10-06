import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler
)
from telegram.constants import ParseMode

from storage import (
    get_vacancy, get_all_vacancies, update_vacancy_status
)
from utils import format_vacancy_text
from conversation import get_vacancy_conversation_handler

logger = logging.getLogger(__name__)

ADMIN_ACTION, HANDLE_VACANCY = range(2)

def register_handlers(application, admin_user_id, admin_chat_id, target_group_id):
    application.add_handler(get_vacancy_conversation_handler())
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('admin', admin_panel))

    conv_handler_admin = ConversationHandler(
        entry_points=[CommandHandler('admin', admin_panel)],
        states={
            ADMIN_ACTION: [CallbackQueryHandler(admin_action_handler)],
            HANDLE_VACANCY: [CallbackQueryHandler(handle_vacancy)]
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)],
        per_chat=False
    )
    application.add_handler(conv_handler_admin)

    application.bot_data['ADMIN_USER_ID'] = admin_user_id
    application.bot_data['ADMIN_CHAT_ID'] = admin_chat_id
    application.bot_data['TARGET_GROUP_ID'] = target_group_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для публикации вакансий.\n"
        "Отправьте команду /vacancy, чтобы начать создание новой вакансии."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/vacancy - Создать новую вакансию\n"
        "/admin - Открыть админ-панель (только для администратора)"
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_user_id = context.bot_data['ADMIN_USER_ID']
    
    logger.info(f"Попытка доступа к админ-панели. User ID: {user_id}, Admin ID: {admin_user_id}")
    
    if user_id != admin_user_id:
        logger.warning(f"Попытка несанкционированного доступа к админ-панели. User ID: {user_id}")
        await update.message.reply_text("У вас нет прав для доступа к админ-панели.")
        return ConversationHandler.END
    
    logger.info(f"Доступ к админ-панели разрешен для пользователя {user_id}")
    
    keyboard = [
        [InlineKeyboardButton("Просмотр новых вакансий", callback_data='view_pending')],
        [InlineKeyboardButton("Просмотр одобренных вакансий", callback_data='view_approved')],
        [InlineKeyboardButton("Просмотр отклоненных вакансий", callback_data='view_rejected')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
    return ADMIN_ACTION

async def admin_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    action = query.data
    if action.startswith('view_'):
        status = action.split('_')[1]
        vacancies = get_all_vacancies(status=status)
        if not vacancies:
            await query.edit_message_text(f"Нет вакансий со статусом '{status}'.")
            return ADMIN_ACTION
        
        for vacancy in vacancies:
            vacancy_text = format_vacancy_text(vacancy)
            keyboard = [
                [InlineKeyboardButton("✅ Одобрить", callback_data=f'approve_{vacancy["id"]}'),
                 InlineKeyboardButton("❌ Отклонить", callback_data=f'reject_{vacancy["id"]}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=context.bot_data['ADMIN_CHAT_ID'],
                text=vacancy_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        return HANDLE_VACANCY
    return ADMIN_ACTION

async def handle_vacancy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    action, vacancy_id = query.data.split('_')
    vacancy_id = int(vacancy_id)
    
    if action == 'approve':
        update_vacancy_status(vacancy_id, 'approved')
        await publish_vacancy(context, vacancy_id)
        await query.edit_message_text("Вакансия одобрена и опубликована.")
    elif action == 'reject':
        update_vacancy_status(vacancy_id, 'rejected')
        await query.edit_message_text("Вакансия отклонена.")
    
    return ADMIN_ACTION

async def publish_vacancy(context: ContextTypes.DEFAULT_TYPE, vacancy_id):
    vacancy = get_vacancy(vacancy_id)
    if vacancy:
        target_group_id = context.bot_data['TARGET_GROUP_ID']
        vacancy_text = format_vacancy_text(vacancy)
        await context.bot.send_message(
            chat_id=target_group_id,
            text=vacancy_text,
            parse_mode=ParseMode.MARKDOWN
        )

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END