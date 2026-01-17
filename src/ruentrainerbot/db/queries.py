import sqlalchemy as sq
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from ruentrainerbot.db.models import Base, Dictionary, Users, UserWords
from sqlalchemy.dialects.postgresql import insert


async def create_tables(engine: AsyncEngine) -> None:
    """
    Создает таблицы
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_random_words(session: AsyncSession,
                           limit: int = 10
                           ) -> list[Dictionary]:
    """
    Возвращает случайные слова из таблицы words
    """
    stmt = (
        sq.select(Dictionary)
        .order_by(sq.func.random())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())

async def get_similar_wrong_words(session: AsyncSession,
                                  correct_word: Dictionary
                                  ) -> list[Dictionary]:
    """
    Возвращает неправильные варианты перевода
    """
    en = correct_word.en.lower()
    if len(en) >= 3:
        part = en[:3]
    else:
        part = en

    pattern = f'%{part}%'
    stmt = (
        sq.select(Dictionary)
        .where(
            Dictionary.id != correct_word.id,
            Dictionary.en.ilike(pattern),
        )
        .order_by(sq.func.random())
        .limit(3)
    )
    result = await session.execute(stmt)
    words = list(result.scalars().all())

    if len(words) < 3:
        need = 3 - len(words)

        fallback_stmt = (
            sq.select(Dictionary)
            .where(
                Dictionary.id != correct_word.id,
                Dictionary.id.notin_([w.id for w in words]) if words else sq.true(),
            )
            .order_by(sq.func.random())
            .limit(need)
        )
        fallback_result = await session.execute(fallback_stmt)
        words.extend(list(fallback_result.scalars().all()))
    return words

async def add_word_to_user(
        session: AsyncSession,
        user_id: int,
        word_id: int,
    ) -> None:
    """
    Добавляет слово в личный список пользователя:
    - создает пользователя, если его нет;
    - если запись user_words уже есть включаем обратно;
    - иначе создает новую.
    """
    await session.execute(
        insert(Users.__table__)
        .values(id=user_id)
        .on_conflict_do_nothing(index_elements=['id'])
    )

    stmt = (
        insert(UserWords.__table__)
        .values(user_id=user_id, word_id=word_id, is_active=True)
        .on_conflict_do_update(
            index_elements=['user_id', 'word_id'],
            set_={'is_active': True},
        )
    )
    await session.execute(stmt)
    await session.commit()

async def remove_word_from_user(
    session: AsyncSession,
    user_id: int,
    word_id: int,
    ) -> None:
    """
    Удаляет слово у пользователя
    """
    stmt = (
        sq.update(UserWords)
        .where(
            UserWords.user_id == user_id,
            UserWords.word_id == word_id,
            UserWords.is_active == True,
        )
        .values(is_active=False)
    )
    await session.execute(stmt)
    await session.commit()

async def get_user_active_words(
    session: AsyncSession,
    user_id: int,
    limit: int | None = None,
    ) -> list[Dictionary]:
    """
    Возвращает активные слова пользователя из его личного словаря.
    """
    stmt = (
        sq.select(Dictionary)
        .join(UserWords, UserWords.word_id == Dictionary.id)
        .where(
            UserWords.user_id == user_id,
            UserWords.is_active == True,
        )
        .order_by(sq.func.random())
    )
    if limit:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())

async def is_word_active_for_user(
    session: AsyncSession,
    user_id: int,
    word_id: int,
) -> bool:
    """
    Проверяет добавлено ли слово в активный личный словарь пользователя
    """
    stmt = (
        sq.select(UserWords.word_id)
        .where(
            UserWords.user_id == user_id,
            UserWords.word_id == word_id,
            UserWords.is_active == True,
        )
        .limit(1)
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none() is not None

