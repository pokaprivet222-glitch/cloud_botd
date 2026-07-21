import asyncio
import logging
from datetime import datetime
from typing import Dict, List

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ==================== КОНФИГУРАЦИЯ ====================
BOT_TOKEN = "8759230800:AAEKHtJUig9XKBC6nIxzA41paGa163ZXBRc"
ADMIN_ID = 8891314013

# ==================== ТОВАРЫ ====================
PRODUCTS = {
    "5gb": {
        "id": "5gb",
        "name": "Пакет 5 ГБ",
        "price_label": "100 Stars",
        "size": "5 ГБ",
        "emoji": "🎉",
        "payment_link": "https://t.me/+e0coxbzyAWFjYzk5",
        "archive_link": "https://example.com/archive_5gb.zip"
    },
    "10gb": {
        "id": "10gb",
        "name": "Пакет 10 ГБ",
        "price_label": "250 Stars",
        "size": "10 ГБ",
        "emoji": "🎉",
        "payment_link": "https://t.me/+rpeY-cXDOpg5OTMx",
        "archive_link": "https://example.com/archive_10gb.zip"
    },
    "20gb": {
        "id": "20gb",
        "name": "Пакет 20 ГБ",
        "price_label": "350 Stars",
        "size": "20 ГБ",
        "emoji": "🎉",
        "payment_link": "https://t.me/+onb_d-mHWks4YjQx",
        "archive_link": "https://example.com/archive_20gb.zip"
    },
}

# ==================== ХРАНИЛИЩЕ ДАННЫХ ====================
user_purchases: Dict[int, List[Dict]] = {}

# ==================== FSM ДЛЯ ПОДДЕРЖКИ ====================
class SupportStates(StatesGroup):
    waiting_for_ticket = State()

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# ==================== КЛАВИАТУРЫ ====================
def get_main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📦 КАТАЛОГ ПАКЕТОВ", callback_data="catalog"))
    builder.row(InlineKeyboardButton(text="ℹ️ ОПИСАНИЕ И ИНФО", callback_data="info"))
    builder.row(InlineKeyboardButton(text="🆘 ТЕХПОДДЕРЖКА", callback_data="support"))
    builder.row(InlineKeyboardButton(text="🛒 МОИ ПОКУПКИ", callback_data="my_purchases"))
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
    builder.row(InlineKeyboardButton(text="🔙 НАЗАД", callback_data="back_to_main"))
    return builder.as_markup()

def get_payment_keyboard(product_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    product = PRODUCTS[product_id]
    builder.row(
        InlineKeyboardButton(text="⭐️ ОПЛАТИТЬ И ВСТУПИТЬ", url=product["payment_link"])
    )
    builder.row(
        InlineKeyboardButton(text="🔙 НАЗАД К КАТАЛОГУ", callback_data="back_to_catalog")
    )
    return builder.as_markup()

def get_support_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✍️ НАПИСАТЬ ТИКЕТ", callback_data="write_ticket"))
    builder.row(InlineKeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"))
    return builder.as_markup()

def get_back_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 НАЗАД", callback_data="back_to_main"))
    return builder.as_markup()

# ==================== ОБРАБОТЧИКИ КОМАНД ====================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Приветственное сообщение с кнопками"""
    welcome_text = (
        "🌟 ДОБРО ПОЖАЛОВАТЬ В CLOUD STORE!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📁 Премиум Архивы Контента\n\n"
        "🔥 Что мы предлагаем:\n"
        "• Эксклюзивная коллекция — только лучший и проверенный контент.\n"
        "• Разовая оплата — доступ навсегда, без скрытых списаний.\n"
        "• Мгновенная выдача — ссылка приходит сразу после оплаты.\n"
        "• Круглосуточная поддержка — поможем в любой ситуации.\n\n"
        "👇 Выбери нужный раздел:"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📦 ОТКРЫТЬ КАТАЛОГ", callback_data="catalog")
    )
    builder.row(
        InlineKeyboardButton(text="ℹ️ ОПИСАНИЕ И ИНФО", callback_data="info"),
        InlineKeyboardButton(text="🆘 ТЕХПОДДЕРЖКА", callback_data="support")
    )
    builder.row(
        InlineKeyboardButton(text="🛒 МОИ ПОКУПКИ", callback_data="my_purchases")
    )
    
    await message.answer(welcome_text, reply_markup=builder.as_markup())

@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "🏠 ГЛАВНОЕ МЕНЮ CLOUD STORE\n\n"
        "Ты вернулся на главную. Выбери интересующий раздел ниже:",
        reply_markup=get_main_menu()
    )

# ==================== ОБРАБОТЧИКИ КНОПОК ====================
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
    await callback.message.edit_text(info_text, reply_markup=get_back_button())
    await callback.answer()

@dp.callback_query(F.data == "support")
async def show_support(callback: CallbackQuery):
    support_text = (
        "🆘 ТЕХПОДДЕРЖКА CLOUD STORE\n\n"
        "Возникли трудности со скачиванием, оплатой или есть предложение?\n\n"
        "Опиши свой вопрос подробно, и наш саппорт ответит тебе прямо сюда в течение 15-30 минут."
    )
    await callback.message.edit_text(support_text, reply_markup=get_support_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "write_ticket")
async def write_ticket(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✍️ НАПИСАТЬ ТИКЕТ\n\n"
        "Опиши свою проблему или вопрос максимально подробно.\n"
        "Наш саппорт ответит тебе в ближайшее время.\n\n"
        "Отправь сообщение с описанием:"
    )
    await state.set_state(SupportStates.waiting_for_ticket)
    await callback.answer()

@dp.message(SupportStates.waiting_for_ticket)
async def process_ticket(message: Message, state: FSMContext):
    ticket_text = (
        f"📩 НОВЫЙ ТИКЕТ!\n\n"
        f"👤 От: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"📝 Сообщение:\n{message.text}"
    )
    await bot.send_message(ADMIN_ID, ticket_text)
    await message.answer(
        "✅ Ваш тикет отправлен! Саппорт ответит вам в ближайшее время.",
        reply_markup=get_back_button()
    )
    await state.clear()

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
        )
    
    await callback.message.edit_text(purchases_text, reply_markup=get_back_button())
    await callback.answer()

