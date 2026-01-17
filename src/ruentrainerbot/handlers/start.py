from aiogram import Router
from aiogram.filters import CommandStart
from aiogram import F
from aiogram.types import Message
from ruentrainerbot.core.logging import get_logger
from ruentrainerbot.keyboards.reply import main_menu_kb, BTN_START

router = Router()
logger = get_logger(__name__)

@router.message(CommandStart())
@router.message(F.text == BTN_START)
async def start_cmd(message: Message) -> None:
    """
    Обрабатывает команду /start
    """
    logger.info('Команда /start', text=message.text)
    await message.answer(
        'Привет! Я помогу тебе с изучением английских слов\n'
        'Нажми /quiz чтобы начать квиз\n'
        'Нажми /myquiz чтобы начать квиз по личным словам',
        reply_markup=main_menu_kb(),
    )