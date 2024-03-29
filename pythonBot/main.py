from config import TOKEN
import text

import sqlite3 as sq
from aiogram import types, Dispatcher, executor, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import datetime
# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)
db = sq.connect('TG_BOT_MATRIX.db')


#Менюшка с кнопками
get_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

item1 = types.KeyboardButton('Инструкция')
item2 = types.KeyboardButton('Я водитель')
item3 = types.KeyboardButton('Я попутчик')
get_kb.add(item1, item2, item3)

xyi = types.ReplyKeyboardMarkup(resize_keyboard=True)
xyi.row("/отмена_поиска")


@dp.message_handler(commands=['отмена_поиска', 'отменить_создания'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):

    await state.finish()
    await message.reply('Успешно выполненно!', reply_markup=get_kb)


@dp.message_handler(text="Назад")
async def with_puree(message: types.Message):
    await message.reply('Вы вернулись в меню', reply_markup=get_kb)


async def send_message_to_user(user_id: int, text: str):
    await bot.send_message(user_id, text)


@dp.message_handler(commands=['start'])
async def startap(message: types.Message):

    user_name = message.from_user.first_name
    user_id = message.from_user.id
    await bot.send_sticker(message.from_user.id, sticker= "CAACAgIAAxkBAAEENjxl_IUljeYelBgwsc8ONsw8YzWRgAACkgEAAladvQqf0C0IQi7VBTQE" )
    await message.reply(f'<em>Привет,{user_name}\nДобро пожаловать в бота для организации работы сервиса попутчиков</em>', parse_mode='HTML', reply_markup = get_kb)


@dp.message_handler(text="Я водитель")
async def vodila(message: types.Message):
    global keyboard_vod
    keyboard_vod = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_vod.row("Создать новую поездку")
    keyboard_vod.row("Мои поездки", "Мoй профиль")
    keyboard_vod.row("Назад")

    await message.reply('Выберите пункт в меню', reply_markup=keyboard_vod)


@dp.message_handler(text="Мoй профиль")
async def vodila_profile(message: types.Message):
    global keyboard_vod_profile
    keyboard_vod_profile = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_vod_profile.row("Назад")

    await message.reply('Ваши персональные данные:  \n \n'
                        'ФИО: [данные о водителе] \n  \n'
                        'Год рождения: [дд.мм.гггг]  \n \n'
                        'Номер телефона: [00000000000] \n \n'
                        'Данные автомобиля:  \n \n'
                        'Марка автомобиля: […]  \n \n'
                        'Модель автомобиля: […]  \n \n'
                        'Гос.номер: [Ф000ФФ]  \n \n'
                        'Стаж вождения: [00]  \n \n'
                        'Фото автомобиля […]', reply_markup=keyboard_vod_profile)


@dp.message_handler(text="Мои поездки")
async def vodila_trip(message: types.Message):
    global keyboard_vod_trip
    keyboard_vod_trip = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_vod_trip.row("Назад")

    await message.reply('Ваши поездки', reply_markup=keyboard_vod_trip)


class CreateTripStates(StatesGroup):
    waiting_for_createtrip_point_departure = State()
    waiting_for_createtrip_point_arrival = State()
    waiting_for_createtrip_date_departure = State()
    waiting_for_createtrip_time_departure = State()
    waiting_for_createtrip_time_arrival = State()
    waiting_for_createtrip_number_of_seats = State()
    waiting_for_createtrip_extra_options = State()
    waiting_for_createtrip_savecreate = State()


@dp.message_handler(text="Создать новую поездку")
async def Create_trip(message: types.Message, state: FSMContext):

    global keyboard_create_trip
    keyboard_create_trip = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_create_trip.row("Отмена")

    await message.answer('Укажите точку отправления:', reply_markup=keyboard_create_trip)

    await CreateTripStates.waiting_for_createtrip_point_departure.set()


@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_point_departure)
async def Create_trip_point_departure (message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['Create_trip_departure'] = message.text
        await message.answer("Укажите точку прибытия:")
        await CreateTripStates.waiting_for_createtrip_point_arrival.set()


@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_point_arrival)
async def Create_trip_point_arrival (message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['Create_trip_arrival'] = message.text
        await message.answer("Выберите подходящую дату поездки:", reply_markup=get_date_keyboard())
        await CreateTripStates.waiting_for_createtrip_date_departure.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('date_'), state=CreateTripStates.waiting_for_createtrip_date_departure)
