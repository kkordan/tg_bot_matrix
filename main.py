from config import TOKEN
import text
import sqlite3 as sq
from aiogram import types, Dispatcher, executor, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Command, Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)
# db = sq.connect('new.db')

keyboard_markup = None
# Менюшка кнопок
get_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

item1 = types.KeyboardButton('Инструкция')
item2 = types.KeyboardButton('Я водитель')
item3 = types.KeyboardButton('Я попутчик')
get_kb.add(item1, item2, item3)


@dp.message_handler(text="Назад")
async def with_puree(message: types.Message):
    await message.reply('Вы вернулись в меню', reply_markup=get_kb)


async def send_message_to_user(user_id: int, text: str):
    await bot.send_message(user_id, text)


@dp.message_handler(commands=['start'])
async def startap(message: types.Message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    await send_message_to_user(user_id, "Привет! Это бот.")
    await bot.send_sticker(message.from_user.id, sticker="CAACAgIAAxkBAAEENjxl_IUljeYelBgwsc8ONsw8YzWRgAACkgEAAladvQqf0C0IQi7VBTQE")
    await message.reply(f'<em>Привет,{user_name}\nДобро пожаловать в бота для организации работы сервиса попутчиков</em>',
                        parse_mode='HTML', reply_markup=get_kb)


@dp.message_handler(text="Я водитель")
async def vodila(message: types.Message):
    keyboard_vod = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_vod.row("Создать новую поездку")
    keyboard_vod.row("Мои поездки", "Мой профиль")
    keyboard_vod.row("Назад")

    await message.reply('Выберите пункт в меню', reply_markup=keyboard_vod)


@dp.message_handler(text="Я попутчик")
async def poputchki(message: types.Message):
    keyboard_pop = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_pop.row("Мой профиль")
    keyboard_pop.row("История поездок", "Найти поездку")
    keyboard_pop.row("Назад")

    await message.reply('Выберите пункт в меню', reply_markup=keyboard_pop)


@dp.message_handler(text="Инструкция")
async def with_instr(message: types.Message):
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.row("Написать администратору")
    keyboard_markup.row("О попутчике", "О водителе")
    keyboard_markup.row("Ответы на частые вопросы", "Пользовательское соглашение")
    keyboard_markup.row("Назад")

    await message.reply('В этом разделе Вы можете ознакомиться с интсрукцией по использованию Telegram-бота'
                        , reply_markup=keyboard_markup)


@dp.message_handler(text="Ответы на частые вопросы")
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


# Запускаем
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
