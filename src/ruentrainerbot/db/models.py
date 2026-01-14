import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Dictionary(Base):
    __tablename__ = 'words'
    id = sq.Column(sq.Integer, primary_key=True)
    ru = sq.Column(sq.String(length=50), nullable=False)
    en = sq.Column(sq.String(length=50), nullable=False)
    created_at = sq.Column(sq.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = sq.Column(sq.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user_words = relationship('UserWords', back_populates='word', cascade='all, delete-orphan')

    __table_args__ = (
        sq.UniqueConstraint('ru', name='uq_words_ru'),
        sq.UniqueConstraint('en', name='uq_words_en')
    )

    def __str__(self):
        return f'{self.ru} | {self.en}'


class Users(Base):
    __tablename__ = 'users'
    id = sq.Column(sq.BigInteger, primary_key=True)
    created_at = sq.Column(sq.DateTime(timezone=True), server_default=func.now(), nullable=False)
    words = relationship('UserWords', back_populates='user', cascade='all, delete-orphan')

    def __str__(self):
        return f'id {self.id} | {self.created_at}'


class UserWords(Base):
    __tablename__ = 'user_words'
    user_id = sq.Column(
        sq.BigInteger,
        sq.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    word_id = sq.Column(
        sq.Integer,
        sq.ForeignKey('words.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    added_at = sq.Column(sq.DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = sq.Column(sq.Boolean, nullable=False, server_default=sq.true())
    user = relationship('Users', back_populates='words')
    word = relationship('Dictionary', back_populates='user_words')

    def __str__(self):
        return f'Пользователь {self.user_id} | Слово {self.word_id}'

