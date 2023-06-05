from aiogram.dispatcher.filters.state import StatesGroup, State


class Form(StatesGroup):
    Genres = State()


class Delivery(StatesGroup):
    Book_title = State()
    Address = State()