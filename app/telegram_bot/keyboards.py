"""Telegram reply and inline keyboards."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            ["📊 Таблица обращений", "📋 Последние обращения"],
            ["📈 Статистика", "⚙️ Настройки"],
        ],
        resize_keyboard=True,
    )


def lead_actions_keyboard(lead_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📅 Добавить в календарь",
                    callback_data=f"calendar:{lead_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "✉️ Черновик ответа",
                    callback_data=f"reply:{lead_id}",
                ),
                InlineKeyboardButton(
                    "✅ Закрыть",
                    callback_data=f"close:{lead_id}",
                ),
            ],
        ]
    )

