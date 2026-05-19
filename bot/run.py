import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.handlers import router
from config import ADMIN_CHAT_ID, BOT_TOKEN, BOT_WEB_HOST, BOT_WEB_PORT, LEAD_SECRET
from database import add_lead, get_operators, init_db

try:
    from aiohttp import web
except ModuleNotFoundError:
    web = None


async def health(_):
    return json_response({"ok": True})


async def options_handler(_):
    return web.Response(headers=cors_headers())


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type, X-Lead-Secret",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    }


def json_response(data, status=200):
    return web.json_response(data, status=status, headers=cors_headers())


def create_lead_handler(bot: Bot):
    async def handle_lead(request):
        if LEAD_SECRET:
            request_secret = request.headers.get("X-Lead-Secret")
            if request_secret != LEAD_SECRET:
                return json_response({"ok": False, "error": "forbidden"}, status=403)

        try:
            data = await request.json()
        except Exception:
            return json_response({"ok": False, "error": "invalid_json"}, status=400)

        lead_id = add_lead(
            name=data.get("name"),
            phone=data.get("phone"),
            email=data.get("email"),
            city=data.get("city"),
            message=data.get("message"),
        )

        recipients = set(get_operators())
        if ADMIN_CHAT_ID:
            recipients.add(str(ADMIN_CHAT_ID))

        for chat_id in recipients:
            await bot.send_message(
                chat_id,
                f"Новая заявка #{lead_id}. Откройте меню бота, чтобы взять её в работу или отказать.",
            )

        return json_response({"ok": True, "lead_id": lead_id})

    return handle_lead


async def start_web_app(bot: Bot):
    if web is None:
        logging.warning("aiohttp is not installed. Lead endpoint /lead is disabled.")
        await asyncio.Event().wait()
        return

    app = web.Application()
    app.router.add_get("/health", health)
    app.router.add_post("/lead", create_lead_handler(bot))
    app.router.add_options("/lead", options_handler)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, BOT_WEB_HOST, BOT_WEB_PORT)
    await site.start()
    logging.info("Lead endpoint started on http://%s:%s/lead", BOT_WEB_HOST, BOT_WEB_PORT)

    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()


async def main():
    init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()
    dp.include_router(router)

    await asyncio.gather(
        dp.start_polling(bot),
        start_web_app(bot),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
