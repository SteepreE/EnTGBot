from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_back_keyboard():

    buttons = [
        KeyboardButton("Назад")
    ]

    return ReplyKeyboardMarkup(resize_keyboard=True).row(*buttons)


def get_pages_keyboard():

    buttons = [
        KeyboardButton("<"),
        KeyboardButton(">")
    ]

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(*buttons)
    keyboard.row(KeyboardButton("Выход"))

    return keyboard


def get_admin_keyboard():

    buttons = [
        KeyboardButton("/archive")
    ]

    return ReplyKeyboardMarkup(resize_keyboard=True).row(*buttons)


def get_user_keyboard():

    buttons = [
        KeyboardButton("Добавить обращение")
    ]

    return ReplyKeyboardMarkup(resize_keyboard=True).row(*buttons)
