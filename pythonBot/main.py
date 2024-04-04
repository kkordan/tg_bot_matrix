from config import TOKEN
import text

import re
import sqlite3 as sq
from aiogram import types, Dispatcher, executor, Bot

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.markdown import hlink
import datetime
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)
conn = sq.connect('TG_BOT_MATRIX.db')
cursor = conn.cursor()


#Менюшка с кнопками
get_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

item1 = types.KeyboardButton('Инструкция⚙')
item2 = types.KeyboardButton('Я водитель🚘')
item3 = types.KeyboardButton('Я попутчик🧍🏻🎒')
get_kb.add(item1, item2, item3)

xyi = types.ReplyKeyboardMarkup(resize_keyboard=True)
xyi.row("на Главную")


@dp.message_handler(commands=['Отменить поиск', 'Отменить создание'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):

    await state.finish()
    await message.reply('Успешно выполнено!', reply_markup=get_kb)


@dp.message_handler(text="на Главную")
async def with_puree(message: types.Message, state: FSMContext):
    await message.reply('Вы вернулись в меню', reply_markup=get_kb)
    await state.finish()


async def send_message_to_user(user_id: int, text: str):
    await bot.send_message(user_id, text)


@dp.message_handler(commands=['start'])
async def startap(message: types.Message):

    user_name = message.from_user.first_name
    user_id = message.from_user.id
    await bot.send_sticker(message.from_user.id, sticker= "CAACAgIAAxkBAAEENjxl_IUljeYelBgwsc8ONsw8YzWRgAACkgEAAladvQqf0C0IQi7VBTQE" )
    await message.reply(f'<em>Привет,{user_name}👋🏻\nДобро пожаловать в бота для организации работы сервиса попутчиков</em>', parse_mode='HTML', reply_markup = get_kb)


@dp.message_handler(text="Я водитель🚘")
async def vodila(message: types.Message):
    global keyboard_vod
    keyboard_vod = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_vod.row("Создать новую поездку📝")
    keyboard_vod.row("Мои поездки🗺", "Мoй профиль🔐")
    keyboard_vod.row("на Главную")

    await message.reply('Выберите пункт в меню⬇️', reply_markup=keyboard_vod)


@dp.message_handler(text="Мoй профиль🔐")
async def vodila_profile(message: types.Message):
    global keyboard_vod_profile
    keyboard_vod_profile = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_vod_profile.row("на Главную")

    await message.reply('✅Ваши персональные данные:  \n \n'
                        'ФИО: [данные о водителе] \n  \n'
                        'Год рождения: [дд.мм.гггг]  \n \n'
                        'Номер телефона: [00000000000] \n \n'
                        'Данные автомобиля:  \n \n'
                        'Марка автомобиля: […]  \n \n'
                        'Модель автомобиля: […]  \n \n'
                        'Гос.номер: [Ф000ФФ]  \n \n'
                        'Стаж вождения: [00]  \n \n'
                        'Фото автомобиля […]', reply_markup=keyboard_vod_profile)


@dp.message_handler(text="Мои поездки🗺")
async def vodila_trip(message: types.Message):
    global keyboard_vod_trip
    keyboard_vod_trip = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_vod_trip.row("на Главную")

    await message.reply('Ваши поездки:', reply_markup=keyboard_vod_trip)


class CreateTripStates(StatesGroup):
    waiting_for_createtrip_point_departure = State()
    waiting_for_createtrip_point_arrival = State()
    waiting_for_createtrip_date_departure = State()
    waiting_for_createtrip_time_departure = State()
    waiting_for_createtrip_time_arrival = State()
    waiting_for_createtrip_number_of_seats = State()
    waiting_for_createtrip_extra_options = State()
    waiting_for_createtrip_savecreate = State()


@dp.message_handler(text="Создать новую поездку📝")
async def Create_trip(message: types.Message, state: FSMContext):

    global keyboard_create_trip
    keyboard_create_trip = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_create_trip.row("на Главную")

    await message.answer('📍Укажите точку отправления:', reply_markup=keyboard_create_trip)

    await CreateTripStates.waiting_for_createtrip_point_departure.set()


@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_point_departure)
async def Create_trip_point_departure (message: types.Message, state: FSMContext):
    if message.text == "на Главную":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['Create_trip_departure'] = message.text
        await message.answer("📍Укажите точку прибытия:")
        await CreateTripStates.waiting_for_createtrip_point_arrival.set()


