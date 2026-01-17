from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from ruentrainerbot.core.logging import get_logger
from ruentrainerbot.db.queries import (get_random_words, get_similar_wrong_words,
                                       is_word_active_for_user, get_user_active_words,
                                       add_word_to_user, remove_word_from_user)
from ruentrainerbot.db.session import AsyncSessionLocal
from ruentrainerbot.keyboards.quiz import quiz_options_kb
from ruentrainerbot.keyboards.reply import BTN_QUIZ, BTN_MY_QUIZ
from ruentrainerbot.utils.quiz import build_options, render_question_text

router = Router()
logger = get_logger(__name__)

TOTAL_QUESTIONS = 10


class QuizStates(StatesGroup):
    """
    FSM состояния для квиза
    """
    in_quiz = State()


async def _send_next_question(chat_id: int,
                              user_id: int,
                              bot,
                              state: FSMContext
                              ) -> None:
    """
    Отправляет следующий вопрос квиза или завершает квиз,
    если вопросы закончились
    """
    data = await state.get_data()
    words = data.get('words', [])
    idx = int(data.get('idx', 0))
    total = int(data.get('total', len(words)))
    score = int(data.get('score', 0))

    if idx >= total:
        percent = int((score / total) * 100) if total else 0
        logger.info(
            'Квиз завершен',
            total=total,
            score=score,
            percent=percent)
        await state.clear()
        await bot.send_message(
            chat_id,
            f'Квиз завершен\n'
            f'Результат: {percent}%',
        )
        return
    correct = words[idx]

    async with AsyncSessionLocal() as session:
        wrong = await get_similar_wrong_words(session, correct)
        added = await is_word_active_for_user(session, user_id=user_id, word_id=correct.id)
    options, correct_index = build_options(correct, wrong)

    await state.update_data(
        idx=idx,
        correct_word_id=correct.id,
        correct_ru=correct.ru,
        correct_en=correct.en,
        options=options,
        correct_index=correct_index,
    )
    text = render_question_text(idx + 1, total, correct.ru)
    logger.info(
        'Отправлен вопрос для квиза',
        question_index=idx,
        total=total,
        correct_word_id=correct.id,
        correct_en=correct.en,
        is_added=added,
    )
    await bot.send_message(
        chat_id,
        text,
        reply_markup=quiz_options_kb(options, word_id=correct.id, is_added=added)
    )


async def _start_quiz_with_words(
        message: Message,
        state: FSMContext,
        words, mode: str
) -> None:
    """
    Инициализирует квиз с заданным набором слов
    и отправляет первый вопрос
    """
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not words:
        logger.warning(
            'Список слов пользователя пуст',
            mode=mode
        )
        await message.answer('У тебя пока нет слов '
                             '\nДобавляй слова во время квиза кнопкой «➕ Добавить»')
        return

    await state.set_state(QuizStates.in_quiz)
    await state.set_data(
        {
            'mode': mode,
            'words': words,
            'idx': 0,
            'total': min(TOTAL_QUESTIONS, len(words)),
            'score': 0,
        }
    )

    logger.info('Квиз запущен', mode=mode, total=len(words))
    await _send_next_question(chat_id=chat_id, user_id=user_id, bot=message.bot, state=state)


