import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message,
    LabeledPrice,
    PreCheckoutQuery,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ==================== КОНФИГУРАЦИЯ ====================
# Берем токены из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 8891314013))

# Если токен не найден - ошибка
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

# ==================== ТОВАРЫ С ССЫЛКАМИ ====================
PRODUCTS = {
    "5gb": {
        "id": "5gb",
        "name": "Пакет 5 ГБ",
        "price": 100,
        "price_label": "100 ⭐️ Stars",
        "size": "5 ГБ",
        "emoji": "📦",
        "link": "https://t.me/+e0coxbzyAWFjYzk5",
    },
    "10gb": {
        "id": "10gb",
        "name": "Пакет 10 ГБ",
        "price": 250,
        "price_label": "250 ⭐️ Stars",
        "size": "10 ГБ",
        "emoji": "📦",
        "link": "https://t.me/+rpeY-cXDOpg5OTMx",
    },
    "20gb": {
        "id": "20gb",
        "name": "Пакет 20 ГБ",
        "price": 350,
        "price_label": "350 ⭐️ Stars",
        "size": "20 ГБ",
        "emoji": "📦",
        "link": "https://t.me/+onb_d-mHWks4YjQx",
    },
}

# ==================== ХРАНИЛИЩЕ ДАННЫХ ====================
user_purchases: Dict[int, List[Dict]] = {}

# ==================== FSM СОСТОЯНИЯ ====================
class PurchaseStates(StatesGroup):
    waiting_for_payment = State()

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# ==================== КЛАВИАТУРЫ ====================
def get_main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📦 КАТАЛОГ ПАКЕТОВ", callback_data="catalog")
    )
    builder.row(
        InlineKeyboardButton(text="ℹ️ ОПИСАНИЕ И ИНФО", callback_data="info")
    )
    builder.row(
        InlineKeyboardButton(text="🆘 ТЕХПОДДЕРЖКА", callback_data="support")
    )
    builder.row(
        InlineKeyboardButton(text="🛒 МОИ ПОКУПКИ", callback_data="my_purchases")
    )
    return builder.as_markup()

def get_catalog_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product_id, product in PRODUCTS.items():
        builder.row(
            InlineKeyboardButton(
                text=f"{product['emoji']} {product['name']} — {product['price_label']}",
                callback_data=f"buy_{product_id}"
            )
        )
    builder.row(
        InlineKeyboardButton(text="🔙 НАЗАД", callback_data="back_to_main")
    )
    return builder.as_markup()

def get_back_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 НАЗАД", callback_data="back_to_main")
    )
    return builder.as_markup()

def get_payment_confirm_keyboard(product_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    product = PRODUCTS[product_id]
    builder.row(
        InlineKeyboardButton(
            text=f"⭐️ Оплатить {product['price_label']}",
            callback_data=f"pay_{product_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(text="🔙 ОТМЕНА", callback_data="back_to_catalog")
    )
    return builder.as_markup()

# ==================== ОБРАБОТЧИКИ КОМАНД ====================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в CLOUD Store!\n\n"
        "Здесь ты можешь приобрести доступ к приватным архивам.\n"
        "Выбери интересующий раздел ниже:",
        reply_markup=get_main_menu()
    )

@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "🏠 ГЛАВНОЕ МЕНЮ CLOUD STORE\n\n"
        "Ты вернулся на главную. Выбери интересующий раздел ниже:",
        reply_markup=get_main_menu()
    )

# ==================== ОБРАБОТЧИКИ CALLBACK ====================
@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 ГЛАВНОЕ МЕНЮ CLOUD STORE\n\n"
        "Ты вернулся на главную. Выбери интересующий раздел ниже:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_catalog")
async def back_to_catalog(callback: CallbackQuery):
    await callback.message.edit_text(
        "📦 КАТАЛОГ ПАКЕТОВ\n\n"
        "Выбери подходящий тариф и нажми на кнопку для покупки:",
        reply_markup=get_catalog_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "catalog")
async def show_catalog(callback: CallbackQuery):
    await callback.message.edit_text(
        "📦 КАТАЛОГ ПАКЕТОВ\n\n"
        "Выбери подходящий тариф и нажми на кнопку для покупки:",
        reply_markup=get_catalog_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "info")
async def show_info(callback: CallbackQuery):
    info_text = (
        "📦 ПОДРОБНАЯ ИНФОРМАЦИЯ\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Мы открываем доступ к защищенным приватным папкам "
        "на быстрых серверах.\n\n"
        "🔥 Плюсы нашего сервиса:\n"
        "• Файлы хранятся вечно и не удаляются.\n"
        "• Регулярное добавление нового материала.\n"
        "• Никаких ежемесячных списаний — покупка разовая.\n"
        "• Полная конфиденциальность.\n\n"
        "💰 Наш прайс-лист:\n"
        "➕ Пакет 5 ГБ — 100 ⭐️ Stars\n"
        "➕ Пакет 10 ГБ — 250 ⭐️ Stars\n"
        "➕ Пакет 20 ГБ — 350 ⭐️ Stars"
    )
    await callback.message.edit_text(
        info_text,
        reply_markup=get_back_button()
    )
    await callback.answer()