@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_point_arrival)
async def Create_trip_point_arrival (message: types.Message, state: FSMContext):
    if message.text == "на Главную":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['Create_trip_arrival'] = message.text
        await message.answer("📆Выберите подходящую дату поездки:", reply_markup=get_date_keyboard())
        await CreateTripStates.waiting_for_createtrip_date_departure.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('date_'), state=CreateTripStates.waiting_for_createtrip_date_departure)
async def Create_trip_date(callback_query: CallbackQuery, state: FSMContext):
    date_str = callback_query.data[5:]
    async with state.proxy() as data:
        data['Create_trip_date_departure'] = date_str
    await CreateTripStates.waiting_for_createtrip_time_departure.set()
    await bot.send_message(callback_query.from_user.id, f'📆Вы выбрали дату: {date_str}')
    await bot.send_message(callback_query.from_user.id, '⏰Укажите время отправления:')



@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_time_departure)
async def Create_trip_time_departure (message: types.Message, state: FSMContext):
    if message.text == "на Главную":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()
    else:
        await message.answer("Укажите время прибытия УБРАТЬ:")
        async with state.proxy() as data:
            data['Create_trip_time_departure'] = message.text
        await  CreateTripStates.waiting_for_createtrip_time_arrival.set()


@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_time_arrival)
async def Create_trip_time_arrive(message: types.Message, state: FSMContext):
    if message.text == "на Главную":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['Create_trip_time_arrive'] = message.text

        global keyboard_vod_number_of_seats
        keyboard_vod_number_of_seats = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(1, 6, 2):
            keyboard_vod_number_of_seats.row(f'{i}',f'{i + 1}')
        keyboard_vod_number_of_seats.row('на Главную')

        await message.answer('❗Укажите количество мест:', reply_markup=keyboard_vod_number_of_seats)

        await  CreateTripStates.waiting_for_createtrip_number_of_seats.set()


@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_number_of_seats)
async def Create_trip_number_of_seats(message: types.Message, state: FSMContext):
    if message.text == "на Главную":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()  # Сбрасываем состояние
    else:
        async with state.proxy() as data:
            data['Create_trip_number_of_seats'] = message.text
        global keyboard_vod_extra_options
        keyboard_vod_extra_options = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_vod_extra_options.row('Можно курить🚬', 'Наличие багажа🎒')
        keyboard_vod_extra_options.row('Провоз с животным🐈', 'Ребенок до 12 лет🤱')
        keyboard_vod_extra_options.row('на Главную','Пропустить➡️')

        await message.answer('⚙️Укажите дополнительные опции:', reply_markup=keyboard_vod_extra_options)

        await  CreateTripStates.waiting_for_createtrip_extra_options.set()


@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_extra_options)
async def Create_trip_extra_options(message: types.Message, state: FSMContext):

    if message.text == "на Главную":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()
    else:

        if message.text != "Пропустить➡️":
            async with state.proxy() as data:
                data['Create_trip_extra_options'] = message.text
        else:
            async with state.proxy() as data:
                data['Create_trip_extra_options'] = 'Отсутствуют'

        global keyboard_create_trip
        keyboard_create_trip = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_create_trip.row('на Главную', 'Создать✅')

        await message.answer('Вы точно хотите создать новую поездку? \n\n'
                             f'📍Точка отправления: {data["Create_trip_departure"]}\n\n'
                             f'📍Точка прибытия: {data["Create_trip_arrival"]}\n\n'
                             f'📆Дата отправления: {data["Create_trip_date_departure"]}\n\n'
                             f'⏰Время отправления: {data["Create_trip_time_departure"]}\n\n'
                             f'Время прибытия УБРАТЬ: {data["Create_trip_time_arrive"]}\n\n'
                             f'❗Количество мест: {data["Create_trip_number_of_seats"]}\n\n'
                             f'⚙Дополнительные опции: {data["Create_trip_extra_options"]}', reply_markup=keyboard_create_trip)

        await CreateTripStates.waiting_for_createtrip_savecreate.set()


