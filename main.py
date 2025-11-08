import os
import logging
import telebot
from openai import OpenAI

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DEEPSEEK_KEY = os.environ.get('DEEPSEEK_API_KEY')

print("🔧 Проверка переменных...")
print(f"BOT_TOKEN: {'✅' if BOT_TOKEN else '❌'}")
print(f"DEEPSEEK_KEY: {'✅' if DEEPSEEK_KEY else '❌'}")

if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не установлен!")
    exit(1)

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

# Инициализируем клиент DeepSeek
client = OpenAI(
    api_key=DEEPSEEK_KEY,
    base_url="https://api.deepseek.com"
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "🤖 *DeepSeek AI Assistant* 🚀\n\n"
        "Задавайте любые вопросы! Я помогу с:\n"
        "• Кодом и программированием\n"
        "• Текстами и переводами\n" 
        "• Идеями и решениями\n"
        "• Обучением и объяснениями",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_text = message.text
        
        # Показываем индикатор набора
        bot.send_chat_action(message.chat.id, 'typing')
        
        if not DEEPSEEK_KEY:
            bot.reply_to(message, "❌ API ключ не настроен")
            return
        
        # Используем официальный SDK DeepSeek
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": user_text},
            ],
            max_tokens=2000,
            stream=False
        )
        
        answer = response.choices[0].message.content
        bot.reply_to(message, answer)
                
    except Exception as e:
        logging.error(f"Error: {e}")
        bot.reply_to(message, "❌ Произошла ошибка. Попробуйте еще раз.")

if __name__ == '__main__':
    print("🚀 Запуск бота...")
    print("🤖 Бот запущен и готов к работе!")
    bot.infinity_polling()