@dp.callback_query(F.data == "support")
async def show_support(callback: CallbackQuery):
    support_text = (
        "🆘 ТЕХПОДДЕРЖКА\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Если у тебя возникли вопросы или проблемы:\n\n"
        "✉️ Напиши нам: @support_bot\n"
        "📧 Email: support@cloudstore.com\n\n"
        "Мы отвечаем в течение 24 часов!"
    )
    await callback.message.edit_text(
        support_text,
        reply_markup=get_back_button()
    )
    await callback.answer()

@dp.callback_query(F.data == "my_purchases")
async def show_my_purchases(callback: CallbackQuery):
    user_id = callback.from_user.id
    purchases = user_purchases.get(user_id, [])
    
    if not purchases:
        await callback.message.edit_text(
            "🛒 МОИ ПОКУПКИ\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "У тебя пока нет покупок.\n"
            "Перейди в каталог и выбери подходящий пакет!",
            reply_markup=get_back_button()
        )
        await callback.answer()
        return
    
    purchases_text = "🛒 МОИ ПОКУПКИ\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, purchase in enumerate(purchases, 1):
        purchases_text += (
            f"{i}. {purchase['emoji']} {purchase['name']}\n"
            f"   📅 {purchase['date']}\n"
            f"   💰 {purchase['price_label']}\n"
            f"   📎 Ссылка: {purchase['link']}\n\n"
        )
    
    await callback.message.edit_text(
        purchases_text,
        reply_markup=get_back_button()
    )
    await callback.answer()

# ==================== ПОКУПКА ТОВАРА ====================
@dp.callback_query(F.data.startswith("buy_"))
async def select_product(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[1]
    product = PRODUCTS.get(product_id)
    
    if not product:
        await callback.answer("Товар не найден!")
        return
    
    await state.update_data(product_id=product_id)
    await state.set_state(PurchaseStates.waiting_for_payment)
    
    product_text = (
        f"{product['emoji']} {product['name']}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Цена: {product['price_label']}\n"
        f"📦 Объём: {product['size']}\n\n"
        "После оплаты ты получишь доступ к архиву.\n"
        "Оплата происходит через Telegram Stars."
    )
    
    await callback.message.edit_text(
        product_text,
        reply_markup=get_payment_confirm_keyboard(product_id)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("pay_"), PurchaseStates.waiting_for_payment)
async def process_payment(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[1]
    product = PRODUCTS.get(product_id)
    
    if not product:
        await callback.answer("Товар не найден!")
        return
    
    await state.clear()
    
    prices = [LabeledPrice(label=product['name'], amount=product['price'])]
    
    try:
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title=f"Покупка {product['name']}",
            description=f"Доступ к архиву объёмом {product['size']}",
            payload=f"purchase_{product_id}_{callback.from_user.id}",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter="cloudstore_purchase",
            need_name=False,
            need_phone_number=False,
            need_email=False,
        )
        await callback.answer("💳 Отправлен счёт на оплату!")
    except Exception as e:
        logging.error(f"Payment error: {e}")
        await callback.answer("❌ Ошибка при создании счёта. Попробуйте позже.", show_alert=True)

# ==================== ОБРАБОТКА УСПЕШНОЙ ОПЛАТЫ ====================
@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    payment_info = message.successful_payment
    payload = payment_info.invoice_payload
    
    parts = payload.split("_")
    if len(parts) >= 2:
        product_id = parts[1]
    else:
        product_id = "5gb"
    
    product = PRODUCTS.get(product_id, PRODUCTS["5gb"])
    user_id = message.from_user.id
    
    purchase = {
        "product_id": product_id,
        "name": product["name"],
        "price": product["price"],
        "price_label": product["price_label"],
        "size": product["size"],
        "emoji": product["emoji"],
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "link": product["link"],
    }
    
    if user_id not in user_purchases:
        user_purchases[user_id] = []
    user_purchases[user_id].append(purchase)
    
    success_text = (
        "✅ ОПЛАТА ПРОШЛА УСПЕШНО!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎉 Ты приобрёл {product['emoji']} {product['name']}!\n\n"
        "🔗 Ссылка для скачивания архива:\n"
        f"{product['link']}\n\n"
        "📌 Ссылка также сохранена в разделе «МОИ ПОКУПКИ».\n\n"
        "Спасибо за покупку! ❤️"
    )
    
    await message.answer(
        success_text,
        reply_markup=get_main_menu()
    )
    
    try:
        await bot.send_message(
            ADMIN_ID,
            f"🛒 НОВАЯ ПОКУПКА!\n\n"
            f"👤 Пользователь: {message.from_user.full_name} (@{message.from_user.username})\n"
            f"🆔 ID: {user_id}\n"
            f"📦 Товар: {product['name']}\n"
            f"💰 Цена: {product['price_label']}\n"
            f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
    except Exception as e:
        logging.error(f"Admin notification error: {e}")

# ==================== ЗАПУСК БОТА ====================
async def main():
    logging.info("Бот CLOUD Store запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())