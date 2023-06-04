from aiogram.types import Message, ChatMemberStatus, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ContentTypes
from buttons import main_markup, type_of_service_button, type_of_promotion_button, cancel_markup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from handlers.admin import admin_handler
from dispatcher import bot, dp
from datetime import datetime
from config import BOT_OWNER
from bot import BotDB
import random
import api


class OrderStates(StatesGroup):
    service = State()
    type = State()
    quality = State()
    link = State()
    quantity = State()


class replenishState(StatesGroup):
    check = State()


descriptions = {
    "Instagram": {
        "Arzon": "💵Narx (x1000): 5000 so'm.\n📑Batafsil ma'lumot: Tez boshlanadi. Tezlik soatiga 5-10K.\n🔽Min: 10ta  🔼Max: 10000ta.\n\n🔗Instagram profilingizni havolasini yuboring.",
        "Sifatli": "💵Narx (x1000): 7000 so'm.\n📑Batafsil ma'lumot: Tez boshlanadi. Tezlik soatiga 2-5K. Chiqib ketish ehtimoli 30% gacha.\n🔽Min: 10ta  🔼Max: 10000ta.\n\n🔗Instagram profilingizni havolasini yuboring.",
        "Chiqmaydigan": "💵Narx (x1000): 10000 so'm.\n📑Batafsil ma'lumot: Tez boshlanadi. Chiqishlar bo'lmaydi.\n🔽Min: 10ta  🔼Max: 10000ta.\n\n🔗Instagram profilingizni havolasini yuboring.",
        "Layk": "💵Narx (x1000): 2000 so'm.\n📑Batafsil ma'lumot: Tez boshlanadi. Tezlik soatiga  10K. Qaytishlar bo'lmaydi.\n🔽Min: 10ta  🔼Max: 10000ta.\n\n🔗Instagram postingizni havolasini yuboring.",
    },
    "Telegram": {
        "Obunachi": "💵Narx (x1000): 10000 so'm.\n📑Batafsil ma'lumot: Tez boshlanadi. Tezlik kuniga 20-30K.\n🔽Min: 100ta  🔼Max: 50000ta.\n\n🔗Telegram kanalingizni havolasini yuboring.",
        "Ko'rishlar": "💵Narx (x1000): 500 so'm.\n📑Batafsil ma'lumot: Tez boshlanadi. \n🔽Min: 100ta  🔼Max: 50000ta.\n\n🔗Telegram postingizni havolasini yuboring."
    }
}


async def get_daily_bonus(user_id):
    user_data = BotDB.get_user(user_id)
    if user_data[1] == 0:
        return None

    if user_data[3] is not None:
        last_bonus_date = datetime.strptime(
            user_data[3], "%Y-%m-%d %H:%M:%S.%f")
        today = datetime.today()
        if last_bonus_date.date() == today.date():
            return False

    chance = random.randint(1, 100)
    if chance <= 62:
        bonus = random.randint(10, 30)
    elif chance <= 82:
        bonus = random.randint(31, 65)
    elif chance <= 93:
        bonus = random.randint(66, 90)
    else:
        bonus = random.randint(91, 100)

    BotDB.change_user_balance('+', bonus, user_id)
    BotDB.update_user_last_bonus_date(datetime.now(), user_id)
    return bonus


async def check_subscription(user_id):
    channels_markup = InlineKeyboardMarkup()
    channels = BotDB.get_channels()
    is_subscribed = True
    for channel in channels:
        chat_member = await bot.get_chat_member(channel[2], user_id=user_id)
        if chat_member.status == ChatMemberStatus.LEFT:
            channels_markup.add(InlineKeyboardButton(
                channel[0], url=channel[1]))
            is_subscribed = False
    if not is_subscribed:
        await bot.send_message(user_id, f"⚠️ Bot xizmatlaridan foydalanish uchun quyidagi kanallarga obuna bo'ling.", reply_markup=channels_markup)
    return is_subscribed


