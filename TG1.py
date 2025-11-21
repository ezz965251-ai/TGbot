import telebot

bot = telebot.TeleBot('8310431204:AAEXfSgJZLlp-DABnDeZ7VfCWHamFBgSBoc')

@bot.message_handler(commands=['start'])
def start(message):
    mess = (
        f'Приветствую, дорогой {message.from_user.first_name} {message.from_user.last_name or ""}! 🎓\n\n'
        'Этот бот создан исключительно для <b>учеников данного учреждения</b> '
        'и не предназначен для использования посторонними лицами.\n\n'
        'Для продолжения работы введите: <b>Имя Фамилия Пароль</b>\n'
        'Пример: <code>Шилов Ваня dowN1</code>\n\n'
        'Для получения справки используйте команду /help'
    )
    bot.send_message(message.chat.id, mess, parse_mode='HTML')

if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)