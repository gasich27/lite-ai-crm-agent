"""Message formatting for Telegram CRM views."""

from collections import Counter
from typing import Any


def _value(record: dict, key: str, fallback: str = "не указано") -> Any:
    value = record.get(key)
    return value if value not in (None, "") else fallback


def format_lead_short(record: dict) -> str:
    return (
        f"#{_value(record, 'id', '—')}\n"
        f"Компания: {_value(record, 'company', 'не указана')}\n"
        f"Дата: {_value(record, 'created_at', '')}\n"
        f"Тема: {_value(record, 'subject', '')}\n"
        f"Приоритет: {_value(record, 'priority')}"
    )


def format_lead_full(record: dict) -> str:
    return (
        f"🟢 Обращение #{_value(record, 'id', '—')}\n\n"
        f"Email: {_value(record, 'email', 'не указан')}\n"
        f"Компания: {_value(record, 'company', 'не указана')}\n"
        f"Дата: {_value(record, 'created_at', '')}\n"
        f"Тема: {_value(record, 'subject', '')}\n"
        f"Категория: {_value(record, 'category')}\n"
        f"Приоритет: {_value(record, 'priority')}\n"
        f"Бюджет: {_value(record, 'budget')}\n"
        f"Срок: {_value(record, 'deadline')}\n\n"
        f"Кратко:\n{_value(record, 'summary', '')}\n\n"
        "Рекомендованное действие:\n"
        f"{_value(record, 'recommended_action', '')}"
    )


def format_stats(records: list[dict]) -> str:
    categories = Counter(
        str(record.get("category") or "other") for record in records
    )
    priorities = Counter(
        str(record.get("priority") or "").lower() for record in records
    )

    category_lines = (
        "\n".join(
            f"• {category}: {count}"
            for category, count in sorted(categories.items())
        )
        or "• нет данных"
    )

    return (
        "📈 Статистика обращений\n\n"
        f"Всего обращений: {len(records)}\n\n"
        f"По категориям:\n{category_lines}\n\n"
        "По приоритету:\n"
        f"• high: {priorities['high']}\n"
        f"• medium: {priorities['medium']}\n"
        f"• low: {priorities['low']}"
    )

