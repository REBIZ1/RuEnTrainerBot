from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def quiz_options_kb(
        options: list[str],
        word_id: int,
    is_added: bool,
) -> InlineKeyboardMarkup:
    """
    Кнопки ответы и завершить
    """
    kb = InlineKeyboardBuilder()
    for i, opt in enumerate(options):
        kb.button(text=opt, callback_data=f'quiz:ans:{i}')
    if is_added:
        kb.button(text='✅ Добавлен', callback_data='quiz:noop')
        kb.button(text='➖ Удалить', callback_data=f'quiz:rm:{word_id}')
    else:
        kb.button(text='➕ Добавить', caYllback_data=f'quiz:add:{word_id}')
    kb.button(text='Завершить квиз', callback_data='quiz:stop')
    kb.adjust(2)
    return kb.as_markup()
