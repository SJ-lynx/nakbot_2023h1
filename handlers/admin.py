from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ContentTypes, CallbackQuery
from aiogram.dispatcher.filters.state import State, StatesGroup
from buttons import admin_markup, cancel_ru_markup
from aiogram.dispatcher import FSMContext
from dispatcher import bot, dp
from config import BOT_OWNER
from bot import BotDB
import asyncio


class AdminState(StatesGroup):
	get_channel = State()
	WaitingForBroadcast = State()
	replenish = State()


@dp.message_handler(commands="admin")
async def cmd_admin(message: Message):
	if message.from_user.id == BOT_OWNER:
		return await message.answer(f"Админ панель:", reply_markup=admin_markup)


@dp.message_handler(text='Отмена', state='*')
async def cancel_FSM(message: Message, state: FSMContext):
	await state.finish()
	if message.from_user.id == BOT_OWNER:
		await message.answer("Операция отменена!", reply_markup=admin_markup)


@dp.message_handler(state=AdminState.replenish)
async def process_get_channel(message: Message, state: FSMContext):
	try:
		id, amount = message.text.split(" - ")
		BotDB.change_user_balance('+', float(amount), int(id))
		await message.answer(f"Пользователью под ID {id} пополнен баланс.", parse_mode="Markdown", reply_markup=admin_markup)
		await state.finish()
	except Exception as Ex:
		await message.answer(Ex)


@dp.message_handler(state=AdminState.get_channel)
async def process_replanish(message: Message, state: FSMContext):
	try:
		name, link, id = message.text.split(" - ")
		BotDB.add_channel(name, link, id)
		await message.answer(f"Канал {name} добавлен на обьязательную подписку.", reply_markup=admin_markup)
		await state.finish()
	except Exception as Ex:
		await message.answer(Ex)


async def send_broadcast_to_user(content_type, user_id, message):
	try:
		if content_type == "text":
			await bot.send_message(user_id, message.text)
		elif content_type == "photo":
			await bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
		elif content_type == "video":
			await bot.send_video(user_id, message.video.file_id, caption=message.caption)
	except Exception as e:
		print(f"Ошибка при отправке рассылки пользователю {user_id}: {str(e)}")


@dp.message_handler(state=AdminState.WaitingForBroadcast, content_types=ContentTypes.ANY)
async def handle_broadcast_message(message: Message, state: FSMContext):
	await message.reply("Рассылка получена! Начинаю отправку...")

	users = BotDB.get_users()

	for user in users:
		user_id = user[0]
		content_type = message.content_type

		await send_broadcast_to_user(content_type, user_id, message)

		await asyncio.sleep(0.1)
	await state.finish()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del_'))
async def delete_channel(call: CallbackQuery):
	try:
		channel_id = call.data.replace("del_", "")
		BotDB.delete_channel(channel_id)

		channels_markup = InlineKeyboardMarkup()
		channels = BotDB.get_channels()

		for channel in channels:
			channels_markup.add(InlineKeyboardButton(
				f"⛔ {channel[0]}", callback_data=f"del_{channel[2]}"))
		await call.message.edit_reply_markup(channels_markup)
		await call.answer(f"Канал под ID {channel_id}, удалён из обьязательной подписки!")
	except Exception as Ex:
		await bot.send_message(call.from_user.id, Ex)


async def admin_handler(message, text):
	if message.from_user.id != BOT_OWNER:
		return
	elif text == "Добавить канал":
		await AdminState.get_channel.set()
		await message.answer("Введите название, ссылку и ID на канала, которую вы зотите добавить на ОП в формате \"название - ссылка - ID\"", reply_markup=cancel_ru_markup)
	elif text == "Убрать канал":
		channels_markup = InlineKeyboardMarkup()
		channels = BotDB.get_channels()

		for channel in channels:
			channels_markup.add(InlineKeyboardButton(
				f"⛔ {channel[0]}", callback_data=f"del_{channel[2]}"))
		await message.answer("Нажмите на название нужного канала чтобы убрать тот канал с объязательной подписки", reply_markup=channels_markup)
	elif text == "Пополнить баланс":
		await message.answer("Введите ID пользователья и сумму, которую вы зотите добавить в формате \"ID - сумма\"", reply_markup=cancel_ru_markup)
		await AdminState.replenish.set()
	elif text == "Статистика":
		users = BotDB.get_users()
		await message.answer(f"В боте всего {len(users)} пользователей.")
	elif text == "Рассылка":
		await message.reply("Отправьте боту рассылку для пользователей (текст, фото, видео и т. д.)", reply_markup=cancel_ru_markup)
		await AdminState.WaitingForBroadcast.set()
