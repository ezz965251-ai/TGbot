import telebot
import hashlib
from datetime import datetime

# токен бота
bot = telebot.TeleBot('8310431204:AAEXfSgJZLlp-DABnDeZ7VfCWHamFBgSBoc')

# функция для хэши пароля
def hash_pass(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# имя фамилия хэш пароля
AUTHORIZED_USERS = {
    ("Беляев", "Илья"): hash_pass("qwe1"),
    ("Гаврилов", "Дима"): hash_pass("sey2"),
    ("Гаврилов", "Егор"): hash_pass("xim9"),
    ("Канчуга", "Артем"): hash_pass("glx6"),
    ("Графов", "Леша"): hash_pass("grF4"),
    ("Лобастов", "Данил"): hash_pass("Dan1"),
    ("Кириллов", "Никита"): hash_pass("kiR3"),
    ("Шпехт", "Тихон"): hash_pass("Tix0"),
    ("Хохлов", "Даниил"): hash_pass("Dan2"),
    ("Парфенов", "Тимофей"): hash_pass("T1m0"),
    ("Жгунов", "Леша"): hash_pass("gun0"),
    ("Шохин", "Лев"): hash_pass("lev5"),
    ("Катаев", "Ярик"): hash_pass("kat3"),
    ("Урунбаев", "Хусан"): hash_pass("uru0"),
    ("Умариев", "Умар"): hash_pass("umr1"),
    ("Шангин", "Лев"): hash_pass("lev2"),
    ("Феоктистов", "Виталя"): hash_pass("rea3"),
    ("Болькин", "Галсан"): hash_pass("gal3"),
    ("Лавров", "Ефим"): hash_pass("l0wr"),
    ("Чемякин", "Вадим"): hash_pass("vad1"),
}

AUTHORIZED_CHAT_IDS = set()
user_states = {}
poll_results = {}

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id in user_states:
        del user_states[message.chat.id]

    mess = (
        f'Приветствую, дорогой {message.from_user.first_name} {message.from_user.last_name or ""}! 🎓\n\n'
        'Этот бот создан исключительно для <b>учеников данного учреждения</b> '
        'и не предназначен для использования посторонними лицами.\n\n'
        'Для продолжения работы введите: <b>Имя Фамилия Пароль</b>\n'
        'Пример: <code>Шилов Ваня dowN1</code>\n\n'
        'Для получения справки используйте команду /help'
    )
    bot.send_message(message.chat.id, mess, parse_mode='HTML')

@bot.message_handler(commands=['help'])
def help_cmd(message):
    help_text = """
📖 <b>Справка по использованию бота:</b>

• Для начала работы используйте команду /start
• Для авторизации введите: <b>Имя Фамилия Пароль</b>
• Пример: <code>Иванов Петя password123</code>

Если у вас возникли проблемы, обратитесь к администратору @Ezzglx.
"""
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.chat.id not in AUTHORIZED_CHAT_IDS)
def handle_login(message):
    chat_id = message.chat.id
    text = message.text.strip()
    parts = text.split()

    if len(parts) < 3:
        bot.send_message(chat_id,
                         "❌ Неверный формат.\nПожалуйста, введите: <b>Имя Фамилия Пароль</b>\n\nИспользуйте /help для справки",
                         parse_mode='HTML')
        return
    first_name = parts[0]
    last_name = ' '.join(parts[1:-1])
    password = parts[-1]
    first_name = first_name.capitalize()
    last_name = last_name.capitalize()

    user_key = (first_name, last_name)
    if user_key in AUTHORIZED_USERS:
        if AUTHORIZED_USERS[user_key] == hash_pass(password):
            AUTHORIZED_CHAT_IDS.add(chat_id)
            bot.send_message(chat_id, f"✅ Добро пожаловать, {first_name} {last_name}!")
        else:
            bot.send_message(chat_id, "❌ Неверный пароль.\n\nИспользуйте /help для справки")
    else:
        bot.send_message(chat_id, "❌ Пользователь не найден в списке учеников.\n\nИспользуйте /help для справки")

# запуск
if __name__ == "__main__":
    print("Бот запущен...")

    bot.polling(none_stop=True)

