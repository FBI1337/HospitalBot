import re
from telebot import types
from database import add_user, user_exists, get_doctors
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut

user_data = {}

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        send_welcome(bot, message)

    @bot.message_handler(func=lambda message: message.text == 'Регистрация')
    def handle_registration(message):
        user_id = message.from_user.id
        if user_exists(user_id):
            bot.send_message(message.chat.id, "Вы уже зарегистрированы!")
        else: 
            bot.send_message(message.chat.id, "Начался процесс регистрации.")
            bot.send_message(message.chat.id, "Введите свое имя:")
            bot.register_next_step_handler(message, process_name_step)

    @bot.message_handler(func=lambda message: message.text == 'Врачи')
    def handle_doctors(message):
        doctors = get_doctors()
        if not doctors:
            bot.send_message(message.chat.id, "В данный момент нет доступных врачей.")
            return

        response = "Доступные врачи:\n\n"
        for doctor in doctors:
            response += (
                f"Имя: {doctor[0]}\n"
                f"Фамилия: {doctor[1]}\n"
                f"Специализация: {doctor[2]}\n"
                f"Кабинет: {doctor[3]}\n"
                f"Номер телефона: {doctor[4]}\n\n"
            )
        
        bot.send_message(message.chat.id, response)

    @bot.message_handler(func=lambda message: message.text == 'Запись к врачу')
    def handle_appointment(message):
        bot.send_message(message.chat.id, "Раздел Запись к врачу пока недоступен.")

    def send_welcome(bot, message):
        markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        registration_button = types.KeyboardButton('Регистрация')
        doctors_button = types.KeyboardButton('Врачи')
        appointment_button = types.KeyboardButton('Запись к врачу')
        markup.add(registration_button, doctors_button, appointment_button)

        bot.send_message(message.chat.id, "Добро пожаловать! Пожалуйста, выберите действие:", reply_markup=markup)
        
    def send_message(bot, chat_id, text):
        bot.send_message(chat_id, text)
    
    def is_valid_text(text):
        return bool(re.match("^[A-Za-zА-Яа-яЁё ]{2,}$", text))
    
    def handle_all_message(message):
        if message.content_type != 'text':
            send_error_message(message)
            return False
        return True
    
    def send_error_message(message):
        bot.send_message(message.chat.id, "Извините, я понимаю только текстовые сообщения.")
        
    def process_name_step(message):
        if not handle_all_message(message):
            bot.register_next_step_handler(message, process_name_step)
            return
        
        user_id = message.from_user.id
        if not is_valid_text(message.text):
            msg = bot.send_message(message.chat.id, "Имя должно содержать только буквы. Попробуйте снова:")
            bot.register_next_step_handler(msg, process_name_step)
            return
        
        user_data[user_id] = {'name': message.text}
        bot.send_message(message.chat.id, "Введите вашу фамилию:")
        bot.register_next_step_handler(message, process_surname_step)

    def process_surname_step(message):
        if not handle_all_message(message):
            bot.register_next_step_handler(message, process_surname_step)
            return
        
        user_id = message.from_user.id
        if not is_valid_text(message.text):
            msg = bot.send_message(message.chat.id, "Фамилия должна содержать только буквы. Попробуйте снова:")
            bot.register_next_step_handler(msg, process_surname_step)
            return
        
        user_data[user_id]['surname'] = message.text
        bot.send_message(message.chat.id, "Введите ваш адрес: (4-я линия д.21)")
        bot.register_next_step_handler(message, process_address_step)

    def process_address_step(message):
        if not handle_all_message(message):
            bot.register_next_step_handler(message, process_address_step)
            return
        
        user_id = message.from_user.id
        address = message.text
        
        if not is_valid_address_format(address):
            msg = bot.send_message(message.chat.id, "Адрес должен содержать буквы, цифры и допустимые спецсимволы (/ , .). Попробуйте снова:")
            bot.register_next_step_handler(msg, process_address_step)
            return
              
        if not verify_address(address):
            msg = bot.send_message(message.chat.id,  "Адрес не найден. Повторите снова:")
            bot.register_next_step_handler(msg, process_address_step)
            return
        
        user_data[user_id]['address'] = message.text
        bot.send_message(message.chat.id, "Введите ваш номер полиса: (16 цифр)")
        bot.register_next_step_handler(message, process_polis_number_step)
        
    def process_polis_number_step(message):
        if not handle_all_message(message):
            bot.register_next_step_handler(message, process_polis_number_step)
            return
        user_id = message.from_user.id
        polis_number = message.text
        
        if not is_valid_polis_number_format(polis_number):
            msg = bot.send_message(message.chat.id, "Номер полиса должен содержать только цифры. Попробуйте снова:")
            bot.register_next_step_handler(msg, process_polis_number_step)
            return
        user_data[user_id]['polis_number'] = polis_number
        bot.send_message(message.chat.id, "Введите ваш номер телефона: (+79117990881)")
        bot.register_next_step_handler(message, process_phone_number_step)

    def process_phone_number_step(message):
        if not handle_all_message(message):
            bot.register_next_step_handler(message, process_phone_number_step)
            return
        
        user_id = message.from_user.id
        phone_number = message.text

        if not is_valid_phone_number_format(phone_number):
            msg = bot.send_message(message.chat.id, "Номер телефона должен содержать только цифры. Попробуйте снова:")
            bot.register_next_step_handler(msg, process_phone_number_step)
            return

        user_data[user_id]['phone_number'] = phone_number
        save_user_data(user_id)
        bot.send_message(message.chat.id, "Регистрация завершена!")

    def save_user_data(user_id):
        user = user_data[user_id]
        add_user(user_id, user['name'], user['surname'], user['address'], user['polis_number'], user['phone_number'])
        
    def is_valid_polis_number_format(polis_number):
        return bool(re.match("^[0-9]{16,}$", polis_number))
    
    def is_valid_phone_number_format(phone_number):
        return bool(re.match("^[0-9+]{11,}$", phone_number))
        
    def is_valid_address_format(address):
        return bool(re.match("^[A-Za-z0-9А-Яа-яЁё /,.-]{5,}$", address))
    
    def verify_address(address):
        geolocator = Nominatim(user_agent="hospital_bot", timeout=10)
        try:
            location = geolocator.geocode(address)
            return location is not None
        except (GeocoderUnavailable, GeocoderTimedOut):
            return False
