import os
import keyboards

from aiogram.dispatcher import FSMContext
from database import Database

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text

from loguru import logger

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMINS_LIST = [766903109, 1121822939]

storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)

messages_db = Database("database.db", "Messages")

get_content_id = {
    "text": lambda message: message.text,
    "photo": lambda message: message.photo[0].file_id,
    "voice": lambda message: message.voice.file_id,
    "video": lambda message: message.video.file_id,
    "document": lambda message: message.document.file_id,
    "audio": lambda message: message.audio.file_id
}

send_data = {
    "text": lambda user, text, caption: bot.send_message(user, text),
    "photo": lambda user, data_id, caption: bot.send_photo(user, data_id, caption),
    "voice": lambda user, data_id, caption: bot.send_voice(user, data_id, caption),
    "video": lambda user, data_id, caption: bot.send_video(user, data_id, caption),
    "document": lambda user, data_id, caption: bot.send_document(user, data_id, caption=caption),
    "audio": lambda user, data_id, caption: bot.send_audio(user, data_id, caption),
}


class TreatmentStates(StatesGroup):
    treatment = State()


class ArchiveStates(StatesGroup):
    archive = State()


@dp.message_handler(commands="start")
async def start_message(message: types.Message):
    try:
        if message.from_user.id in ADMINS_LIST:
            await message.reply("Добро пожаловать в архив",
                                reply_markup=keyboards.get_admin_keyboard())
        else:
            await bot.send_message(message.from_user.id,
                                   """⚡️Если вы столкнулись с противозаконной деятельностью энергетиков, расскажите о своей истории нашему чат-боту. Чем больше случаев, связанных с несправедливостью со стороны энергетиков и компании En+ Group, тем быстрее и эффективнее мы сможем обратить внимание проверяющих органов на данный правовой беспредел
    """, reply_markup=keyboards.get_user_keyboard())
    except Exception as e:
        logger.exception(e.args)


@dp.message_handler(commands="archive")
async def start_message(message: types.Message, state: FSMContext):
    try:
        if message.from_user.id in ADMINS_LIST:
            await ArchiveStates.archive.set()
            await state.update_data(page=0)
            await show_treatments(message, 0)
    except Exception as e:
        logger.exception(e.args)
        await message.answer(
            text="Что-то пошло не так, попробуйте снова!",
            reply_markup=keyboards.get_admin_keyboard())
        await state.finish()


@dp.message_handler(Text(equals=['<', '>']), state=ArchiveStates.archive)
async def change_page(message: types.Message, state: FSMContext):

    try:
        data = await state.get_data()
        page = data['page']

        if message.text == '<' and page > 0:
            page -= 1
        if message.text == '>':
            page += 1

        await state.update_data(page=page)

        if message.from_user.id in ADMINS_LIST:
            await show_treatments(message, page)
    except Exception as e:
        logger.exception(e.args)
        await message.answer(
            text="Что-то пошло не так, попробуйте снова!",
            reply_markup=keyboards.get_admin_keyboard())
        await state.finish()


@dp.message_handler(Text(equals='Выход'), state=ArchiveStates.archive)
async def exit_from_archive(message: types.Message, state: FSMContext):
    try:
        await state.finish()
        await message.reply("Вы вышли из архива", reply_markup=keyboards.get_admin_keyboard())
    except Exception as e:
        logger.exception(e.args)

    await state.finish()


async def show_treatments(message: types.Message, page: int):

    treatments = messages_db.get_orders_by_offset(page)

    for treatment in treatments:
        user_id = message.from_user.id
        data_type = treatment[2]
        data = treatment[3]
        caption = treatment[4]

        await send_data[data_type](user_id, data, caption)

    await bot.send_message(message.from_user.id,
                           f"Страница {page + 1}", reply_markup=keyboards.get_pages_keyboard())


@dp.message_handler()
async def treatment_start(message: types.Message):
    try:
        if message.text != "Добавить обращение":
            return

        await TreatmentStates.treatment.set()
        await bot.send_message(message.from_user.id, """⚡️Помните, ваше обращение должно быть одним сообщением: если у вас есть фото\видео\документ, то описание к нему должно быть прикреплено сразу
    
⚡️В конце обращения оставьте свои контакты, чтобы мы могли связать с вами
        """)
    except Exception as e:
        logger.exception(e.args)


@dp.message_handler(content_types=types.ContentTypes.ANY, state=TreatmentStates.treatment)
async def add_treatment(message: types.Message, state):
    try:
        content_type = message.content_type
        data_id = get_content_id[content_type](message)
        caption = message.caption
        user_id = message.from_user.id

        messages_db.add_new_message(content_type, data_id, caption, user_id)

        await message.answer(text="Сообщение добавлено в архив")
    except Exception as e:
        logger.exception(e.args)
        await message.answer(
            text="Что-то пошло не так, попробуйте снова!\nВозможно формат сообщения не поддерживается!",
            reply_markup=keyboards.get_user_keyboard())

    await state.finish()


def main():
    logger.add("logs.log", format="{time} {message}")

    executor.start_polling(dp)


if __name__ == '__main__':
    main()