async def Create_trip_date(callback_query: CallbackQuery, state: FSMContext):
    date_str = callback_query.data[5:]
    async with state.proxy() as data:
        data['Create_trip_date_departure'] = date_str
    await CreateTripStates.waiting_for_createtrip_time_departure.set()
    await bot.send_message(callback_query.from_user.id, f'Вы выбрали дату: {date_str}')
    await bot.send_message(callback_query.from_user.id, 'Укажите время отправления:')



@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_time_departure)
async def Create_trip_time_departure (message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()
    else:
        await message.answer("Укажите время прибытия:")
        async with state.proxy() as data:
            data['Create_trip_time_departure'] = message.text
        await  CreateTripStates.waiting_for_createtrip_time_arrival.set()


@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_time_arrival)
async def Create_trip_time_arrive(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['Create_trip_time_arrive'] = message.text

        global keyboard_vod_number_of_seats
        keyboard_vod_number_of_seats = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(1, 6, 2):
            keyboard_vod_number_of_seats.row(f'{i}',f'{i + 1}')
        keyboard_vod_number_of_seats.row('Отмена')

        await message.answer('Укажите количество мест:', reply_markup=keyboard_vod_number_of_seats)

        await  CreateTripStates.waiting_for_createtrip_number_of_seats.set()

@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_number_of_seats)
async def Create_trip_number_of_seats(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()  # Сбрасываем состояние
    else:
        async with state.proxy() as data:
            data['Create_trip_number_of_seats'] = message.text
        global keyboard_vod_extra_options
        keyboard_vod_extra_options = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_vod_extra_options.row('Можно курить', 'Наличие багажа')
        keyboard_vod_extra_options.row('Провоз с животным', 'Ребенок до 12')
        keyboard_vod_extra_options.row('Отмена','Пропустить')

        await message.answer('Укажите дополнительные опции:', reply_markup=keyboard_vod_extra_options)

        await  CreateTripStates.waiting_for_createtrip_extra_options.set()


@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_extra_options)
async def Create_trip_extra_options(message: types.Message, state: FSMContext):

    if message.text == "Отмена":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()
    else:

        if message.text != "Пропустить":
            async with state.proxy() as data:
                data['Create_trip_extra_options'] = message.text
        else:
            async with state.proxy() as data:
                data['Create_trip_extra_options'] = 'Отсутвтвуют'

        global keyboard_create_trip
        keyboard_create_trip = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_create_trip.row('Отмена', 'Создать')

        await message.answer('Вы точно хотите создать новую поездку? \n\n'
                             f'Точка отправления: {data['Create_trip_departure']}\n\n'
                             f'Точка прибытия: {data['Create_trip_arrival']}\n\n'
                             f'Дата отправления: {data['Create_trip_date_departure']}\n\n'
                             f'Время отправления: {data['Create_trip_time_departure']}\n\n'
                             f'Время прибытия: {data['Create_trip_time_arrive']}\n\n'
                             f'Количество мест: {data['Create_trip_number_of_seats']}\n\n'
                             f'Дополнительные опции: {data['Create_trip_extra_options']}', reply_markup=keyboard_create_trip)

        await CreateTripStates.waiting_for_createtrip_savecreate.set()


@dp.message_handler(state=CreateTripStates.waiting_for_createtrip_savecreate)
async def Create_trip_save(message: types.Message, state: FSMContext):
    if message.text == "Создать":
        await message.reply('Ваша поездка успешно сохранена!', reply_markup=get_kb)
        await state.finish()
    elif message.text == "Отмена":
        await message.reply('Вы вернулись в меню', reply_markup=get_kb)
        await state.finish()
    else: return 0


@dp.message_handler(text="Я попутчик")
async def poputchki(message: types.Message):
    global keyboard_pop
    keyboard_pop = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_pop.row("Мой профиль")
    keyboard_pop.row("История поездок", "Найти поездку")
    keyboard_pop.row("Назад")

    await message.reply('Выберите пункт в меню', reply_markup=keyboard_pop)


