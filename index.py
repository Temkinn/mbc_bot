import telebot
from telebot import types
import os
import config

import requests


#Подписки
#Вопросы
#Меню
#Скидочка

bot = telebot.TeleBot(os.environ.get("TOKEN"))
subWeb = types.WebAppInfo(os.environ.get('subURL'))
questionWeb = types.WebAppInfo(os.environ.get('questionURL'))
menuWeb = types.WebAppInfo(os.environ.get('menuURL'))
ansWeb = types.WebAppInfo(os.environ.get('ansURL'))
api = os.environ.get("API_URL")


@bot.message_handler(commands=['start'])
def start_command(message):
    
    requests.post(f"{api}/users/add", json = {
        "id": message.from_user.id,
        "name": message.from_user.first_name,
        "username": message.from_user.username
    })
    
    requests.put(f"{api}/users/update/{message.from_user.id}", json={
        "name": message.from_user.first_name,
        "username": message.from_user.username
    })
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        
    #buttons
    menu = types.KeyboardButton("☕ Заглянуть в меню", web_app=menuWeb)
    subscribe = types.KeyboardButton("💌 Подписки", web_app=subWeb)
    questions = types.KeyboardButton("❓ Задать вопрос", web_app=questionWeb)
    ofquestions = types.KeyboardButton("❔ Часто задаваемые вопросы")
    # add buttons to markup
    markup.add(menu, subscribe, questions,ofquestions)
    bot.send_photo(message.chat.id, types.InputFile("assets/welcome.png"), config.welcome(message.from_user.first_name), reply_markup=markup)

@bot.message_handler(commands=['message'])
def message(message):
    bot.send_message(message.chat.id, message)
    
@bot.message_handler(commands=['admin'])
def admin(message):
    print("ADMIN!!!!")
    if config.admin(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(row_width=1)
        
        ans = types.KeyboardButton("/answer", web_app=ansWeb)
        news = types.KeyboardButton("/news")
        user = types.KeyboardButton("/user")
        markup.add(ans, news, user)
        bot.send_message(message.chat.id, "Вы в режиме админа", reply_markup=markup)
    
@bot.message_handler(commands=['news'])
def news(message):
    if config.admin(message.from_user.id):
        bot.send_message(message.from_user.id, "Отправьте новость: ")
        
@bot.message_handler(content_types=['photo', 'video'])
def get_news(message):
    if config.admin(message.from_user.id):
        markup = types.InlineKeyboardMarkup()

        yes = types.InlineKeyboardButton("Да", callback_data="yes")
        no = types.InlineKeyboardButton("Нет", callback_data="no")
        
        markup.add(yes, no)
        
        bot.send_message(message.from_user.id, "Отправить новость всем подписчикам этого бота?", reply_markup=markup)

        
@bot.callback_query_handler(func=lambda call: call.data == "yes")
def send_news(call):
    bot.answer_callback_query(call.id, text="Рассылаю всем...")#
    bot.edit_message_text("Новость успешно отпралена!", call.from_user.id, call.message.id)
    users = requests.get(f"{api}/users").json()
    for user in users: 
        bot.copy_message(user["id"], call.from_user.id, call.message.id - 1)

@bot.callback_query_handler(func=lambda call: call.data == "no")
def send_news(call):
    bot.answer_callback_query(call.id, text="Удаляю...")#
    bot.delete_messages(call.from_user.id, [call.message.id, call.message.id - 1])


@bot.message_handler(commands=["user"])
def user(message):
    markup = types.InlineKeyboardMarkup(resize_keyboard=True)

    subWeb = types.WebAppInfo(config.subURL)
    questionWeb = types.WebAppInfo(config.questionURL)
    menuWeb = types.WebAppInfo(config.menuURL)
    #buttons
    menu = types.KeyboardButton("☕ Заглянуть в меню", web_app=menuWeb)
    subscribe = types.KeyboardButton("💌 Подписки", web_app=subWeb)
    questions = types.KeyboardButton("❓ Задать вопрос", web_app=questionWeb)
    ofquestions = types.KeyboardButton("❔ Часто задаваемые вопросы")
    # add buttons to markup
    markup.add(menu, subscribe, questions,ofquestions)
    bot.send_photo(message.chat.id, types.InputFile("assets/welcome.png"), config.welcome(message.from_user.first_name), reply_markup=markup)
    
@bot.message_handler(content_types="web_app_data") #получаем отправленные данные 
def answer(webMes):
    decdata = config.decode(webMes.web_app_data.data)
    print(decdata)
    if decdata[0] == 'answer':
        if webMes.from_user.id in config.admins:
            try:
                bot.send_message(int(decdata[1]), f"Ответ на заданный вами вопрос:\n{decdata[2]}")
                for a in config.admins:
                    bot.send_message(a, f"Ответ на вопрос от чата {decdata[1]} отправлен!")
            except telebot.apihelper.ApiTelegramException:
                bot.send_message(webMes.from_user.id, "Не могу отправить ответ. Возможно, чата с таким id не существует.")
    elif decdata[0] == 'question':
        for a in config.admins:
            print(a)
            bot.send_message(a, f"Вы получили вопрос из чата {webMes.chat.id}:\n{decdata[1]}")
    elif decdata[0] == "subscribe":
        for a in config.admins:
            bot.send_message(a, f"{decdata[1]}")
    elif decdata[0] == "subscribe_question":
        for a in config.admins:
            bot.send_message(a, f"Вопрос по подписке!!!\n{decdata[1]}")
   #отправляем сообщение в ответ на отправку данных из веб-приложения

if __name__ == "__main__":
    bot.polling()