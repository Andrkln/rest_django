import telebot
import threading
from decouple import config


bot = telebot.TeleBot(config('telegram_bot'))



def telegram_message(name, message, email_of_customer):
    chat_id = '681347698'
    message_to_send = f"""
    
    Hello Andrey 
A person named {name} 
just send you a new email
the messsage is {message} 
and his email is {email_of_customer}
    
    """

    bot.send_message(chat_id, 
        message_to_send)
