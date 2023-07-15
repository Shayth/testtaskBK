import threading
import time
import pygsheets
import telebot

from config import *
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot(tg_token)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Приветствую!\n')
    user_id = message.chat.id
    username = message.from_user.username
    file = open("userdata.txt", "w")
    file.write(f'{username} : {user_id} \n')
    file.close()


def check_task():
    t = threading.Timer(1.0, check_task)
    t.start()
    phone_id = wks.get_values('A2', 'A2')
    ready_id = (''.join(map(str, phone_id)).strip("[''])"))
    with open('userdata.txt', 'r') as f:
        if ready_id in f.read():
            t.cancel()
            get_another_info()
        else:
            pass


def get_another_info():
    phone_id = wks.get_values('A2', 'A2')
    test_table = wks.get_values('B2', 'B2')
    date_table = wks.get_values('C2', 'C2')
    time_table = wks.get_values('D2', 'D2')
    answer_time = wks.get_values('E2', 'E2')
    ready_id = (''.join(map(str, phone_id)).strip("[''])"))
    ready_test_table = (''.join(map(str, test_table)).strip("[''])"))
    ready_date_table = (''.join(map(str, date_table)).strip("[''])"))
    ready_time_table = (''.join(map(str, time_table)).strip("[''])"))
    ready_answer_time = (''.join(map(str, answer_time)).strip("[''])"))
    markup_inline = InlineKeyboardMarkup()
    markup_inline.row_width = 2
    markup_inline.add(InlineKeyboardButton("Выполнено", callback_data="cb_yes"),
                      InlineKeyboardButton("Не выполнено", callback_data="cb_no"))
    butmsg = bot.send_message(ready_id, f'{ready_test_table}\nВремя на ответ: {ready_answer_time} секунд',
                     reply_markup=markup_inline)
    print('Кнопки вызваны')
    start_time = 0
    while start_time < int(ready_answer_time):
        start_time = start_time + 1
        time.sleep(1)
    else:
        bot.edit_message_text("Время истекло", chat_id=ready_id, message_id=butmsg.message_id)
        bot.send_message(admin_id, "[Админ, время выполнения задания истекло]")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_yes":
        bot.answer_callback_query(call.id, "")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выполнено",
                              reply_markup=None)
        bot.send_message(admin_id, "[Админ, задание выполнено]")
    if call.data == "cb_no":
        bot.answer_callback_query(call.id, "")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Не Выполнено",
                              reply_markup=None)
        bot.send_message(admin_id, "[Админ, задание не выполнено]")


if __name__ == '__main__':
    admin_id = admin_id_tg
    gc = pygsheets.authorize(service_file=creds_path)
    sh = gc.open_by_url(table_url)
    wks = sh[0]
    check_task()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            print(e)
