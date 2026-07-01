"""Command, menu, and callback handlers for the Telegram bot."""

import asyncio
import os
from pathlib import Path

import requests
from telegram import Update
from telegram.ext import ContextTypes

from app.crud import get_email_analysis_by_id, get_email_history
from app.export.excel_export import export_requests_to_excel
from app.telegram_bot.keyboards import lead_actions_keyboard, main_menu_keyboard
from app.telegram_bot.messages import format_lead_short, format_stats


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.effective_message is not None:
        await update.effective_message.reply_text(
            "Добро пожаловать в AI CRM Assistant. Выберите действие:",
            reply_markup=main_menu_keyboard(),
        )


async def export_table(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.effective_message is None:
        return

    records = await asyncio.to_thread(get_email_history, 1000)
    file_path = await asyncio.to_thread(export_requests_to_excel, records)
    with open(file_path, "rb") as document:
        await update.effective_message.reply_document(
            document=document,
            filename=Path(file_path).name,
            caption=f"Таблица обращений: {len(records)} записей.",
        )


async def recent_leads(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.effective_message is None:
        return

    records = await asyncio.to_thread(get_email_history, 5)
    if not records:
        await update.effective_message.reply_text("История обращений пока пуста.")
        return

    for record in records:
        await update.effective_message.reply_text(
            format_lead_short(record),
            reply_markup=lead_actions_keyboard(record["id"]),
        )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.effective_message is None:
        return
    records = await asyncio.to_thread(get_email_history, 1000)
    await update.effective_message.reply_text(format_stats(records))


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.effective_message is not None:
        await update.effective_message.reply_text(
            "Настройки будут добавлены позже."
        )


def _callback_lead_id(update: Update) -> int | None:
    query = update.callback_query
    if query is None or not query.data:
        return None
    try:
        return int(query.data.split(":", maxsplit=1)[1])
    except (IndexError, ValueError):
        return None


async def calendar_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    lead_id = _callback_lead_id(update)
    record = (
        await asyncio.to_thread(get_email_analysis_by_id, lead_id)
        if lead_id is not None
        else None
    )
    if record is None:
        await query.message.reply_text("Обращение не найдено.")
        return

    webhook_url = os.getenv("N8N_CALENDAR_WEBHOOK_URL", "").strip()
    if not webhook_url:
        await query.message.reply_text(
            "Webhook календаря не настроен. Укажите N8N_CALENDAR_WEBHOOK_URL."
        )
        return

    payload = {
        "lead_id": record["id"],
        "subject": record["subject"],
        "company": record["company"],
        "summary": record["summary"],
        "deadline": record["deadline"],
        "recommended_action": record["recommended_action"],
    }
    try:
        response = await asyncio.to_thread(
            requests.post,
            webhook_url,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        await query.message.reply_text(
            f"Не удалось отправить запрос в n8n: {exc}"
        )
        return

    await query.message.reply_text(
        "Запрос на добавление в календарь отправлен."
    )


async def reply_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    lead_id = _callback_lead_id(update)
    record = (
        await asyncio.to_thread(get_email_analysis_by_id, lead_id)
        if lead_id is not None
        else None
    )
    if record is None:
        await query.message.reply_text("Обращение не найдено.")
        return

    reply_draft = str(record.get("reply_draft") or "").strip()
    await query.message.reply_text(
        reply_draft or "Черновик ответа не найден."
    )


async def close_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context
    query = update.callback_query
    if query is not None:
        await query.answer()
        await query.message.reply_text("Обращение закрыто.")