@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_savecreate)
async def Create_trip_save(message: types.Message, state: FSMContext):
    if message.text == "Создать✅":
        await message.reply('Ваша поездка успешно сохранена!', reply_markup=get_kb)
        await state.finish()
    elif message.text == "на Главную":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()
    else: return 0


@dp.message_handler(text="Я попутчик🧍🏻🎒")
async def poputchki(message: types.Message):
    global keyboard_pop
    keyboard_pop = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_pop.row("Мой профиль🔐")
    keyboard_pop.row("История поездок🗺", "Найти поездку🔍")
    keyboard_pop.row("на Главную")

    await message.reply('Выберите пункт в меню⬇️', reply_markup=keyboard_pop)


@dp.message_handler(text="История поездок🗺")
async def history_of_trips(message: types.Message):
    await message.reply("Здесь Вы можете просмотреть Вашу историю поездок:")


@dp.message_handler(text="Мой профиль🔐")
async def my_profile(message: types.Message):
    user_id = message.from_user.id

    cursor.execute("SELECT * FROM passenger WHERE id_passenger = ?", (user_id,))
    data = cursor.fetchone()

    if data is None:
        await message.answer(
            "На данный момент Ваши персональные данные отсутствуют. Необходимо выбрать и забронировать поездку.",
            reply_markup=get_kb)
    else:
        profile_text = f"Имя: {data[1]}\n" \
                       f"Фамилия: {data[2]}\n" \
                       f"Отчество: {data[3]}\n" \
                       f"Дата рождения: {data[4]}\n" \
                       f"Телефон: {data[5]}"

        if data[6] is not None:
            photo_id = data[6]
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.row("Редактировать профиль")
            keyboard.row("на Главную")
            await message.reply_photo(photo_id, caption=profile_text, reply_markup=keyboard)
        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.row("Редактировать профиль")
            keyboard.row("на Главную")
            await message.reply(profile_text, reply_markup=keyboard)


@dp.message_handler(text="Редактировать🔄")
async def my_profile(message: types.Message):    await message.reply("Иди нахуй пока не работате", reply_markup=get_kb)


class MyStates(StatesGroup):
    waiting_for_departure = State()
    waiting_for_arrival = State()
    waiting_for_date = State()
    waiting_for_options = State()
    waiting_for_seats = State()


class ProfileStatesGroup(StatesGroup):
    name = State()
    surname = State()
    otchestvo = State()
    date_of_birth = State()
    phone_number = State()
    photo = State()


@dp.message_handler(text="Найти поездку🔍")
async def find_trip(message: types.Message):
    await message.answer("📍Укажите точку отправления:")
    await MyStates.waiting_for_departure.set()


