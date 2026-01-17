# RuEnTrainerBot

Бот для изучения английского языка.

## Возможности

- Пройти общий квиз;
- Пройти квиз по личным словам;
- Добавить слово в личный словарь;
- Удалить слово из личного словаря.

## Стек технологий 

- Python 3.12+;
- psycopg[binary] 3.3.2;
- aiogram 3.24.0;
- asyncpg 0.31.0;
- SQLAlchemy 2.0.45;
- pydantic-settings 2.12.0;
- structlog 25.5.0.

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone git@github.com:REBIZ1/RuEnTrainerBot.git
```

### 2. Создать виртуальное окружение

```bash
python -m venv .venv
```

#### Активировать окружение:

Windows:

```bash
.venv\Scripts\Activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install .
```

## Использование

### Запуск

```bash
python main.py
```



