import re
from telebot import types
from database import get_users
from config import ADMIN_USERS
from config import admin_password


admin_chat_sessions = {}
active_chats = {}

def admin(bot):
    
    @bot.message_handler(commands=['admin'])
    def handle_admin(message):
        user_id = message.from_user.id
        bot.send_message(message.chat.id, "Введите пароль:")
        bot.register_next_step_handler(message, process_admin_password_step)  
        
    @bot.message_handler(commands=['end_chat'])
    def handle_end_chat_command(message):
        end_chat(message.chat.id)
    
    @bot.message_handler(func=lambda message: message.text == 'Больница')
    def handle_hospital(message):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        user_list_button = types.KeyboardButton('Список пользователей')
        doctor_management_button = types.KeyboardButton('Управление врачами')
        back_button = types.KeyboardButton('Назад')
        markup.add(user_list_button, doctor_management_button, back_button)
        bot.send_message(message.chat.id, "Вы в административной панели. Пожалуйста, выберите действие:", reply_markup=markup)
    
    @bot.message_handler(func=lambda message: message.text == '😈')
    def handle_devil(message):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        send_message_button = types.KeyboardButton('Отправить сообщение пользователю')
        end_chat_button = types.KeyboardButton('Завершить чат')
        back_button = types.KeyboardButton('Назад')
        markup.add(send_message_button, back_button,  end_chat_button)
        bot.send_message(message.chat.id, "Вы в разделе 😈. Пожалуйста, выберите действие:", reply_markup=markup)
        
    @bot.message_handler(func=lambda message: message.text == 'Отправить сообщение пользователю')
    def handle_send_message_button(message):
        msg = bot.send_message(message.chat.id, "Введите ID пользователя:")
        bot.register_next_step_handler(msg, process_user_id_step)

    @bot.message_handler(func=lambda message: True)
    def handle_user_reply(message):
        if message.chat.id in admin_chat_sessions.values():
            admin_id = next(key for key, value in admin_chat_sessions.items() if value == message.chat.id)
            bot.send_message(chat_id=admin_id, text=f"Пользователь {message.chat.id} отвечает: {message.text}")
        elif message.chat.id in active_chats:
            bot.send_message(message.chat.id, "Ваше сообщение получено.")
        else:
            bot.send_message(message.chat.id, "Ваше сообщение получено.")
    
    @bot.message_handler(func=lambda message: message.text == 'Список пользователей')
    def handle_user_list(message):
        markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        view_button = types.KeyboardButton('Просмотр')
        add_button = types.KeyboardButton('Добавить')
        delete_button = types.KeyboardButton('Удалить')
        back_button = types.KeyboardButton('Назад')
        markup.add(view_button, add_button, delete_button, back_button)
        bot.send_message(message.chat.id, "Выберите действие для пользователей:", reply_markup=markup)
    
    @bot.message_handler(func=lambda message: message.text == 'Просмотр')
    def handle_view_users(message):
        users = get_users()
        if not users:
            bot.send_message(message.chat.id, "В базе данных нет пользователей")
            return

        response = "Пользователи:\n\n"
        for user in users:
            response += (
                f"user_id: {user[0]}\n"
                f"Имя: {user[1]}\n"
                f"Фамилия: {user[2]}\n"
                f"Адрес: {user[3]}\n"
                f"Номер полиса: {user[4]}\n"
                f"Номер телефона: {user[5]}\n"
                f"Дата регистрации: {user[6]}\n\n"
            )      
        bot.send_message(message.chat.id, response)
    
    @bot.message_handler(func=lambda message: message.text == 'Управление врачами')
    def handle_doctor_management(message):
        bot.send_message(message.chat.id, "Здесь будет управление врачами.")
    
    @bot.message_handler(func=lambda message: message.text == 'Назад')
    def handle_back(message):
        send_admin_menu(bot, message)


    @bot.message_handler(func=lambda message: message.text == "Завершить чат")            
    def handle_end_chat(message):
        end_chat(message.chat.id)
            
            
    def process_user_id_step(message):
        try:
            user_id = int(message.text)
            msg = bot.send_message(message.chat.id, "Введите сообщение:")
            admin_chat_sessions[message.chat.id] = user_id
            active_chats[user_id] = True
            bot.register_next_step_handler(msg, process_message_step)
        except ValueError:
            bot.send_message(message.chat.id, "ID пользователя должно быть числом.")

    def process_message_step(message):
        if message.text == 'Завершить чат': 
            end_chat(message.chat.id)
        else:      
            admin_id = message.chat.id
            user_id = admin_chat_sessions.get(admin_id)
            if user_id:
                text = message.text
                if send_message_to_user(bot, user_id, text):
                    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                    end_chat_button = types.KeyboardButton('Завершить чат')
                    markup.add(end_chat_button)
                    bot.send_message(message.chat.id, "Сообщение отправлено. Вы можете продолжать переписку.", reply_markup=markup)
                    # Register next step to continue chatting
                    bot.register_next_step_handler(message, process_message_step)
                else:
                    bot.send_message(message.chat.id, "Ошибка при отправке сообщения.")
            else:
                bot.send_message(message.chat.id, "Ошибка: не удалось найти пользователя для отправки сообщения.")
            
    def send_message_to_user(bot, user_id, text):
        try:
            bot.send_message(chat_id=user_id, text=text)
            return True
        except Exception as e: 
            print(f"Error sending message: {str(e)}")
            return False
    
    def process_admin_password_step(message):
        user_id = message.from_user.id
        if message.text == admin_password:
            if user_id in ADMIN_USERS:
                send_admin_menu(bot, message)
            else:
                bot.send_message(message.chat.id, "У вас нет прав администратора.")
        else:
            bot.send_message(message.chat.id, "Не правильный пароль.")
            handle_admin(message)
            
    def send_admin_menu(bot, message):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        hospital_button = types.KeyboardButton('Больница')
        devil_button = types.KeyboardButton('😈')
        markup.add(hospital_button, devil_button)
        bot.send_message(message.chat.id, "Добро пожаловать в админ-панель! Выберите действие:", reply_markup=markup)

    def send_message_to_user(bot, user_id, text):
        try:
            bot.send_message(chat_id=user_id, text=text)
            return True
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False
        
        
    def end_chat(admin_id):
        if admin_id in admin_chat_sessions:
            user_id = admin_chat_sessions[admin_id]
            del admin_chat_sessions[admin_id]
            if user_id in active_chats:
                del active_chats[user_id]
            bot.send_message(admin_id, "Чат завершен.")
            bot.send_message(bot, bot.send_message(admin_id, "Вы завершили чат"))
        else:
            bot.send_message(admin_id, "У вас нет активного чата.")