import html

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

import app.keyboards as kb
from config import ADMIN_CHAT_ID
from database import add_operator, get_lead, get_leads, update_lead_status


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    if not await ensure_allowed_message(message):
        return

    add_operator(message.chat.id)

    await message.answer(
        "Панель заявок Complex SW СУСТАВЫ.",
        reply_markup=kb.main_kb,
    )


@router.message(F.text == "Все заявки")
async def all_leads(message: Message):
    if not await ensure_allowed_message(message):
        return

    await send_leads_list(message, "new", "Все заявки")


@router.message(F.text == "В работе")
async def work_leads(message: Message):
    if not await ensure_allowed_message(message):
        return

    await send_leads_list(message, "work", "Заявки в работе")


@router.message(F.text == "В отказе")
async def rejected_leads(message: Message):
    if not await ensure_allowed_message(message):
        return

    await send_leads_list(message, "rejected", "Заявки в отказе")


@router.message(F.text == "Выполненные")
async def done_leads(message: Message):
    if not await ensure_allowed_message(message):
        return

    await send_leads_list(message, "done", "Выполненные заявки")


@router.callback_query(F.data.startswith("lead:"))
async def lead_details(callback: CallbackQuery):
    if not await ensure_allowed_callback(callback):
        return

    lead_id = int(callback.data.split(":")[1])
    lead = get_lead(lead_id)

    if not lead:
        await callback.answer("Заявка не найдена")
        return

    await callback.answer()
    await callback.message.answer(
        format_lead(lead),
        reply_markup=kb.lead_actions_ikb(lead_id, lead[6]),
    )


@router.callback_query(F.data.startswith("status:"))
async def set_status(callback: CallbackQuery):
    if not await ensure_allowed_callback(callback):
        return

    _, lead_id, status = callback.data.split(":")
    lead_id = int(lead_id)

    update_lead_status(lead_id, status)
    lead = get_lead(lead_id)

    if status == "new":
        text = "Заявка возвращена в новые"
    elif status == "done":
        text = "Заявка отмечена выполненной"
    else:
        text = "Статус обновлён"

    await callback.answer(text)
    await callback.message.edit_text(
        format_lead(lead),
        reply_markup=kb.lead_actions_ikb(lead_id, lead[6]),
    )


async def send_leads_list(message: Message, status: str | None, title: str):
    records = get_leads(status)

    if not records:
        await message.answer(f"{title}: пока пусто.", reply_markup=kb.main_kb)
        return

    await message.answer(
        f"{title}: {len(records)}",
        reply_markup=kb.leads_list_ikb(records),
    )


def format_lead(lead):
    lead_id, name, phone, email, city, message, status, created_at = lead

    lines = [
        f"<b>Заявка #{lead_id}</b>",
        f"<b>Статус:</b> {kb.status_label(status)}",
        f"<b>Дата:</b> {safe(created_at)}",
        "",
        f"<b>Имя:</b> {safe(name) or 'не указано'}",
        f"<b>Телефон:</b> {safe(phone) or 'не указан'}",
        f"<b>Email:</b> {safe(email) or 'не указан'}",
        f"<b>Город:</b> {safe(city) or 'не указан'}",
    ]

    if message:
        lines.extend(["", f"<b>Комментарий:</b>\n{safe(message)}"])

    return "\n".join(lines)


def safe(value):
    return html.escape(str(value or "").strip())


async def ensure_allowed_message(message: Message):
    if is_allowed(message.chat.id, message.from_user.id):
        return True

    await message.answer("Доступ к заявкам ограничен.")
    return False


async def ensure_allowed_callback(callback: CallbackQuery):
    chat_id = callback.message.chat.id if callback.message else None
    user_id = callback.from_user.id

    if is_allowed(chat_id, user_id):
        return True

    await callback.answer("Доступ ограничен", show_alert=True)
    return False


def is_allowed(chat_id, user_id):
    if not ADMIN_CHAT_ID:
        return True

    allowed = str(ADMIN_CHAT_ID)
    return str(chat_id) == allowed or str(user_id) == allowed
