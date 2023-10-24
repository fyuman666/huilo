import telebot
import pickle
from telebot import types
import random

bot_token = '6958037674:AAFdhcmiNzerOSI_xhaokhy64sbLXSOLiYs'
admin_code = '5727907441'

bot = telebot.TeleBot(bot_token)

user_data_file = 'user_data.pkl'
banned_users_file = 'banned_users.pkl'

try:
    with open(user_data_file, 'rb') as file:
        user_data = pickle.load(file)
except FileNotFoundError:
    user_data = {}

try:
    with open(banned_users_file, 'rb') as file:
        banned_users = pickle.load(file)
except FileNotFoundError:
    banned_users = []

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    response_message = '''Канал создателя https://t.me/fyuman_guard | вывод денег производится через @are_over вывод от 10₽ внимание стоит защита от авто кликера то есть за авто кликер вы получаете блокировку аккаунта на 30 дней с момента махинаций.'''
    bot.send_message(chat_id, response_message)
    show_main_menu(chat_id)

def show_main_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_get_money = types.KeyboardButton(text='click 0.002₽')
    button_contacts = types.KeyboardButton(text='Контакты')
    button_profile = types.KeyboardButton(text='Мой профиль') 
    keyboard.add(button_get_money, button_contacts, button_profile)
    bot.send_message(chat_id, 'Выберите действие:', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'click 0.002₽')
def handle_get_money(message):
    chat_id = message.chat.id
    if is_user_banned(chat_id):
        bot.send_message(chat_id, 'Вы заблокированы и не можете получить монеты')
        return
    amount = 0.002
    bot.send_message(chat_id, f'Вы получили {amount}₽')
    update_user_balance(chat_id, amount) 

@bot.message_handler(func=lambda message: message.text == 'Контакты')
def handle_contacts(message):
    chat_id = message.chat.id
    response_message = '''Контакты создателей:
    - developers: fyuman, @fyuman1336
    - вывод денег: areover, @Are_over'''
    bot.send_message(chat_id, response_message)

@bot.message_handler(func=lambda message: message.text == 'Мой профиль')
def handle_profile(message):
    chat_id = message.chat.id
    user_data = get_user_data(chat_id)
    if user_data:
        response_message = f'''Ваш профиль:
        - Имя: {message.from_user.first_name}
        - Айди: {user_data['chat_id']}
        - Баланс: {user_data['balance']}₽'''
    else:
        response_message = 'Вы еще не зарегистрированы в боте.'
    bot.send_message(chat_id, response_message)

@bot.message_handler(commands=['admin'])
def handle_admin_panel(message):
    chat_id = message.chat.id
    admin_codes = message.text.split()
    if len(admin_codes) >= 2 and admin_codes[1] == '5727907441':
        show_admin_menu(chat_id)
    else:
        bot.send_message(chat_id, 'Неверный код администратора')

def show_admin_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_ban_user = types.KeyboardButton(text='Забанить пользователя')
    button_unban_user = types.KeyboardButton(text='Разбанить пользователя')
    button_reset_balance = types.KeyboardButton(text='Обнулить баланс пользователя') 
    button_give_coins = types.KeyboardButton(text='выдать монеты') 
    keyboard.add(button_ban_user, button_unban_user, button_reset_balance,button_give_coins)
    bot.send_message(chat_id, 'Выберите действие:', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'Забанить пользователя')
def handle_ban_user(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Введите айди пользователя, которого нужно забанить:')
    bot.register_next_step_handler(message, ban_user)

def ban_user(message):
    user_id = message.text
    if user_id.isdigit():
        user_id = int(user_id)
        banned_users.append(user_id)
        save_banned_users()
        bot.send_message(message.chat.id, f'Пользователь {user_id} заблокирован')
    else:
        bot.send_message(chat_id, 'Неверный айди пользователя')

@bot.message_handler(func=lambda message: message.text == 'Разбанить пользователя')
def handle_unban_user(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Введите айди пользователя, которого нужно разбанить:')
    bot.register_next_step_handler(message, unban_user)

def unban_user(message):
    user_id = message.text
    if user_id.isdigit():
        user_id = int(user_id)
        if user_id in banned_users:
            banned_users.remove(user_id)
            save_banned_users()
            bot.send_message(message.chat.id, f'Пользователь {user_id} разблокирован')
        else:
            bot.send_message(message.chat.id, f'Пользователь {user_id} не заблокирован')
    else:
        bot.send_message(chat_id, 'Неверный айди пользователя')

@bot.message_handler(func=lambda message: message.text == 'Обнулить баланс пользователя')
def handle_reset_balance(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Введите айди пользователя, у которого нужно обнулить баланс:')
    bot.register_next_step_handler(message, reset_balance)

def reset_balance(message):
    user_id = message.text
    if user_id.isdigit():
        user_id = int(user_id)
        user_data = get_user_data(user_id)
        if user_data:
            user_data['balance'] = 0
            save_user_data()
            bot.send_message(message.chat.id, f'Баланс пользователя {user_id} обнулен')
        else:
            bot.send_message(message.chat.id, f'Пользователь {user_id} не найден')
    else:
        bot.send_message(chat_id, 'Неверный айди пользователя')

def update_user_balance(chat_id, amount):
    if chat_id in user_data:
        user_data[chat_id]['balance'] += amount
    else:
        user_data[chat_id] = {
            'name': '',
            'chat_id': chat_id,
            'balance': amount
        }
    save_user_data()
    
@bot.message_handler(func=lambda message: message.text == 'выдать монеты')
def handle_give_coins(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Введите айди пользователя, которому нужно выдать монеты:')
    bot.register_next_step_handler(message, ask_coins)

def ask_coins(message):
    user_id = message.text
    if user_id.isdigit():
        user_id = int(user_id)
        if user_id in user_data:
            bot.send_message(message.chat.id, 'Введите сумму монет для выдачи:')
            bot.register_next_step_handler(message, lambda msg: give_coins(msg, user_id))         
        else:
            bot.send_message(message.chat.id, f'Пользователь {user_id} не найден')
    else:
        bot.send_message(chat_id, 'Неверный айди пользователя')        

def give_coins(message, user_id):
    coins = message.text
    if coins.isdigit():
        coins = int(coins)
        user_data[user_id]['balance'] += coins
        save_user_data()
        bot.send_message(message.chat.id, f'Вы успешно выдали {coins} монет пользователю {user_id}')
    else:
        bot.send_message(message.chat.id, 'Неверная сумма монет') 



def save_banned_users():
    with open(banned_users_file, 'wb') as file:
        pickle.dump(banned_users, file)

def is_user_banned(chat_id):
    if chat_id in banned_users:
        return True
    return False

def get_user_data(chat_id):
    if chat_id in user_data:
        return user_data[chat_id]
    return None

def update_user_balance(chat_id, amount):
    if chat_id in user_data:
        user_data[chat_id]['balance'] += amount
    else:
        user_data[chat_id] = {'chat_id': chat_id, 'balance': amount}
    save_user_data()

def save_user_data():
    with open(user_data_file, 'wb') as file:
        pickle.dump(user_data, file)

bot.polling()
