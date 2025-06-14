import telebot
from telebot import asyncio_helper
from config import BOT_TOKEN
from handlers import (
    start_handler, submit_handler, match_handler, proof_handler,
    verify_handler, report_handler, video_handler
)
from database import init_db

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

def register_handlers(bot):
    start_handler.register(bot)
    submit_handler.register(bot)
    match_handler.register(bot)
    proof_handler.register(bot)
    verify_handler.register(bot)
    report_handler.register(bot)
    video_handler.register(bot)

if __name__ == "__main__":
    init_db()
    register_handlers(bot)
    print("Bot started.")
    bot.infinity_polling()