@router.message(Command('quiz'))
@router.message(F.text == BTN_QUIZ)
async def quiz_cmd(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /quiz
    Запускает квиз со случайными словами из словаря
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    logger.info('Команда quiz')
    try:
        async with AsyncSessionLocal() as session:
            words = await get_random_words(session, limit=TOTAL_QUESTIONS)
        if not words:
            logger.warning('Нет слов в словаре')
            await message.answer('Пока нет слов в словаре')
            return

        await state.set_state(QuizStates.in_quiz)
        await state.set_data(
            {
                'words': words,
                'idx': 0,
                'total': min(TOTAL_QUESTIONS, len(words)),
                'score': 0,
            }
        )
        logger.info('quiz_started', total=len(words))

        await _send_next_question(chat_id=chat_id, user_id=user_id, bot=message.bot, state=state)
    except Exception:
        logger.exception('Ошибка запуска квиза')
        await message.answer('Ошибка при запуске квиза!')


@router.message(Command('myquiz'))
@router.message(F.text == BTN_MY_QUIZ)
async def my_quiz_cmd(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /myquiz
    Запускает персональный квиз со словами пользователя
    """
    user_id = message.from_user.id
    logger.info('Команда quiz', mode='personal')

    try:
        async with AsyncSessionLocal() as session:
            words = await get_user_active_words(session, user_id=user_id, limit=TOTAL_QUESTIONS)
        await _start_quiz_with_words(message, state, words, mode='personal')
    except Exception:
        logger.exception('Ошибка запуска квиза', mode='personal')
        await message.answer('Ошибка при запуске квиза')


@router.callback_query(lambda c: c.data == 'quiz:noop')
async def quiz_noop(call: CallbackQuery) -> None:
    """
    Callback заглушка для кнопки,
    когда слово уже добавлено пользователю
    """
    await call.answer('Уже в личном словаре', show_alert=False)


@router.callback_query(lambda c: c.data == 'quiz:stop')
async def quiz_stop(call: CallbackQuery, state: FSMContext) -> None:
    """
    Останавливает активный квиз по запросу пользователя
    и показывает текущий результат
    """
    data = await state.get_data()
    score = int(data.get('score', 0))
    total = int(data.get('total', 0))
    logger.info(
        'Квиз остановлен пользователем',
        score=score,
        total=total
    )

    await state.clear()
    await call.answer('Остановлено')
    if call.message:
        percent = int((score / total) * 100) if total else 0
        await call.message.edit_text(
            f'Квиз остановлен\n'
            f'Результат: {score}/{total} ({percent}%)'
        )


@router.callback_query(lambda c: c.data and c.data.startswith('quiz:add:'))
async def quiz_add_word(call: CallbackQuery, state: FSMContext) -> None:
    """
    Добавляет слово из квиза в личный словарь пользователя
    """
    user_id = call.from_user.id

    try:
        word_id = int(call.data.split(':')[-1])
        logger.info('Запрос на добавление слова', word_id=word_id)

        async with AsyncSessionLocal() as session:
            await add_word_to_user(session, user_id=user_id, word_id=word_id)

        data = await state.get_data()
        options = data.get('options', [])
        if call.message:
            await call.message.edit_reply_markup(
                reply_markup=quiz_options_kb(options, word_id=word_id, is_added=True)
            )

        logger.info('user_word_added', word_id=word_id)
        await call.answer('Добавлено ➕')

    except Exception:
        logger.exception('Ошибка при добавлении слова')
        await call.answer('Ошибка при добавлении слова')


@router.callback_query(lambda c: c.data and c.data.startswith('quiz:rm:'))
async def quiz_remove_word(call: CallbackQuery, state: FSMContext) -> None:
    """
    Удаляет слово из личного словаря пользователя
    """
    user_id = call.from_user.id

    try:
        word_id = int(call.data.split(':')[-1])
        logger.info('user_word_remove_requested', word_id=word_id)

        async with AsyncSessionLocal() as session:
            await remove_word_from_user(session, user_id=user_id, word_id=word_id)

        data = await state.get_data()
        options = data.get('options', [])
        if call.message:
            await call.message.edit_reply_markup(
                reply_markup=quiz_options_kb(options, word_id=word_id, is_added=False)
            )

        logger.info('user_word_removed', word_id=word_id)
        await call.answer('Удалено ➖')
    except Exception:
        logger.exception('Ошибка при удалении слова')
        await call.answer('Ошибка при удалении слова')


@router.callback_query(lambda c: c.data and c.data.startswith('quiz:ans:'))
async def quiz_answer(call: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает ответ пользователя на вопрос квиза,
    обновляет счет и отправляет следующий вопрос
    """
    user_id = call.from_user.id
    chat_id = call.message.chat.id if call.message else None
    try:
        if await state.get_state() != QuizStates.in_quiz:
            logger.warning('Квиз не активен')
            await call.answer('Квиз не активен')
            return
        data = await state.get_data()
        idx = int(data.get('idx', 0))
        total = int(data.get('total', 0))
        score = int(data.get('score', 0))

        options = data.get('options', [])
        correct_index = int(data.get('correct_index', -1))
        correct_en = data.get('correct_en')
        picked_index = int(call.data.split(':')[-1])
        picked_value = options[picked_index] if 0 <= picked_index < len(options) else None
        is_correct = picked_index == correct_index

        logger.info(
            'quiz_answer_received',
            question_index=idx,
            total=total,
            picked_index=picked_index,
            picked_value=picked_value,
            correct_index=correct_index,
            correct_en=correct_en,
            is_correct=is_correct,
        )

        if is_correct:
            score += 1
            await state.update_data(score=score)
            toast = '✅ Верно!'
            text = f'✅ Верно! Ответ: {correct_en}'
        else:
            toast = '❌ Неверно!'
            text = f'❌ Неверно. Правильный ответ: {correct_en}'

        await call.answer(toast)
        if call.message:
            await call.message.edit_text(text)
        await state.update_data(idx=idx + 1)
        await _send_next_question(chat_id=chat_id, user_id=user_id, bot=call.bot, state=state)
    except Exception:
        logger.exception('не удалось ответить на тест', user_id=user_id, chat_id=chat_id)
        await call.answer('не удалось ответить на тест')