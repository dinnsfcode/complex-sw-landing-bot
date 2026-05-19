from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Все заявки")],
        [KeyboardButton(text="В работе"), KeyboardButton(text="В отказе")],
        [KeyboardButton(text="Выполненные")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите раздел",
)


def leads_list_ikb(records):
    buttons = []

    for lead_id, name, phone, _, _, _, status, created_at in records:
        title = name or phone or "Без имени"
        buttons.append([
            InlineKeyboardButton(
                text=f"#{lead_id} {title} · {status_label(status)} · {created_at}",
                callback_data=f"lead:{lead_id}",
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def lead_actions_ikb(lead_id, status):
    if status == "work":
        buttons = [[
            InlineKeyboardButton(
                text="Выполнено",
                callback_data=f"status:{lead_id}:done",
            )
        ]]
    elif status == "rejected":
        buttons = [[
            InlineKeyboardButton(
                text="Вернуть в работу",
                callback_data=f"status:{lead_id}:new",
            )
        ]]
    elif status == "done":
        buttons = []
    else:
        buttons = [[
            InlineKeyboardButton(
                text="Взято в работу",
                callback_data=f"status:{lead_id}:work",
            ),
            InlineKeyboardButton(
                text="Отказ",
                callback_data=f"status:{lead_id}:rejected",
            ),
        ]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def status_label(status):
    labels = {
        "new": "новая",
        "work": "в работе",
        "rejected": "отказ",
        "done": "выполнено",
    }
    return labels.get(status, status)
