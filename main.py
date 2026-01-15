import telebot
import sqlite3
import os

# Получаем токен из настроек Docker
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("Ошибка: Токен не найден!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# Путь к базе данных внутри контейнера
DB_PATH = '/app/data/bot_database.db'


# Функция создания таблицы
def init_db():
    # Создаем папку, если её нет
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT
        )
    ''')
    conn.commit()
    conn.close()


init_db()


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Напиши текст, я сохраню. Проверка записей: /list")


@bot.message_handler(commands=['list'])
def get_list(message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT text FROM messages WHERE user_id = ?', (message.from_user.id,))
    rows = cursor.fetchall()
    conn.close()

    if rows:
        text = "Твои сообщения:\n" + "\n".join([f"- {r[0]}" for r in rows])
    else:
        text = "Сообщений нет."
    bot.reply_to(message, text)


# Сообщения без команд сохраняются в бд
@bot.message_handler(func=lambda m: True)
def save_msg(message):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (user_id, text) VALUES (?, ?)', (message.from_user.id, message.text))
        conn.commit()
        conn.close()
        bot.reply_to(message, "Записано!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")


if __name__ == '__main__':
    bot.infinity_polling()
