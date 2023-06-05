from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import PollAnswer

import config
import logging
import sqlite3
from aiogram.dispatcher.storage import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from states import Form, Delivery
from random import choice
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# Меню команд
async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("findteams", "Найти команду"),
        types.BotCommand("activities", "Мероприятия")
    ])


# Приветствие
@dp.message_handler(commands=['start'])
async def hello(message: types.Message):
    actions = types.InlineKeyboardMarkup()
    opportunities = types.InlineKeyboardButton(text='Что здесь можно сделать?', callback_data='opportunities')
    actions.add(opportunities)
    await authorization(user_id=message.from_user.id, user_username=message.from_user.username)
    await message.answer('Привет! Это чат-бот платформы Nyteam. Он позволит тебе заниматься нетворкингом с '
                         'людьми из любых сообществ', reply_markup=actions)


# Добавляем id и username пользователя в базу данных
async def authorization(user_id, user_username):
    try:
        conn = sqlite3.connect('Nyteam_base.db')
        cur = conn.cursor()
        cur.execute(f'INSERT INTO users(id, name) VALUES({user_id}, "@{user_username}")')
        conn.commit()
    except Exception as e:
        print(e)


# Добавляем в БД данные о сообществах пользователя
async def update_user(user_id, genres):
    conn = sqlite3.connect('Nyteam_base.db')
    cur = conn.cursor()
    cur.execute(f'UPDATE users SET genres = "{str(genres)}" WHERE id = {user_id}')
    conn.commit()


# help
@dp.message_handler(commands=['help'])
async def hello(message: types.Message):
    actions = types.InlineKeyboardMarkup()
    opportunities = types.InlineKeyboardButton(text='Что здесь можно сделать?', callback_data='opportunities')
    actions.add(opportunities)
    await message.answer('''Пользоваться ботом не сложно. Просто вызывай команды через "/", нажимай на появляющиеся кнопки и пиши то, что просит бот!
    Команды:
    /start - Запуск бота
    /help - Получение справочной информации (это сообщение)
    /findteams - Найти команду
    /activities - Узнать о мероприятиях
    Свои вопросы и предложения можно писать разработчику: @Sanechka_samb
    ''', reply_markup=actions)


# Что-то о возможностях бота
@dp.callback_query_handler(text="opportunities")
async def opportunities(call: types.CallbackQuery):

    actions = types.InlineKeyboardMarkup()
    button_2 = types.InlineKeyboardButton(text="Найти команду", callback_data="findteams")
    button_3 = types.InlineKeyboardButton(text="Узнать о мероприятиях", callback_data="activities")
    button_4 = types.InlineKeyboardButton(text="Пройти тесты", callback_data="get_booky")

    actions.add(button_2)
    actions.add(button_3)
    actions.add(button_4)

    await call.message.answer('Здесь ты можешь: \n• Собрать команду для проекта\n• Узнать о мероприятиях сообществ \n'
                              '• Проходить тестирования на уровень знаний\n• Познакомиться с интересными людьми '
                              '\n• Провести опрос для любой аудитории', reply_markup=actions)
    await call.answer()


# Узнаем об интересах пользователя
@dp.message_handler(commands=['findteams'])
async def poll_handler(message: types.Message):
    await message.answer_poll('Чем ты занимаешься/хочешь заниматься? Отмечай, а после получай рекомендации командой '
                              '/activities',
                              ['IT', 'Волонтерство', 'Бизнес', 'Ищу друзей', 'Собираю команду для олимпиады', 'Другое'],
                         is_anonymous=False, allows_multiple_answers=True)


@dp.poll_answer_handler()
async def result_genres(quiz_answer: PollAnswer):
    answers = {'0': 'IT', '1': 'Волонтерство', '2': 'Бизнес', '3': 'Ищу друзей', '4': 'Собираю команду для олимпиады',
               '5': 'Другое'}
    for answer in quiz_answer.option_ids:
        res = answers[str(answer)]
    print('jhygfd')
    await update_user(user_id=quiz_answer.user.id, genres=res)


@dp.callback_query_handler(text='activities')
async def events(call: types.CallbackQuery):
    actions = types.InlineKeyboardMarkup()
    n1 = types.InlineKeyboardButton(text="Хочу на нетворкинг-встречу", callback_data="n1")
    n2 = types.InlineKeyboardButton(text="Хочу на Спектакль", callback_data="n2")
    n3 = types.InlineKeyboardButton(text="Хочу на мастеркласс", callback_data="n3")
    back_button = types.InlineKeyboardButton(text="Назад", callback_data="opportunities")
    actions.add(back_button)
    actions.add(n1)
    actions.add(n2)
    actions.add(n3)
    await call.message.answer('На данный момент в Вашей библиотеке открыта регистрация на следующие мероприятия: \n'
                              '• Мероприятие "Нетворкинг-встреча...". Дата: 23.07.2023, 14:00\n'
                              '• Спектакль "Забыть Герострата". Дата: 30.07.2023, 19:00\n'
                              '• Мастеркласс в технике оригамми "Весенние цветы". Дата: 1.09.2023, 13:00',
                              reply_markup=actions)
    await call.answer()


@dp.callback_query_handler(text="n1")
async def event1(call: types.CallbackQuery):
    actions = types.InlineKeyboardMarkup()
    remove = types.InlineKeyboardButton(text="Отказаться от участия", callback_data='remove')
    actions.add(remove)
    await call.message.answer('Вы зарегистрированы на мероприятие "Нетворкинг-встреча...""\n'
                              'Дата и время: 23.07.2023, 14:00\nНе опаздывайте!', reply_markup=actions)
    await call.answer()


@dp.callback_query_handler(text="n2")
async def event2(call: types.CallbackQuery):
    actions = types.InlineKeyboardMarkup()
    remove = types.InlineKeyboardButton(text="Отказаться от участия", callback_data='remove')
    actions.add(remove)
    await call.message.answer('Вы зарегистрированы на мероприятие "Спектакль "Забыть Герострата""\n'
                              'Дата и время: 30.04.2023, 19:00\nНе опаздывайте!', reply_markup=actions)
    await call.answer()


@dp.callback_query_handler(text="n3")
async def event3(call: types.CallbackQuery):
    actions = types.InlineKeyboardMarkup()
    remove = types.InlineKeyboardButton(text="Отказаться от участия", callback_data='remove')
    actions.add(remove)
    await call.message.answer('Вы зарегистрированы на мероприятие "Нетворкинг-встреча ...""\n'
                              'Дата и время: 1.07.2023, 13:00\nНе опаздывайте!', reply_markup=actions)
    await call.answer()


@dp.callback_query_handler(text="remove")
async def remove(call: types.CallbackQuery):
    await call.message.answer('Ваша заявка на участие отменена!')
    await call.answer()


@dp.callback_query_handler(text="get_booky")
async def get_booky(call: types.CallbackQuery):
    actions = types.InlineKeyboardMarkup()
    vk = types.InlineKeyboardButton(text="IT",  url='https://forms.gle/RZEpp5im18WQ6Q9V6')
    booky = types.InlineKeyboardButton(text="Бизнес",  url='https://forms.gle/RZEpp5im18WQ6Q9V6')
    back_button = types.InlineKeyboardButton(text="Назад", callback_data="opportunities")
    actions.add(vk)
    actions.add(booky)
    actions.add(back_button)
    await call.message.answer('Выбирай интересующие тебя тесты!', reply_markup=actions)
    await call.answer()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