@dp.message_handler(commands='start', state='*')
async def cmd_start(message: Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    ref_id = message.text.split()[1] if len(message.text.split()) > 1 else None

    if not BotDB.user_exists(user_id):
        BotDB.add_user(user_id)
        if ref_id:
            BotDB.ref_user(ref_id)
            await bot.send_message(ref_id, "😍 Referal havola orqachi chaqirgan do'stingiz uchun sizning balansingizga 100 so'm tushdi")
    await message.answer("Assalomu alaykum, xush kelibsiz 👋\nBu bot orqali Telegram va Instagram profillaringiz uchun sifatli nakrutka buyurtma qilishingiz mumkin 💫", reply_markup=main_markup)
    await check_subscription(user_id)


@dp.message_handler(text='Bekor qilish', state='*')
async def cancel_FSM(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Operatsiya bekor qilindi!", reply_markup=main_markup)


@dp.message_handler(state=OrderStates.service)
async def process_service(message: Message, state: FSMContext):
    selected_service = message.text
    button = ReplyKeyboardMarkup(
        resize_keyboard=True, selective=True, row_width=2)
    if selected_service == "Instagram":
        button.add("Obunachi", "Layk", "Bekor qilish")
    elif selected_service == "Telegram":
        button.add("Obunachi", "Ko'rishlar", "Bekor qilish")
    else:
        await message.answer("O'zingizga kerakli ijtimoiy tarmoqni tanlang:")
        return
    await state.update_data(selected_service=selected_service)
    await message.answer(f"O'zingizga kerakli xizmat turini tanlang:", reply_markup=button)
    await OrderStates.type.set()


@dp.message_handler(state=OrderStates.type)
async def process_typex(message: Message, state: FSMContext):
    selected_type = message.text
    if selected_type not in ["Obunachi", "Layk", "Ko'rishlar"]:
        await message.answer("Faqat pastdagi tugmalar orqali javob bering!")
        return
    await state.update_data(selected_type=selected_type)
    data = await state.get_data()
    selected_service = data.get('selected_service')
    if selected_service == "Instagram" and selected_type == "Obunachi":
        await message.reply("Obunachilar sifatini tanglang:", reply_markup=type_of_promotion_button)
        await OrderStates.quality.set()
        return

    description = descriptions[selected_service][selected_type]
    await message.reply(description, reply_markup=cancel_markup)
    await OrderStates.link.set()


@dp.message_handler(state=OrderStates.quality)
async def process_type(message: Message, state: FSMContext):
    selected_quality = message.text
    if selected_quality not in ["Arzon", "Sifatli", "Chiqmaydigan"]:
        await message.answer("Faqat pastdagi tugmalar orqali javob bering!")
        return
    await state.update_data(selected_quality=selected_quality)
    description = descriptions['Instagram'][selected_quality]
    await message.reply(description, reply_markup=cancel_markup)
    await OrderStates.link.set()


@dp.message_handler(state=OrderStates.link)
async def getting_ig_link(message: Message, state: FSMContext):
    link = message.text.lower()
    await state.update_data(link=link)
    await message.answer("Sonini kiriting:")
    await OrderStates.quantity.set()


@dp.message_handler(state=OrderStates.quantity)
async def process_quantity(message: Message, state: FSMContext):
    quantity = message.text
    if not quantity.isdigit():
        await message.answer("Faqat raqamlar bilan javob bering.")
        return
    quantity = int(quantity)

    data = await state.get_data()
    selected_service = data.get('selected_service')
    selected_type = data.get('selected_type')
    selected_quality = data.get('selected_quality')
    link = data.get('link')

    if selected_service == "Instagram":
        if quantity < 10 or quantity > 10000:
            await message.answer("Instagram uchun nakrutka soni 10 dan kam yoki 10000 dan ortiq bo'lishi mumkin emas.")
            return
        elif selected_type == "Layk":
            cost_per_follower = 2
            service_id = 290
        elif selected_type == "Obunachi":
            if selected_quality == "Arzon":
                cost_per_follower = 5
                service_id = 1670
            elif selected_quality == "Sifatli":
                cost_per_follower = 8
                service_id = 276
            elif selected_quality == "Chiqmaydigan":
                cost_per_follower = 10
                service_id = 1351
    elif selected_service == "Telegram":
        if quantity < 100 or quantity > 50000:
            await message.answer("Telegram uchun nakrutka soni 100 dan kam yoki 50000 dan ortiq bo'lishi mumkin emas.")
            return
        elif selected_type == "Obunachi":
            cost_per_follower = 10
            service_id = 1737
        elif selected_type == "Ko'rishlar":
            cost_per_follower = 0.5
            service_id = 1497
        else:
            await message.answer("Nakrutka turini tanlashda xatolik chiqdi.", reply_markup=main_markup)
            return
    else:
        await message.answer("Xatolik chiqdi.", reply_markup=main_markup)
        return

    total_cost = cost_per_follower * quantity

    user_id = message.from_user.id
    user_balance = BotDB.get_user(user_id)[2]

    if user_balance < total_cost:
        await message.answer("Balansingizda yetarli mablag' yo'q.")
        return

    await state.finish()
    add_order = api.add_order(link, quantity, service_id)

    if add_order is True:
        BotDB.change_user_balance('-', total_cost, user_id)
        await message.answer('Buyurtma qabul qilindi!', reply_markup=main_markup)
    else:
        await message.answer("Nakrutka buyurtma qilishda xatolik chiqdi.", reply_markup=main_markup)
        await bot.send_message(BOT_OWNER, add_order)


@dp.message_handler(state=replenishState.check, content_types=ContentTypes.PHOTO)
async def handle_broadcast_message(message: Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    text = f"By user `{user_id}`\n{message.caption}"
    await bot.send_photo(BOT_OWNER, message.photo[-1].file_id, caption=text, parse_mode="Markdown")
    await message.reply("Qabul qilindi! Tez orada balansingizga pul tushuriladi.", reply_markup=main_markup)


@dp.message_handler()
async def message_handler(message: Message):
    user_id = message.from_user.id
    text = message.text
    if not await check_subscription(user_id):
        return
    elif text == "❤️ Nakrutka":
        await message.answer("O'zingizga kerakli ijtimoiy tarmoqni tanlang:", reply_markup=type_of_service_button)
        await OrderStates.service.set()
    elif text == "💰 Balans":
        balance = BotDB.get_user(user_id)[2]
        await message.answer(f"💵 Balansingiz: {balance}")
    elif text == "💵 Pul ishlash":
        text = f"🔗Sizning referal havolangiz:\nhttps://t.me/ObunaServisBot?start={user_id}\n\nUshbu havolani do'stlaringiz bilan ulashib botdagi hisobingiz uchun pul ishlashingiz mumkin, o'zingizga referal bo'la olmaysiz!"
        await message.answer(text)
    elif text == "💸 Hisob to'ldirish":
        await message.answer("Hisobni to'ldirish uchun, `9860606734672532` kartasiga kerakli miqdorda pul tushurib chekni botga tashlang.", parse_mode="Markdown", reply_markup=cancel_markup)
        await replenishState.check.set()
    elif text == "🎁 Kunlik bonus":
        bonus = await get_daily_bonus(user_id)
        if bonus is False:
            await message.answer("Siz bugun uchun bonus oldingansiz. Kuniga bir marta bonus olishingiz mumkin holos.")
        elif not bonus:
            await message.answer("Kunlik bonus olish uchun kamida bir kishini referral orqali botga chaqirgan bo'lishingiz kerak.")
        else:
            await message.answer(f"Tabrikmaymiz siz +{bonus} so'm bonus oldingiz!")

    elif user_id == BOT_OWNER:
        return await admin_handler(message, text)
