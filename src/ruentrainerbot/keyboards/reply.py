from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BTN_START = "Старт"
BTN_QUIZ = "Квиз"
BTN_MY_QUIZ = "Мой квиз"


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_START)],
            [KeyboardButton(text=BTN_QUIZ), KeyboardButton(text=BTN_MY_QUIZ)],
        ],
        resize_keyboard=True,
        selective=True,
    )
