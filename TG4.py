import telebot
import hashlib
from datetime import datetime

# Токен бота
bot = telebot.TeleBot('8310431204:AAEXfSgJZLlp-DABnDeZ7VfCWHamFBgSBoc')


# Функция для хэширования пароля
def hash_pass(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# Белый список: (имя, фамилия) → хэш пароля
AUTHORIZED_USERS = {
    ("Беляев", "Илья"): hash_pass("qwe1"),
    ("Гаврилов", "Дима"): hash_pass("qwe2"),
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

# Словарь для отслеживания авторизованных пользователей по chat_id
AUTHORIZED_CHAT_IDS = set()

# Словарь для хранения состояний пользователей (отзывы и другая информация)
user_states = {}

# Словарь для хранения результатов опросов
poll_results = {}


@bot.message_handler(commands=['start', 'help'])
def handle_commands(message):
    #Обработка команд /start и /help
    if message.text == '/start':
        start(message)
    elif message.text == '/help':
        help_cmd(message)


def start(message):
    # При старте удаляем состояние пользователя
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
    bot.send_message(message.chat.id, mess, parse_mode='html')


def help_cmd(message):
 # справка по командам
    help_text = """
🛠️ <b>Доступные команды:</b>

<b>Основные команды:</b>
/start - перезапуск бота
/help - эта справка

<b>Функции бота:</b>
📅 <b>Расписание</b> - просмотр расписания занятий
👨‍🏫 <b>Отзыв о учителе</b> - оставить отзыв о преподавателе
🍽️ <b>Отзыв о столовой</b> - оставить отзыв о питании
📊 <b>Опросы</b> - участие в голосованиях

<b>Как пользоваться:</b>
1. Сначала авторизуйтесь, введя Имя Фамилия Пароль
2. Используйте кнопки меню для навигации
3. Для отзывов выберите соответствующего учителя и напишите ваш отзыв
4. В опросах вы можете голосовать и просматривать результаты

<b>Поддержка:</b>
Если возникли проблемы, обратитесь к администратору (@Ezzglx).
"""

    if message.chat.id in AUTHORIZED_CHAT_IDS:
        # Для авторизованных пользователей добавляем кнопку главного меню
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_menu = telebot.types.KeyboardButton('⬅️ Главное меню')
        markup.add(btn_menu)
        bot.send_message(message.chat.id, help_text, parse_mode='html', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, help_text, parse_mode='html')


@bot.message_handler(func=lambda message: message.chat.id not in AUTHORIZED_CHAT_IDS)
def handle_login(message):
    chat_id = message.chat.id
    text = message.text.strip()
    parts = text.split()

    if len(parts) < 3:
        bot.send_message(chat_id,
                         "❌ Неверный формат.\nПожалуйста, введите: <b>Имя Фамилия Пароль</b>\n\nИспользуйте /help для справки",
                         parse_mode='html')
        return

    # Объединяем все части кроме последней как фамилию (на случай двойных фамилий)
    first_name = parts[0]
    last_name = ' '.join(parts[1:-1])
    password = parts[-1]

    # Приводим к нужному регистру
    first_name = first_name.capitalize()
    last_name = last_name.capitalize()

    user_key = (first_name, last_name)
    if user_key in AUTHORIZED_USERS:
        if AUTHORIZED_USERS[user_key] == hash_pass(password):
            AUTHORIZED_CHAT_IDS.add(chat_id)
            bot.send_message(chat_id, f"✅ Добро пожаловать, {first_name} {last_name}!")
            show_main_menu(chat_id)
        else:
            bot.send_message(chat_id, "❌ Неверный пароль.\n\nИспользуйте /help для справки")
    else:
        bot.send_message(chat_id, "❌ Пользователь не найден в списке учеников.\n\nИспользуйте /help для справки")


def show_main_menu(chat_id):
    """Показывает главное меню с кнопками"""
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = telebot.types.KeyboardButton('📅 Посмотреть расписание')
    btn2 = telebot.types.KeyboardButton('👨‍🏫 Оставить отзыв о учителе')
    btn3 = telebot.types.KeyboardButton('🍽️ Оставить отзыв о столовой')
    btn4 = telebot.types.KeyboardButton('📊 Опросы')
    btn_help = telebot.types.KeyboardButton('🛠️ Помощь')
    markup.add(btn1, btn2, btn3, btn4, btn_help)
    bot.send_message(chat_id, "🏠 Главное меню:", reply_markup=markup)


def show_polls_menu(chat_id):
    """Показывает меню опросов"""
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = telebot.types.KeyboardButton('Питьевой фонтан')
    btn2 = telebot.types.KeyboardButton('📈 Посмотреть результаты')
    btn_back = telebot.types.KeyboardButton('⬅️ Назад в меню')
    btn_help = telebot.types.KeyboardButton('🛠️ Помощь')
    markup.add(btn1, btn2, btn_back, btn_help)
    bot.send_message(chat_id, "📊 Выберите опрос:", reply_markup=markup)


def start_canteen_poll(chat_id):
    """Запускает опрос """
    poll_message = """
🍽️ **Питьевой фонтан**

Как вам идея поставить питьевые фонтанчики по одному на каждый этаж?
    """

    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton('✅ Отлично', callback_data='poll_canteen_5')
    btn2 = telebot.types.InlineKeyboardButton('👍 Хорошо', callback_data='poll_canteen_4')
    btn3 = telebot.types.InlineKeyboardButton('😐 Нормально', callback_data='poll_canteen_3')
    btn4 = telebot.types.InlineKeyboardButton('👎 Плохо', callback_data='poll_canteen_2')

    # Добавляем кнопку "Назад к опросам"
    btn_back = telebot.types.InlineKeyboardButton('⬅️ Назад к опросам', callback_data='back_to_polls')
    markup.add(btn1, btn2, btn3, btn4)
    markup.add(btn_back)

    bot.send_message(chat_id, poll_message, reply_markup=markup, parse_mode='Markdown')


def update_poll_results(message, poll_id):
    """Обновляет результаты опроса"""
    votes = poll_results.get(poll_id, {})

    # Считаем результаты
    results = {'5': 0, '4': 0, '3': 0, '2': 0}
    for vote in votes.values():
        results[vote] += 1

    total_votes = len(votes)

    # Определяем название опроса
    poll_names = {
        'canteen': 'Питьевой фонтан'
    }
    poll_name = poll_names.get(poll_id, 'Опрос')

    # Создаем визуализацию
    result_text = f"""
📊 **Результаты опроса: {poll_name}**

✅ Отлично: {results['5']} голосов
👍 Хорошо: {results['4']} голосов  
😐 Нормально: {results['3']} голосов
👎 Плохо: {results['2']} голосов

Всего голосов: {total_votes}
    """

    # Создаем кнопки с обновленными результатами
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton(
        f'✅ Отлично ({results["5"]})',
        callback_data=f'poll_{poll_id}_5'
    )
    btn2 = telebot.types.InlineKeyboardButton(
        f'👍 Хорошо ({results["4"]})',
        callback_data=f'poll_{poll_id}_4'
    )
    btn3 = telebot.types.InlineKeyboardButton(
        f'😐 Нормально ({results["3"]})',
        callback_data=f'poll_{poll_id}_3'
    )
    btn4 = telebot.types.InlineKeyboardButton(
        f'👎 Плохо ({results["2"]})',
        callback_data=f'poll_{poll_id}_2'
    )

    # Добавляем кнопку "Проголосовать снова" и "Назад"
    btn_vote_again = telebot.types.InlineKeyboardButton('🔄 Проголосовать снова', callback_data=f'vote_again_{poll_id}')
    btn_back = telebot.types.InlineKeyboardButton('⬅️ Назад к опросам', callback_data='back_to_polls')
    markup.add(btn1, btn2, btn3, btn4)
    markup.add(btn_vote_again, btn_back)

    try:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=result_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Ошибка при обновлении сообщения: {e}")
        # Сообщение не изменилось или другая ошибка


def show_all_poll_results(chat_id):
    """Показывает результаты всех опросов"""
    results_text = "📈 **Результаты всех опросов**\n\n"

    poll_names = {
        'canteen': 'Питьевой фонтан'
    }

    for poll_id, poll_name in poll_names.items():
        votes = poll_results.get(poll_id, {})

        results = {'5': 0, '4': 0, '3': 0, '2': 0}
        for vote in votes.values():
            results[vote] += 1

        total_votes = len(votes)

        if total_votes > 0:
            # Вычисляем средний балл
            avg_score = (results['5'] * 5 + results['4'] * 4 + results['3'] * 3 + results['2'] * 2) / total_votes
            results_text += f"{poll_name}:\n"
            results_text += f"✅ {results['5']} 👍 {results['4']} 😐 {results['3']} 👎 {results['2']}\n"
            results_text += f"📊 Средний балл: {avg_score:.1f}/5.0\n"
            results_text += f"👥 Всего голосов: {total_votes}\n\n"
        else:
            results_text += f"{poll_name}: пока нет голосов\n\n"

    # Добавляем кнопки навигации
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_vote = telebot.types.KeyboardButton('Питьевой фонтан')
    btn_back = telebot.types.KeyboardButton('⬅️ Назад к опросам')
    btn_help = telebot.types.KeyboardButton('🛠️ Помощь')
    markup.add(btn_vote, btn_back, btn_help)

    bot.send_message(chat_id, results_text, parse_mode='Markdown', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('poll_'))
def handle_poll_vote(call):
    """Обрабатывает голоса в опросах"""
    user_id = call.from_user.id
    data_parts = call.data.split('_')

    if len(data_parts) != 3:
        return

    poll_type = data_parts[1]  # canteen
    vote_value = data_parts[2]  # 5, 4, 3, 2

    poll_id = poll_type

    if poll_id not in poll_results:
        poll_results[poll_id] = {}

    # Проверяем, голосовал ли уже пользователь
    if user_id in poll_results[poll_id]:
        bot.answer_callback_query(call.id, "Вы уже голосовали в этом опросе!", show_alert=True)
        return

    # Сохраняем результат
    poll_results[poll_id][user_id] = vote_value

    # Обновляем сообщение с результатами
    update_poll_results(call.message, poll_id)

    bot.answer_callback_query(call.id, "Спасибо за ваш голос!")


@bot.callback_query_handler(func=lambda call: call.data.startswith('vote_again_'))
def handle_vote_again(call):
    """Обрабатывает кнопку 'Проголосовать снова'"""
    poll_id = call.data.split('_')[2]  # Получаем poll_id

    # Удаляем голос пользователя, чтобы он мог проголосовать снова
    user_id = call.from_user.id
    if poll_id in poll_results and user_id in poll_results[poll_id]:
        del poll_results[poll_id][user_id]

    # Запускаем опрос заново
    if poll_id == 'canteen':
        start_canteen_poll(call.message.chat.id)

    bot.answer_callback_query(call.id, "Можете проголосовать снова!")


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_polls')
def handle_back_to_polls(call):
    """Обрабатывает кнопку 'Назад к опросам'"""
    show_polls_menu(call.message.chat.id)
    bot.answer_callback_query(call.id)


def show_schedule(chat_id):
    """Показывает расписание"""
    schedule_text = """
📅 Расписание на неделю:
(2025-11-10-2025-11-14)

Понедельник (дистант):
8:00-9:20  
9:30- 10:50 Python (ауд 301 Pyton)
11:30-12:50 Литература РПО (ауд 205 Adobe)
13:00-14:20 Обществознание РПО (ауд 205 Adobe)
15:00-16:20 История РПО (ауд 206(Б) Roblox)


Вторник:
8:00-9:20 
9:30- 10:50 
11:30-12:50 Физическая культура (ауд Физкультура1)
13:00-14:20 Информатика (ауд 301 3 этаж Pyton)
15:00-16:20 Физика РПО (ауд 208 А Youtube)

Среда (дистант):
8:00-9:20 
9:30- 10:50 Индивидуальный проект РПО
11:30-12:50 Python
13:00-14:20 Биология РПО
15:00-16:20 Иностранный язык

Четверг:
8:00-9:20 Математика РПО (20ауд 205 Adobe)
9:30- 10:50 Русский язык РПО (ауд 301 Pyton)
11:30-12:50 введение в специальность (ауд 301 Pyton)
13:00-14:20 Oсновы информационных технологий (ауд 301 Pyton)
15:00-16:20

Пятница:
8:00-9:20 Python (ауд 301 Pyton)
9:30- 10:50 Литература РПО (ауд 205 Adobe)
11:30-12:50 Обществознание РПО (ауд 205 Adobe)
13:00-14:20 История РПО (ауд 206 Roblox)
15:00-16:20


    """

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_back = telebot.types.KeyboardButton('⬅️ Назад в меню')
    btn_help = telebot.types.KeyboardButton('🛠️ Помощь')
    markup.add(btn_back, btn_help)

    bot.send_message(chat_id, schedule_text, reply_markup=markup)


def show_teachers_menu(chat_id):
    """Показывает меню выбора учителя для отзыва"""
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = telebot.types.KeyboardButton('👨‍🏫 Андрей Безотчество (python)')
    btn2 = telebot.types.KeyboardButton('👩‍🏫 Брохоцкая Елизавета(матемитика)')
    btn3 = telebot.types.KeyboardButton('👩‍🏫 Федорова Елизавета (общ,лит)')
    btn4 = telebot.types.KeyboardButton('👩‍🏫 Якинцкая Анна (иностранный)')
    btn5 = telebot.types.KeyboardButton('👩‍🏫 Тамбиева Мадина (маркетинг)')
    btn6 = telebot.types.KeyboardButton('👩‍🏫 Попова Ольга (русский)')
    btn7 = telebot.types.KeyboardButton('👩‍🏫 Брындикова Екатерина (история)')
    btn_back = telebot.types.KeyboardButton('⬅️ Назад в меню')
    btn_help = telebot.types.KeyboardButton('🛠️ Помощь')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn_back, btn_help)
    bot.send_message(chat_id, "Выберите учителя для отзыва:", reply_markup=markup)


def request_canteen_feedback(chat_id):
    """Запрашивает отзыв о столовой"""
    # Устанавливаем состояние ожидания отзыва о столовой
    user_states[chat_id] = {'waiting_for': 'canteen_feedback'}

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_back = telebot.types.KeyboardButton('⬅️ Отмена')
    btn_help = telebot.types.KeyboardButton('🛠️ Помощь')
    markup.add(btn_back, btn_help)

    bot.send_message(chat_id,
                     f"🍽️ Пожалуйста, оставьте ваш отзыв о столовой за сегодня ({datetime.now().strftime('%d.%m.%Y')}):",
                     reply_markup=markup)


def request_teacher_feedback(chat_id, teacher_name):
    """Запрашивает отзыв о конкретном учителе"""
    # Сохраняем информацию о выбранном учителе
    user_states[chat_id] = {
        'waiting_for': 'teacher_feedback',
        'teacher': teacher_name
    }

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_back = telebot.types.KeyboardButton('⬅️ Отмена')
    btn_help = telebot.types.KeyboardButton('🛠️ Помощь')
    markup.add(btn_back, btn_help)

    bot.send_message(chat_id,
                     f"👨‍🏫 Пожалуйста, напишите ваш отзыв о преподавателе {teacher_name}:",
                     reply_markup=markup)


def send_feedback_to_admin(chat_id, feedback_type, target, feedback_text, user_info):
    """Отправляет отзыв администратору"""
    admin_chat_id = 2054288434  # Замените на реальный chat_id администратора

    message = f"""
📝 Новый отзыв!

Тип: {feedback_type}
Объект: {target}
От: {user_info}
Текст отзыва:
{feedback_text}

Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}
Chat ID: {chat_id}
    """

    try:
        bot.send_message(admin_chat_id, message)
        return True
    except Exception as e:
        print(f"Ошибка отправки отзыва: {e}")
        return False


@bot.message_handler(func=lambda message: message.chat.id in AUTHORIZED_CHAT_IDS)
def handle_authorized_messages(message):
    """Обработка сообщений от авторизованных пользователей"""
    chat_id = message.chat.id
    text = message.text

    # Обработка кнопки помощи
    if text == '🛠️ Помощь':
        help_cmd(message)
        return

    # Обработка возврата в главное меню (из помощи)
    if text == '⬅️ Главное меню':
        if chat_id in user_states:
            del user_states[chat_id]
        show_main_menu(chat_id)
        return

    # Обработка отмены
    if text == '⬅️ Отмена':
        if chat_id in user_states:
            del user_states[chat_id]
        show_main_menu(chat_id)
        return

    # Обработка возврата в меню
    if text == '⬅️ Назад в меню':
        if chat_id in user_states:
            del user_states[chat_id]
        show_main_menu(chat_id)
        return

    # Обработка возврата к опросам
    if text == '⬅️ Назад к опросам':
        show_polls_menu(chat_id)
        return

    # Проверяем, ожидает ли бот отзыв от пользователя
    if chat_id in user_states:
        state = user_states[chat_id]

        if state['waiting_for'] == 'teacher_feedback' and text:
            # Обработка отзыва о учителе
            teacher_name = state['teacher']
            user_info = f"{message.from_user.first_name} {message.from_user.last_name or ''}"

            if send_feedback_to_admin(chat_id, "Учитель", teacher_name, text, user_info):
                bot.send_message(chat_id, "✅ Спасибо! Ваш отзыв о преподавателе отправлен.")
            else:
                bot.send_message(chat_id, "❌ Произошла ошибка при отправке отзыва.")

            del user_states[chat_id]
            show_main_menu(chat_id)
            return

        elif state['waiting_for'] == 'canteen_feedback' and text:
            # Обработка отзыва о столовой
            user_info = f"{message.from_user.first_name} {message.from_user.last_name or ''}"
            target = f"Столовая за {datetime.now().strftime('%d.%m.%Y')}"

            if send_feedback_to_admin(chat_id, "Столовая", target, text, user_info):
                bot.send_message(chat_id, "✅ Спасибо! Ваш отзыв о столовой отправлен.")
            else:
                bot.send_message(chat_id, "❌ Произошла ошибка при отправке отзыва.")

            del user_states[chat_id]
            show_main_menu(chat_id)
            return

    # Обработка основных кнопок меню
    if text == '📅 Посмотреть расписание':
        show_schedule(chat_id)

    elif text == '👨‍🏫 Оставить отзыв о учителе':
        show_teachers_menu(chat_id)

    elif text == '🍽️ Оставить отзыв о столовой':
        request_canteen_feedback(chat_id)

    elif text == '📊 Опросы':
        show_polls_menu(chat_id)

    elif text == 'Питьевой фонтан':
        start_canteen_poll(chat_id)

    elif text == '📈 Посмотреть результаты' or text == '📈 Результаты':
        show_all_poll_results(chat_id)

    # Обработка выбора учителя
    elif text in ['👨‍🏫 Андрей Безотчество (python)', '👩‍🏫 Брохоцкая Елизавета(матемитика)',
                  '👩‍🏫 Федорова Елизавета (общ,лит)', '👩‍🏫 Якинцкая Анна (иностранный)',
                  '👩‍🏫 Тамбиева Мадина (маркетинг)', '👩‍🏫 Попова Ольга (русский)',
                  '👩‍🏫 Брындикова Екатерина (история)']:
        teacher_name = text.split(' ', 1)[1]  # Убираем эмодзи
        request_teacher_feedback(chat_id, teacher_name)

    else:
        # Если сообщение не распознано, показываем подсказку
        if chat_id not in user_states:
            bot.send_message(chat_id, "Используйте кнопки меню для навигации или нажмите '🛠️ Помощь' для справки")


# Обработчик для неавторизованных пользователей
@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    if message.chat.id not in AUTHORIZED_CHAT_IDS:
        bot.send_message(message.chat.id,
                         "🔒 Для доступа к функциям бота необходимо авторизоваться.\nВведите: Имя Фамилия Пароль\n\nИспользуйте /help для справки")


# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)