@dp.message_handler(state=MyStates.waiting_for_departure)
async def set_departure(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['departure'] = message.text
    await message.answer("📍Укажите точку прибытия:")
    global user_id
    user_id = message.from_user.id
    await MyStates.waiting_for_arrival.set()


@dp.callback_query_handler(lambda c: c.data.startswith('date_'), state=MyStates.waiting_for_date)
async def process_date(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    date = callback_query.data.split('_')[1]
    await state.update_data(date=date)
    await state.update_data(selected_date=date)
    await callback_query.message.answer(f"📆Дата поездки выбрана: {date}", reply_markup=xyi)
    global options_keyboard
    options_keyboard = InlineKeyboardMarkup(row_width=1)
    kur = types.InlineKeyboardButton(text='Можно курить🚬', callback_data='kur')
    bag = types.InlineKeyboardButton(text='Наличие багажа🎒', callback_data='bag')
    pri = types.InlineKeyboardButton(text='Провоз с животным🐈', callback_data='pri')
    reb = types.InlineKeyboardButton(text='Ребенок до 12 лет🤱', callback_data='reb')
    prop = types.InlineKeyboardButton(text='Пропустить➡️', callback_data='prop')
    options_keyboard.add(kur, bag, pri, reb, prop)

    await callback_query.message.answer("⚙️Укажите дополнительные опции:", reply_markup=options_keyboard)
    await MyStates.waiting_for_options.set()


@dp.callback_query_handler(lambda c: c.data in ['kur', 'bag', 'pri', 'reb', 'prop'], state=MyStates.waiting_for_options)
async def process_option(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    if callback_query.data == 'prop':
        await callback_query.message.answer("Вы пропускаете этот пункт➡️")
        await set_seats(callback_query.message, state)

    else:
        await callback_query.message.answer(f"Вы выбрали опцию: {callback_query.data}")
        await ask_for_more_options(callback_query.message)


async def ask_for_more_options(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton("Да", callback_data="more_options_yes")
    no_button = types.InlineKeyboardButton("Нет", callback_data="more_options_no")
    keyboard.add(yes_button, no_button)

    await message.answer("Нужны еще опции для добавления?", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ['more_options_yes', 'more_options_no'],
                           state=MyStates.waiting_for_options)
async def process_more_options_decision(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    if callback_query.data == 'more_options_yes':
        await callback_query.message.answer("Выберите следующую опцию:", reply_markup=options_keyboard)
        await MyStates.waiting_for_options.set()
    elif callback_query.data == 'more_options_no':
        await MyStates.waiting_for_seats.set()
        await set_seats(callback_query.message, state)


class Passenger:
    def __init__(self, user_id, name, age, description, photo):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.description = description
        self.photo = photo


async def save_passenger_data(data, message):
    errors = []

    try:
        if not data.get('name') or len(data['name']) < 2:
            errors.append("Вы ввели некорректное имя.")
        if not data.get('surname') or len(data['surname']) < 2:
            errors.append("Некорректная фамилия.")
        if not data.get('otchestvo') or len(data['otchestvo']) < 2:
            errors.append("Некорректное отчество.")

        date_of_birth_pattern = re.compile(r'\d{2}\.\d{2}\.\d{4}')
        if not re.match(date_of_birth_pattern, data['date_of_birth']):
            errors.append("Неверный формат даты рождения.")

        phone_number_pattern = re.compile(r'(?:\+7|8) \d{3} \d{3} \d{2} \d{2}')
        if not re.match(phone_number_pattern, data['phone_number']):
            errors.append("Неверный формат номера телефона.")

        if errors:
            error_message = "\n".join(errors)
            await message.answer(f"При создании профиля произошли следующие ошибки:\n{error_message}\nВас вернуло на главное меню.", reply_markup=get_kb)
            return

        conn.execute("INSERT INTO passenger (id_passenger, name, surname, otchestvo, date_of_birth, phone_number, photo)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (data['id_passenger'], data['name'], data['surname'], data['otchestvo'], data['date_of_birth'],
                     data['phone_number'], data['photo']))
        conn.commit()

        await message.answer('Ваш профиль успешно создан!', reply_markup=get_kb)

    except Exception as e:
        await message.answer(f"Произошла ошибка при сохранении данных: {str(e)}")


@dp.message_handler(state=MyStates.waiting_for_seats)
async def set_seats(message: types.Message, state: FSMContext):

    cursor.execute("SELECT * FROM passenger WHERE id_passenger = ?", (user_id,))
    data = cursor.fetchone()

    if data is None:
        await message.answer("Давай создадим тебе профиль!\nВведи свое имя:", reply_markup=get_cancel_kb())
        async with state.proxy() as data:
            data['id_passenger'] = user_id

        await ProfileStatesGroup.name.set()
    else:
        await message.answer('Аккаунт уже создан', reply_markup=get_kb)
        await state.finish()


@dp.message_handler(state=ProfileStatesGroup.name)
async def load_surname(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer("Теперь введи свою фамилию:")
    await ProfileStatesGroup.next()


@dp.message_handler(state=ProfileStatesGroup.surname)
async def load_otchestvo(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['surname'] = message.text
    await message.answer("Введите отчество:")
    await ProfileStatesGroup.next()


@dp.message_handler(state=ProfileStatesGroup.otchestvo)
async def load_date_of_birth(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['otchestvo'] = message.text
    await message.answer("Введите дату рождения в формате ДД.ММ.ГГГГ:")
    await ProfileStatesGroup.next()


@dp.message_handler(state=ProfileStatesGroup.date_of_birth)
async def load_phone_number(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['date_of_birth'] = message.text
    await message.answer("Введите номер телефона. В формате +7 000 000 00 00 или 8 000 000 00 00")
    await ProfileStatesGroup.next()


@dp.callback_query_handler(lambda query: query.data == 'skip_photo', state='*')
async def skip_photo_callback(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    async with state.proxy() as data:
        data['photo'] = None

    await query.message.answer('Фотография пропущена.')
    await state.finish()
    await save_passenger_data(data, query.message)


@dp.message_handler(state=ProfileStatesGroup.phone_number)
async def process_photo(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['phone_number'] = message.text

    keyboard_photo = InlineKeyboardMarkup(row_width=1)
    skip_button = InlineKeyboardButton("Пропустить", callback_data="skip_photo")
    keyboard_photo.add(skip_button)

    await message.answer("Пожалуйста, прикрепите фотографию или нажмите 'Пропустить':", reply_markup=keyboard_photo)
    await ProfileStatesGroup.next()


@dp.message_handler(state=ProfileStatesGroup.photo)
@dp.message_handler(content_types=types.ContentType.PHOTO, state="*")
async def load_all(message: types.Message, state: FSMContext) -> None:
    if message.photo:
        async with state.proxy() as data:
            photo_id = message.photo[-1].file_id
            data['photo'] = photo_id
            await save_passenger_data(data, message)
            await state.finish()


def get_cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/отмена_создания'))
    return kb


@dp.message_handler(state=MyStates.waiting_for_arrival)
async def set_arrival(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['arrival'] = message.text
    await message.answer("📆Выберите подходящую дату поездки:", reply_markup=get_date_keyboard())
    await MyStates.waiting_for_date.set()


def get_date_keyboard():
    today = datetime.date.today()
    keyboard = InlineKeyboardMarkup(row_width=3)
    for day in range(18):
        current_date = today + datetime.timedelta(days=day)
        keyboard.insert(InlineKeyboardButton(text=current_date.strftime('%d.%m'), callback_data=f"date_{current_date}"))
    return keyboard


@dp.message_handler(text="Инструкция⚙")
async def with_instr(message: types.Message):
    global keyboard_markup
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.row("Написать администратору🧑🏻‍💻")
    keyboard_markup.row("О попутчике", "О водителе")
    keyboard_markup.row("Ответы на вопросы", "Пользовательское соглашение")
    keyboard_markup.row("на Главную")

    await message.reply('В этом разделе Вы можете ознакомиться с интсрукцией по использованию Telegram-бота'
                        , reply_markup=keyboard_markup)


@dp.message_handler(text="Ответы на вопросы")
async def faq(message: types.Message):
    await message.reply("Выберите частый вопрос⬇️:")
    faq_list = [
        {"text": "❓Когда и где появится информация о забронированной поездке?", "url": "https://telegra.ph/Kogda-i-gde-poyavitsya-informaciya-o-zabronirovannoj-poezdke-04-03-2"},
        {"text": "❓За сколько я могу отменить забронированную поездку?", "url": "https://telegra.ph/Za-skolko-ya-mogu-otmenit-zabronirovannuyu-poezdku-04-03"},
        {"text": "❓Что делать в случае опоздания к месту посадки?", "url": "https://telegra.ph/CHto-delat-v-sluchae-opozdaniya-k-mestu-posadki-04-03"},
        {"text": "❓Как узнать откуда будет место отправления?", "url": "https://telegra.ph/CHto-delat-v-sluchae-opozdaniya-k-mestu-posadki-04-03"},
        {"text": "❓Могу ли я стать водителем, если ранее я был пассажиром (попутчиком)?", "url": "https://telegra.ph/Mogu-li-ya-stat-voditelem-esli-ranee-ya-byl-passazhirom-poputchikom-04-03"},
        {"text": "❓Могу ли я взять с собой свой велосипед/домашнего питомца/крупный багаж?", "url": "https://telegra.ph/Mogu-li-ya-vzyat-s-soboj-svoj-velosipeddomashnego-pitomcakrupnyj-bagazh-04-03"},
        {"text": "❓Есть ли возможность забронировать места заранее?", "url": "https://telegra.ph/Est-li-vozmozhnost-zabronirovat-mesta-zaranee-04-03"},
        {"text": "❓Можем ли мы остановиться где-нибудь по пути для перекуса или отдыха?", "url": "https://telegra.ph/Mozhem-li-my-ostanovitsya-gde-nibud-po-puti-dlya-perekusa-ili-otdyha-04-03"},
        {"text": "❓Можно ли подключить мобильное устройство к системе аудио для прослушивания музыки или аудиокниг?", "url": "https://telegra.ph/Mozhno-li-podklyuchit-mobilnoe-ustrojstvo-k-sisteme-audio-dlya-proslushivaniya-muzyki-ili-audioknig-04-03"},
        {"text": "❓Какие средства безопасности доступны в автомобиле (например, подушки безопасности, ремни безопасности)", "url": "https://telegra.ph/Kakie-sredstva-bezopasnosti-dostupny-v-avtomobile-naprimer-podushki-bezopasnosti-remni-bezopasnosti-04-03"},
        {"text": "❓Сколько времени займет поездка до моего пункта назначения?", "url": "https://telegra.ph/Skolko-vremeni-zajmet-poezdka-do-moego-punkta-naznacheniya-04-03"},
        {"text": "❓Поездка бесплатная, нас повезет незнакомый человек, а я не оплачу поездку, что делать, если мне неловко?", "url": "https://telegra.ph/Poezdka-besplatnaya-nas-povezet-neznakomyj-chelovek-a-ya-ne-oplachu-poezdku-chto-delat-esli-mne-nelovko-04-03"}
    ]

    response = "Выберите частый вопрос⬇️:\n"
    for faq in faq_list:
        response += f"• [{faq['text']}]({faq['url']})\n"

    await message.reply(response, parse_mode=types.ParseMode.MARKDOWN, disable_web_page_preview=True)



@dp.message_handler()
async def handle_buttons(message: types.Message):
    if message.text == "Написать администратору🧑🏻‍💻":
        await message.reply("Перейдите в чат по ссылке с администраторами и задайте волнующий Вас вопрос, как только "
                            "Вы отправите сообщение в ближайшее время Вам ответят! \n Ссылка на группу с "
                            "администраторами: https://t.me/+JwlBQvFYHX41MGEy ✅", reply_markup=keyboard_markup)
    elif message.text == "О попутчике":
        await message.reply(text.text_poput_ruk, reply_markup=keyboard_markup)
    elif message.text == "О водителе":
        await message.reply(text.text_voditel_ruk, reply_markup=keyboard_markup)
    elif message.text == "Пользовательское соглашение":
        await message.reply("https://telegra.ph/Polzovatelskoe-soglashenie-dlya-Telegram-bota-Servis-poputchikov-04-03", reply_markup=keyboard_markup)


#Запускаем
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

    faq_buttons = InlineKeyboardMarkup(row_width=1)
    faq_buttons.add(
        InlineKeyboardButton(text="",
                             url="https://telegra.ph/pelpoldvapldaa-04-03", callback_data="faq_1"),
        InlineKeyboardButton(text="", callback_data="faq_2"),
        InlineKeyboardButton(text="", callback_data="faq_3"),
        InlineKeyboardButton(text="", callback_data="faq_4"),
        InlineKeyboardButton(text="",
                             callback_data="faq_5"),
        InlineKeyboardButton(text="",
                             callback_data="faq_6"),
        InlineKeyboardButton(text="", callback_data="faq_7"),
        InlineKeyboardButton(text="",
                             callback_data="faq_8"),
        InlineKeyboardButton(
            text="",
            callback_data="faq_9"),
        InlineKeyboardButton(
            text="?",
            callback_data="faq_10"),
        InlineKeyboardButton(text="",
                             callback_data="faq_11"),
        InlineKeyboardButton(
            text="",
            callback_data="faq_12"),
    )