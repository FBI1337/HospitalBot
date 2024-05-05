import telebot
from telebot import types
from DataBase import BotDB

# Инициализируем бота
bot = telebot.TeleBot("7000708851:AAHy3Kx7Vw8GKB_HbLPgWyuNEjYZRmKgQAw")
db = BotDB('Hospital.db')

# Словарь для хранения временных данных пользователя
user_data_dict = {}

# Словарь для хранения состояния запроса данных пользователя
user_data_state = {}

# Флаг, указывающий на то, проходит ли пользователь регистрацию
is_registering = False

# Функция для запроса данных у пользователя
def request_data(message, text):
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, process_data)

def is_valid_phone_number(phone_number):
    return phone_number.isdigit()



# Функция для обработки ввода данных пользователем
def process_data(message):
    global is_registering
    # Получаем данные пользователя
    user_id = message.from_user.id

    if message.content_type == 'text':
        try:
            data = message.text.strip()

            # Получаем текущее состояние запроса данных пользователя
            state = user_data_state.get(user_id, 0)

            # Сохраняем данные пользователя
            if user_id not in user_data_dict:
                user_data_dict[user_id] = []
            user_data_dict[user_id].append(data)
            
            # Если введены не все данные, запрашиваем следующие
            if len(user_data_dict[user_id]) <= 6:
                if state == 0:
                    request_data(message, "Введите ваше Имя:")
                    user_data_state[user_id] = 1
                elif state == 1:
                    request_data(message, "Введите ваше Отчество:")
                    user_data_state[user_id] = 2
                elif state == 2:
                    request_data(message, "Введите вашу Фамилию:")
                    user_data_state[user_id] = 3
                elif state == 3:
                    request_data(message, "Введите ваш Адрес:")
                    user_data_state[user_id] = 4
                elif state == 4:
                    if is_valid_phone_number(user_data_dict[user_id][-1]):
                        request_data(message, "Введите ваш Номер телефона:")
                        user_data_state[user_id] = 5
                    else:
                        bot.send_message(user_id, "Номер телефона должен состоять только из цифр. Попробуйте еще раз.")
                        return
            
            # Формируем сообщение для проверки данных
            check_message = f"Вас зовут {user_data_dict[user_id][1]} {user_data_dict[user_id][2]} {user_data_dict[user_id][3]}," \
                f" вы проживаете по адресу {user_data_dict[user_id][4]}," \
                    f" с вами можно связаться по номеру {user_data_dict[user_id][5]}? Да/Нет"
            
            # Отправляем сообщение с проверкой данных и добавляем кнопки "Да" и "Нет" меньшего размера
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(types.KeyboardButton('Да'), types.KeyboardButton('Нет'))
            bot.send_message(user_id, check_message, reply_markup=markup)

            # Устанавливаем флаг, что пользователь находится в процессе регистрации
            is_registering = True

        except Exception as e:
            error_message = f"Произошла ошибка: {str(e)}"
            print(f"Error handling message: {error_message}")
            if user_id:
                bot.send_message(user_id, error_message)

    else: 
        # Если сообщение не текстовое, сообщаем пользователю об ошибке
        bot.send_message(user_id, "Извините, данные должны быть в текстовом или числовом формате.")

        if user_id in user_data_state:
            state = user_data_state[user_id]
            if state == 1:
                request_data(message, "Введите ваше Имя:")
            elif state == 2:
                request_data(message, "Введите ваше Отчество:")
            elif state == 3:
                request_data(message, "Введите вашу Фамилия:")
            elif state == 4:
                request_data(message, "Введите ваш Адресс:")
            elif state == 5:
                request_data(message, "Введите ваш Номер телефона:")





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
    if is_registering:
        # Проверяем, что пользователь в процессе регистрации
        if message.text == 'Да':
            if message.from_user.id in user_data_dict:
                data = user_data_dict[message.from_user.id]
                db.add_user(*data)
                del user_data_dict[message.from_user.id]
                bot.send_message(message.chat.id, "Регистрация успешно завершена!")
                is_registering = False
            else:
                bot.send_message(message.chat.id, "Данные пользователя не найдены во временной памяти")
        elif message.text == 'Нет':
            # Пользователь отказался от введенных данных, начинаем регистрацию заново
            clear_temp_data(message.from_user.id)
            start_registration(message)
    else:
        # Пользователь не находится в процессе регистрации
        bot.send_message(message.chat.id, "Я не понимаю вас, вы не проходите регистрацию!")


# Запускаем бота
bot.polling()