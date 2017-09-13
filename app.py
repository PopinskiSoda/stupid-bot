import config
import telebot
import logic
import time
from telebot import types

bot = telebot.TeleBot(config.token)
chats = {}
logic.load_sentences()

markup = types.ReplyKeyboardMarkup()

btn1 = types.KeyboardButton('Ваш сном?')
btn2 = types.KeyboardButton('Нет время сна.')
btn3 = types.KeyboardButton('У меня солидный.')

markup.add(btn1, btn2, btn3)

u_menya_solidnyi = logic.normalize_sentence("Life является странным")


@bot.message_handler(content_types=["text"])
def handle_text_message(message):

    chat_id = message.chat.id

    normalized_message_text = logic.normalize_sentence(message.text)

    if u_menya_solidnyi <= normalized_message_text:
        bot.send_message(chat_id, 'Выберите возвращение, которое отражает их слова на них:', reply_markup=markup)
        return

    if chat_id not in chats:
        chats[chat_id] = {}

    logic.add_sentence(message.text)
    answer = logic.get_random_answer(message.text)

    if "previous_text" in chats[chat_id]:
        if chats[chat_id]["previous_user"] != message.from_user.id:

            previous_text = chats[chat_id]["previous_text"]
            logic.add_answer(previous_text, message.text)
    
    if answer:
        bot.send_message(chat_id, answer)
        chats[chat_id]["previous_text"] = answer
        chats[chat_id]["previous_user"] = 'yarkiybot'
    else:
        chats[chat_id]["previous_text"] = message.text
        chats[chat_id]["previous_user"] = message.from_user.id

if __name__ == '__main__':
     while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(5)
        finally:
            logic.dump_sentences()