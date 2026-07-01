"""Telegram bot application setup and polling entry point."""

import os

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.database import init_db
from app.telegram_bot.handlers import (
    calendar_callback,
    close_callback,
    export_table,
    recent_leads,
    reply_callback,
    settings,
    start,
    stats,
)


def run_bot() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not configured. Add it to the .env file."
        )

    init_db()
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.Regex(r"^📊 Таблица обращений$"), export_table)
    )
    application.add_handler(
        MessageHandler(filters.Regex(r"^📋 Последние обращения$"), recent_leads)
    )
    application.add_handler(
        MessageHandler(filters.Regex(r"^📈 Статистика$"), stats)
    )
    application.add_handler(
        MessageHandler(filters.Regex(r"^⚙️ Настройки$"), settings)
    )
    application.add_handler(
        CallbackQueryHandler(calendar_callback, pattern=r"^calendar:\d+$")
    )
    application.add_handler(
        CallbackQueryHandler(reply_callback, pattern=r"^reply:\d+$")
    )
    application.add_handler(
        CallbackQueryHandler(close_callback, pattern=r"^close:\d+$")
    )

    application.run_polling()

