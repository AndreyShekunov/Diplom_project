import sqlite3 as sq
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboard as kb

router = Router()


class product_add(StatesGroup):
    product_categories = State()
    product_name = State()
    product_description = State()
    product_price = State()
    product_image = State()


@router.message(Command("admin"))
async def comman_admin(message: Message):
    with sq.connect("app/data_base") as con:
        cursor = con.cursor()
        admin_info = cursor.execute(f"SELECT id FROM admin WHERE telegram_id = {message.from_user.id}").fetchone()

        if admin_info != None:
            message_info = cursor.execute(f"SELECT id, image_info, text_info FROM message_info WHERE id = 2").fetchone()

    await message.answer_photo(photo=message_info[1], caption=message_info[2], reply_markup=await kb.categories_admin())


@router.message(CommandStart())
async def comman_start(message: Message):
    with sq.connect("app/data_base") as con:
        cursor = con.cursor()
        message_info = cursor.execute(f"SELECT id, image_info, text_info FROM message_info WHERE id = 1").fetchone()

    await message.answer_photo(photo=message_info[1], caption=message_info[2],
                               reply_markup=await kb.categories_start())


"""
@router.message(F.photo)
async def get_photo(message: Message):
    await message.answer(message.photo[-1].file_id)
"""


@router.callback_query(F.data == "back_to_start")
async def callback_back_to_start(callback: CallbackQuery):
    with sq.connect("app/data_base") as con:
        cursor = con.cursor()
        message_info = cursor.execute(f"SELECT id, image_info, text_info FROM message_info WHERE id = 1").fetchone()

    await callback.message.answer_photo(photo=message_info[1], caption=message_info[2],
                                        reply_markup=await kb.categories_start())
    await callback.answer()


@router.callback_query(F.data == "buy_none")
async def callback_buy(callback: CallbackQuery):
    await callback.answer("Платежная система не предусмотренна", show_alert=True)


@router.callback_query(F.data.startswith("category_"))
async def callback_category(callback: CallbackQuery):
    category_num = callback.data.split("_")[1]

    with sq.connect("app/data_base") as con:
        cursor = con.cursor()
        callback_info = cursor.execute(f"SELECT name_info, call_info FROM categories WHERE id = 1").fetchall()

    for index, values in enumerate(callback_info):
        if category_num == callback_info[index][1]:
            with sq.connect("app/data_base") as con:
                cursor = con.cursor()
                product_info = cursor.execute(f"SELECT * FROM product WHERE "
                                              f"id_category = {callback_info[index][1]} ORDER BY RANDOM() LIMIT 1").fetchone()

            await callback.message.answer_photo(photo=product_info[2], caption=f"<b>Название:</b> {product_info[3]}\n"
                                                                               f"<b>Описание:</b> {product_info[4]}\n"
                                                                               f"<b>Цена:</b> {product_info[5]}",
                                                reply_markup=await kb.price_button(product_info[1]))
        await callback.answer()


@router.callback_query(F.data.startswith("show_"))
async def callback_show(callback: CallbackQuery):
    category_num = callback.data.split("_")[1]
    with sq.connect("app/data_base") as con:
        cursor = con.cursor()
        callback_info = cursor.execute(f"SELECT id_category FROM product").fetchall()

    for index, values in enumerate(callback_info):

        if category_num == str(callback_info[index][0]):
            with sq.connect("app/data_base") as con:
                cursor = con.cursor()
                product_info = cursor.execute(f"SELECT * FROM product WHERE "
                                              f"id_category = {callback_info[index][0]} ORDER BY RANDOM() LIMIT 1").fetchone()

            await callback.message.answer_photo(photo=product_info[2], caption=f"<b>Название:</b> {product_info[3]}\n"
                                                                               f"<b>Описание:</b> {product_info[4]}\n"

                                                                               f"<b>Цена:</b> {product_info[5]}",
                                                reply_markup=await kb.price_button(product_info[1]))
            break

        await callback.answer()


@router.callback_query(F.data.startswith("add_"))
async def callback_show(callback: CallbackQuery, state: FSMContext):
    category_num = callback.data.split("_")[1]
    with sq.connect("app/data_base") as con:
        cursor = con.cursor()
        callback_info = cursor.execute(f"SELECT id_category FROM product").fetchall()

    for index, values in enumerate(callback_info):

        if category_num == str(callback_info[index][0]):
            await state.set_state(product_add.product_categories)
            await state.update_data(product_categories=str(callback_info[index][0]))
            await state.set_state(product_add.product_name)
            await callback.message.answer("Введите название товара")

            break


@router.message(product_add.product_name)
async def get_product_name(message: Message, state: FSMContext):
    await state.update_data(product_name=message.text)
    await state.set_state(product_add.product_description)
    await message.answer("Введите описание товара")


@router.message(product_add.product_description)
async def get_product_desc(message: Message, state: FSMContext):
    await state.update_data(product_description=message.text)
    await state.set_state(product_add.product_price)
    await message.answer("Введите цену товара")


@router.message(product_add.product_price)
async def get_product_price(message: Message, state: FSMContext):
    await state.update_data(product_price=message.text)
    await state.set_state(product_add.product_image)
    await message.answer("Добавьте изображение товара")


@router.message(product_add.product_image, F.photo)
async def get_product_price(message: Message, state: FSMContext):
    await state.update_data(product_image=message.photo[-1].file_id)
    data = await state.get_data()

    category = data['product_categories']
    image = data['product_image']
    name = data['product_name']
    desc = data['product_description']
    price = data['product_price']

    with sq.connect("app/data_base") as con:
        cursor = con.cursor()
        cursor.execute(
            f"INSERT INTO product (id_category, image_product, name_product, description_product, price_product) "
            f"VALUES ('{category}', '{image}','{name}','{desc}','{price}')")

        message_info = cursor.execute(f"SELECT id, image_info, text_info FROM message_info WHERE id = 2").fetchone()

    await state.clear()
    await message.answer("Товар добавлен")
    await message.answer_photo(photo=message_info[1], caption=message_info[2], reply_markup=await kb.categories_admin())
