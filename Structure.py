import telebot
from telebot import types
from DataBase import BotDB

# Инициализируем бота
bot = telebot.TeleBot("7000708851:AAHy3Kx7Vw8GKB_HbLPgWyuNEjYZRmKgQAw")
db = BotDB('Hospital.db')

# Словарь для хранения временных данных пользователя
user_data_dict = {}

# Флаг, указывающий на то, проходит ли пользователь регистрацию
is_registering = False

# Функция для запроса данных у пользователя
def request_data(message, text):
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, process_data)

# Функция для обработки ввода данных пользователем
def process_data(message):
    global is_registering
    try:
        # Получаем данные пользователя
        user_id = message.from_user.id
        data = message.text.strip()

        #if user_id in user_data_dict:
            #bot.reply_to(message, "Вы уже зарегистрированы!")
            #return
            
        # Сохраняем данные пользователя
        if user_id not in user_data_dict:
            user_data_dict[user_id] = []
        user_data_dict[user_id].append(data)

        # Если введены не все данные, запрашиваем следующие
        if len(user_data_dict[user_id]) < 6:
            if len(user_data_dict[user_id]) == 0:
                request_data(message, "Введите ваше Имя:")
            elif len(user_data_dict[user_id]) == 1:
                request_data(message, "Введите ваше Отчество:")
            elif len(user_data_dict[user_id]) == 2:
                request_data(message, "Введите вашу Фамилию:")
            elif len(user_data_dict[user_id]) == 3:
                request_data(message, "Введите ваш Адрес:")
            elif len(user_data_dict[user_id]) == 4:
                request_data(message, "Введите ваш Номер телефона:")
            return

        # Формируем сообщение для проверки данных
        check_message = f"Вас зовут {user_data_dict[user_id][0]} {user_data_dict[user_id][1]} {user_data_dict[user_id][2]}," \
                        f" вы проживаете по адресу {user_data_dict[user_id][3]}," \
                        f" с вами можно связаться по номеру {user_data_dict[user_id][4]}? Да/Нет"

        # Отправляем сообщение с проверкой данных и добавляем кнопки "Да" и "Нет" меньшего размера
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(types.KeyboardButton('Да'), types.KeyboardButton('Нет'))
        bot.send_message(user_id, check_message, reply_markup=markup)

        # Устанавливаем флаг, что пользователь находится в процессе регистрации
        is_registering = True

    except Exception as e:
        bot.send_message(user_id, f"Произошла ошибка: {e}")

# Функция для очистки временных данных пользователя
def clear_temp_data(user_id):
    if user_id in user_data_dict:
        del user_data_dict[user_id]

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    global is_registering
    # Создаем клавиатуру
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text="Регистрация")
    keyboard.add(button)

    bot.reply_to(message, "Привет! Для регистрации нажмите кнопку 'Регистрация'", reply_markup=keyboard)
    # Сбрасываем флаг процесса регистрации
    is_registering = False

# Обработчик нажатия на кнопку "Регистрация"
@bot.message_handler(func=lambda message: message.text == "Регистрация")
def start_registration(message):
    global is_registering
    if not is_registering:
        # Очищаем временные данные перед началом регистрации
        clear_temp_data(message.from_user.id)
        # Убираем кнопку "Регистрация" после нажатия
        bot.send_message(message.chat.id, "Вы начали процесс регистрации.", reply_markup=types.ReplyKeyboardRemove())
        process_data(message)
    else:
        # Если пользователь уже в процессе регистрации, игнорируем нажатие кнопки
        bot.send_message(message.chat.id, "Вы уже проходите регистрацию!")

# Обработчик нажатия на кнопку "Да" или "Нет"
@bot.message_handler(func=lambda message: message.text in ['Да', 'Нет'])
def check_data(message):
    global is_registering
    user_id = message.from_user.id
    answer = message.text

    if is_registering:
        if answer == 'Да':
            # Если данные подтверждены пользователем, добавляем пользователя в базу данных
            db.add_user(user_id, *user_data_dict[user_id])
            bot.send_message(user_id, "Регистрация успешно завершена!")
            # Очищаем временные данные пользователя
            clear_temp_data(user_id)
            # Сбрасываем флаг процесса регистрации
            is_registering = False
        elif answer == 'Нет':
            # Если пользователь отказывается от введенных данных, начинаем регистрацию заново
            clear_temp_data(user_id)
            start_registration(message)
    else:
        # Если пользователь не находится в процессе регистрации, сообщаем об этом
        bot.send_message(user_id, "Я не понимаю вас, вы не проходите регистрацию!")

# Запускаем бота
bot.polling()