# ==================== ПОКУПКА ТОВАРА ====================
@dp.callback_query(F.data.startswith("buy_"))
async def select_product(callback: CallbackQuery):
    product_id = callback.data.split("_")[1]
    product = PRODUCTS.get(product_id)
    
    if not product:
        await callback.answer("Товар не найден!")
        return
    
    payment_text = (
        f"⭐️ ОПЛАТА ЧЕРЕЗ TELEGRAM STARS\n\n"
        f"Товар: {product['emoji']} {product['name']}\n"
        f"Стоимость: {product['price_label']}\n\n"
        f"📌 Инструкция:\n"
        f"1. Нажмите кнопку «ОПЛАТИТЬ И ВСТУПИТЬ».\n"
        f"2. Оплатите звёздами при вступлении в канал.\n"
        f"3. После оплаты бот автоматически выдаст ссылку на архив!"
    )
    
    await callback.message.edit_text(
        payment_text,
        reply_markup=get_payment_keyboard(product_id)
    )
    await callback.answer()

# ==================== АВТОВЫДАЧА (СИМУЛЯЦИЯ) ====================
@dp.callback_query(F.data.startswith("auto_confirm_"))
async def auto_confirm_payment(callback: CallbackQuery):
    product_id = callback.data.split("_")[2]
    product = PRODUCTS.get(product_id)
    user_id = callback.from_user.id
    
    if not product:
        await callback.answer("Товар не найден!")
        return
    
    purchase = {
        "product_id": product_id,
        "name": product["name"],
        "price_label": product["price_label"],
        "size": product["size"],
        "emoji": product["emoji"],
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "archive_link": product["archive_link"],
    }
    
    if user_id not in user_purchases:
        user_purchases[user_id] = []
    user_purchases[user_id].append(purchase)
    
    await callback.message.edit_text(
        f"✅ ОПЛАТА ПРОШЛА УСПЕШНО!\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎉 Ты приобрёл {product['emoji']} {product['name']}!\n\n"
        f"🔗 Ссылка для скачивания архива:\n"
        f"{product['archive_link']}\n\n"
        f"📌 Ссылка также сохранена в разделе «МОИ ПОКУПКИ».\n\n"
        f"Спасибо за покупку! ❤️",
        reply_markup=get_main_menu()
    )
    
    try:
        await bot.send_message(
            ADMIN_ID,
            f"🛒 НОВАЯ ПОКУПКА!\n\n"
            f"👤 Пользователь: {callback.from_user.full_name} (@{callback.from_user.username})\n"
            f"🆔 ID: {user_id}\n"
            f"📦 Товар: {product['name']}\n"
            f"💰 Цена: {product['price_label']}\n"
            f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
    except Exception as e:
        logging.error(f"Admin notification error: {e}")
    
    await callback.answer("✅ Покупка подтверждена!")

# ==================== ЗАПУСК ====================
async def main():
    logging.info("Бот CLOUD Store запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
