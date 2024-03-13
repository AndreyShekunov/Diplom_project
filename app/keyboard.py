from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import sqlite3 as sq


async def categories_admin():
    with sq.connect("app/data_base") as con:
        cursor = con.cursor()
        categories_info = cursor.execute(f"SELECT name_info, call_info FROM categories WHERE id = 1").fetchall()

    keyboard = InlineKeyboardBuilder()

    for index, values in enumerate(categories_info):
        keyboard.add(
            InlineKeyboardButton(text=categories_info[index][0], callback_data=f"add_{categories_info[index][1]}"))
    return keyboard.adjust(3).as_markup()


async def categories_start():
    with sq.connect("app/data_base") as con:
        cursor = con.cursor()
        categories_info = cursor.execute(f"SELECT name_info, call_info FROM categories WHERE id = 1").fetchall()

    keyboard = InlineKeyboardBuilder()

    for index, values in enumerate(categories_info):
        keyboard.add(
            InlineKeyboardButton(text=categories_info[index][0], callback_data=f"category_{categories_info[index][1]}"))
    return keyboard.adjust(3).as_markup()


async def price_button(text):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Посмотреть еще 🔄", callback_data=f"show_{text}"))
    keyboard.add(InlineKeyboardButton(text="Купить 🛍", callback_data="buy_none"))
    keyboard.add(InlineKeyboardButton(text="Назад ↩️", callback_data="back_to_start"))
    return keyboard.adjust(1).as_markup()