@dp.message_handler(text="История поездок")
async def history_of_trips(message: types.Message):
    await message.reply("Здесь Вы можете просмотреть Вашу историю поездок:")


@dp.message_handler(text="Мой профиль")
async def my_profile(message: types.Message):
    keyboard_my_profile = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_my_profile.row("Редактировать")
    keyboard_my_profile.row("Назад")
    await message.reply("На данный момент Ваши персональные данные отсутствуют. Необходимо выбрать и забронировать поездку.", reply_markup=keyboard_my_profile)


@dp.message_handler(text="Редактировать")
async def my_profile(message: types.Message):    await message.reply("Нет данных для редактирования", reply_markup=get_kb)


class MyStates(StatesGroup):
    waiting_for_departure = State()
    waiting_for_arrival = State()
    waiting_for_date = State()
    waiting_for_options = State()
    waiting_for_seats = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_photo = State()


@dp.message_handler(text="Найти поездку")
async def find_trip(message: types.Message):
    await message.answer("Укажите точку отправления:")
    await MyStates.waiting_for_departure.set()


@dp.message_handler(state=MyStates.waiting_for_departure)
async def set_departure(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['departure'] = message.text
    await message.answer("Укажите точку прибытия:")
    await MyStates.waiting_for_arrival.set()


@dp.callback_query_handler(lambda c: c.data.startswith('date_'), state=MyStates.waiting_for_date)
async def process_date(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    date = callback_query.data.split('_')[1]
    await state.update_data(date=date)
    await state.update_data(selected_date=date)
    await callback_query.message.answer(f"Дата поездки выбрана: {date}", reply_markup=xyi)
    global options_keyboard
    options_keyboard = InlineKeyboardMarkup(row_width=1)
    kur = types.InlineKeyboardButton(text='Можно курить', callback_data='kur')
    bag = types.InlineKeyboardButton(text='Наличие багажа', callback_data='bag')
    pri = types.InlineKeyboardButton(text='Провоз с животным', callback_data='pri')
    reb = types.InlineKeyboardButton(text='Ребенок до 12 лет', callback_data='reb')
    prop = types.InlineKeyboardButton(text='Пропустить опции', callback_data='prop')
    options_keyboard.add(kur, bag, pri, reb, prop)

    await callback_query.message.answer("Укажите дополнительные опции:", reply_markup=options_keyboard)
    await MyStates.waiting_for_options.set()


@dp.callback_query_handler(lambda c: c.data in ['kur', 'bag', 'pri', 'reb', 'prop'], state=MyStates.waiting_for_options)
async def process_option(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    if callback_query.data == 'prop':
        await callback_query.message.answer("Вы пропускаете этот пункт")
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
        await callback_query.message.answer("Хорошо, переходим дальше.")
        await MyStates.waiting_for_seats.set()
        await set_seats(callback_query.message, state)


@dp.message_handler(state=MyStates.waiting_for_seats)
async def set_seats(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['seats'] = message.text
    await message.answer("Заполните данные для регистрации:")
    await message.answer("Введите ФИО:")
    await MyStates.next()


@dp.message_handler(state=MyStates.waiting_for_name)
async def set_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer("Введите номер телефона:")
    await MyStates.next()


@dp.message_handler(state=MyStates.waiting_for_phone)
async def set_phone(message: types.Message, state: FSMContext):
    keyboard_pht = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_pht.row("Оставить без фотографии")
    keyboard_pht.row("/отменить_создания")
    async with state.proxy() as data:
        data['phone'] = message.text
    await message.answer("При желании добавьте фото:", reply_markup=keyboard_pht)

    await MyStates.next()


@dp.message_handler(state=MyStates.waiting_for_photo)
async def skip_photo(message: types.Message, state: FSMContext):
    await message.answer("Поздравляем! Теперь Ваши данные находятся в «Мой профиль».")
    await state.finish()


@dp.message_handler(state=MyStates.waiting_for_arrival)
async def set_arrival(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['arrival'] = message.text
    await message.answer("Выберите подходящую дату поездки:", reply_markup=get_date_keyboard())
    await MyStates.waiting_for_date.set()


def get_date_keyboard():
    today = datetime.date.today()
    keyboard = InlineKeyboardMarkup(row_width=3)
    for day in range(18):
        current_date = today + datetime.timedelta(days=day)
        keyboard.insert(InlineKeyboardButton(text=current_date.strftime('%d.%m'), callback_data=f"date_{current_date}"))
    return keyboard


@dp.message_handler(text="Инструкция")
async def with_instr(message: types.Message):
    global keyboard_markup
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.row("Написать администратору")
    keyboard_markup.row("О попутчике", "О водителе")
    keyboard_markup.row("Ответы на вопросы", "Пользовательское соглашение")
    keyboard_markup.row("Назад")

    await message.reply('В этом разделе Вы можете ознакомиться с интсрукцией по использованию Telegram-бота'
                        , reply_markup=keyboard_markup)


@dp.message_handler(text="Ответы на вопросы")
async def faq(message: types.Message):
    faq_buttons = InlineKeyboardMarkup(row_width=1)
    faq_buttons.add(
        InlineKeyboardButton(text="Когда и где появится информация о забронированной поездке?", callback_data="faq_1"),
        InlineKeyboardButton(text="За сколько я могу отменить забронированную поездку?", callback_data="faq_2"),
        InlineKeyboardButton(text="Что делать в случае опоздания к месту посадки?", callback_data="faq_3"),
        InlineKeyboardButton(text="Как узнать откуда будет место отправления?", callback_data="faq_4"),
        InlineKeyboardButton(text="Могу ли я стать водителем, если ранее я был пассажиром (попутчиком)?",
                             callback_data="faq_5"),
        InlineKeyboardButton(text="Могу ли я взять с собой свой велосипед/домашнего питомца/крупный багаж?",
                             callback_data="faq_6"),
        InlineKeyboardButton(text="Есть ли возможность забронировать места заранее?", callback_data="faq_7"),
        InlineKeyboardButton(text="Можем ли мы остановиться где-нибудь по пути для перекуса или отдыха?",
                             callback_data="faq_8"),
        InlineKeyboardButton(text="Есть ли возможность встретить пробки или задержки на дороге?",
                             callback_data="faq_9"),
        InlineKeyboardButton(text="Можно ли подключить мобильное устройство к системе аудио для прослушивания музыки или аудиокниг?",
                             callback_data="faq_10"),
        InlineKeyboardButton(text="Какие средства безопасности доступны в автомобиле (например, подушки безопасности, ремни безопасности)?",
                             callback_data="faq_11"),
        InlineKeyboardButton(text="Сколько времени займет поездка до моего пункта назначения?",
                             callback_data="faq_12"),
        InlineKeyboardButton(text="Поездка бесплатная, нас повезет незнакомый человек, а я не оплачу поездку, что делать, если мне неловко?",
                             callback_data="faq_13"),
    )
    await message.reply("Выберите частый вопрос:", reply_markup=faq_buttons)



@dp.callback_query_handler(lambda c: c.data.startswith('faq_'))
async def process_faq_callback(callback_query: types.CallbackQuery):
    faq_id = callback_query.data.split('_')[1]
    answer = text.faq_answers.get(faq_id, "Ответ на данный вопрос не найден.")
    await bot.send_message(callback_query.from_user.id, answer)


@dp.message_handler()
async def handle_buttons(message: types.Message):
    if message.text == "Написать администратору":
        await message.reply("Перейдите в чат по ссылке с администраторами и задайте волнующий Вас вопрос, как только "
                            "Вы отправите сообщение в ближайшее время Вам ответят! \n Ссылка на группу с "
                            "администраторами: https://t.me/+JwlBQvFYHX41MGEy", reply_markup=keyboard_markup)
    elif message.text == "О попутчике":
        await message.reply(text.text_poput_ruk, reply_markup=keyboard_markup)
    elif message.text == "О водителе":
        await message.reply(text.text_voditel_ruk, reply_markup=keyboard_markup)
    elif message.text == "Пользовательское соглашение":
        await message.reply(text.text_polzov_sogl, reply_markup=keyboard_markup)


#Запускаем
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
