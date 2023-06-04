from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
promotion_button = KeyboardButton("❤️ Nakrutka")
balance_button = KeyboardButton("💰 Balans")
earn_button = KeyboardButton("💵 Pul ishlash")
replenish_button = KeyboardButton("💸 Hisob to'ldirish")
bonus_button = KeyboardButton("🎁 Kunlik bonus")
main_markup.add(promotion_button)
main_markup.add(balance_button, earn_button, replenish_button, bonus_button)

cancel_button = KeyboardButton("Bekor qilish")
cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_button)

cancel_ru_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Отмена")

type_of_service_button = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
type_of_service_button.add(KeyboardButton("Instagram"), KeyboardButton("Telegram"), cancel_button)

type_of_promotion_button = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
type_of_promotion_button.add("Arzon", "Sifatli", "Chiqmaydigan", cancel_button)

admin_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
admin_markup.add("Добавить канал", "Убрать канал", "Пополнить баланс", "Статистика", "Рассылка")
