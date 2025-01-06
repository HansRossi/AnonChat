import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from collections import deque

# Токен бота
bot = telebot.TeleBot('7330871122:AAHhvZgtrAVjWWAAvXhZ818E5dEBeNGe0jg')

# Очередь пользователей, ищущих собеседника
search_queue = deque()
# Словарь для хранения пар собеседников
active_chats = {}

# Главное меню
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔍 Найти собеседника"), KeyboardButton("❌ Остановить поиск"))
    return markup

# Меню для чата
def chat_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔄 Следующий собеседник"), KeyboardButton("❌ Завершить диалог"))
    return markup

# Стартовое сообщение с меню
@bot.message_handler(commands=['start'])
def start_handler(message: Message):
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в анонимный чат! Используйте меню ниже для действий.\n\n"
        "💬 Команды:\n"
        "🔍 /search - Найти собеседника\n"
        "❌ /stop - Остановить поиск или завершить диалог\n"
        "🔄 /next - Найти нового собеседника",
        reply_markup=main_menu()
    )

# Команда для поиска собеседника
@bot.message_handler(func=lambda m: m.text == "🔍 Найти собеседника")
@bot.message_handler(commands=['search'])
def search_handler(message: Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        bot.send_message(user_id, "❗ Вы уже находитесь в чате.\nИспользуйте кнопку '🔄 Следующий собеседник' для перехода к следующему собеседнику.", reply_markup=chat_menu())
    elif user_id in search_queue:
        bot.send_message(user_id, "❗ Вы уже ищете собеседника.\nПожалуйста, подождите, пока найдем пару.", reply_markup=main_menu())
    else:
        if search_queue:
            partner_id = search_queue.popleft()
            active_chats[user_id] = partner_id
            active_chats[partner_id] = user_id

            bot.send_message(user_id, "✅ Собеседник найден! Начните общение.\n\nДля завершения диалога используйте /stop.", reply_markup=chat_menu())
            bot.send_message(partner_id, "✅ Собеседник найден! Начните общение.\n\nДля завершения диалога используйте /stop.", reply_markup=chat_menu())
        else:
            search_queue.append(user_id)
            bot.send_message(user_id, "🔄 Поиск собеседника... Пожалуйста, подождите.", reply_markup=main_menu())

# Команда для завершения чата
@bot.message_handler(func=lambda m: m.text == "❌ Завершить диалог")
@bot.message_handler(commands=['stop'])
def stop_handler(message: Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)

        bot.send_message(user_id, "❌ Вы завершили чат.\nДля поиска нового собеседника используйте /search.", reply_markup=main_menu())
        bot.send_message(partner_id, "❌ Собеседник покинул чат.", reply_markup=main_menu())
    elif user_id in search_queue:
        search_queue.remove(user_id)
        bot.send_message(user_id, "❌ Вы прекратили поиск собеседника.", reply_markup=main_menu())
    else:
        bot.send_message(user_id, "❗ Вы не находитесь в чате или поиске.\nИспользуйте /search для начала.", reply_markup=main_menu())

# Команда для поиска нового собеседника
@bot.message_handler(func=lambda m: m.text == "🔄 Следующий собеседник")
@bot.message_handler(commands=['next'])
def next_handler(message: Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)

        bot.send_message(user_id, "🔄 Вы завершили текущий диалог. Поиск нового собеседника...", reply_markup=main_menu())
        bot.send_message(partner_id, "❌ Собеседник покинул чат.", reply_markup=main_menu())
        search_handler(message)
    else:
        bot.send_message(user_id, "❗ Вы не находитесь в чате.\nИспользуйте /search для начала поиска собеседника.", reply_markup=main_menu())

# Пересылка текстовых сообщений
@bot.message_handler(content_types=['text'])
def text_message_handler(message: Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        bot.send_message(partner_id, message.text)
    else:
        bot.send_message(user_id, "❗ Вы не находитесь в чате. Используйте меню для действий.", reply_markup=main_menu())

# Пересылка фото
@bot.message_handler(content_types=['photo'])
def photo_message_handler(message: Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        bot.send_photo(partner_id, message.photo[-1].file_id, caption=message.caption)
    else:
        bot.send_message(user_id, "❗ Вы не находитесь в чате. Используйте меню для действий.", reply_markup=main_menu())

# Пересылка видео
@bot.message_handler(content_types=['video'])
def video_message_handler(message: Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        bot.send_video(partner_id, message.video.file_id, caption=message.caption)
    else:
        bot.send_message(user_id, "❗ Вы не находитесь в чате. Используйте меню для действий.", reply_markup=main_menu())

# Пересылка голосовых сообщений
@bot.message_handler(content_types=['voice'])
def voice_message_handler(message: Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        bot.send_voice(partner_id, message.voice.file_id, caption=message.caption)
    else:
        bot.send_message(user_id, "❗ Вы не находитесь в чате. Используйте меню для действий.", reply_markup=main_menu())

# Пересылка видео-сообщений (кружков)
@bot.message_handler(content_types=['video_note'])
def video_note_message_handler(message: Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        bot.send_video_note(partner_id, message.video_note.file_id)
    else:
        bot.send_message(user_id, "❗ Вы не находитесь в чате. Используйте меню для действий.", reply_markup=main_menu())

# Запуск бота
if __name__ == '__main__':
    try:
        bot.polling()
    except Exception as e:
        print(f"Ошибка: {e}")
