import random
from ruentrainerbot.db.models import Dictionary

def build_options(correct: Dictionary,
                   wrong: list[Dictionary]
                   ) -> tuple[list[str], int]:
    """
    Возвращает options, correct_index
    """
    options = [correct.en, *[w.en for w in wrong]]
    random.shuffle(options)
    correct_index = options.index(correct.en)
    return options, correct_index

def render_question_text(question_num: int,
                        total: int,
                        ru_word: str
                        ) -> str:
    """
    Рендерит вопрос
    """
    return (
        f'Вопрос {question_num}/{total}\n'
        f'Как переводится: {ru_word}?'
    )