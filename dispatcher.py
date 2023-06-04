from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
import logging
import config

logging.basicConfig(level=logging.INFO)

if not config.BOT_TOKEN:
	exit("No token provided")

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
