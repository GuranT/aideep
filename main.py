import os
import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DEEPSEEK_KEY = os.environ.get('DEEPSEEK_API_KEY')

# Проверяем переменные
print("🔧 Проверка переменных...")
print(f"BOT_TOKEN: {'✅' if BOT_TOKEN else '❌'}")
print(f"DEEPSEEK_KEY: {'✅' if DEEPSEEK_KEY else '❌'}")

if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не установлен!")
    exit(1)

def start(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    update.message.reply_text(
        "🤖 *DeepSeek AI Assistant запущен!*\n\n"
        "Задавайте любые вопросы и я помогу!",
        parse_mode='Markdown'
    )

def handle_message(update: Update, context: CallbackContext):
    """Обработка всех сообщений"""
    user_text = update.message.text
    
    # Показываем индикатор набора
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        if not DEEPSEEK_KEY:
            update.message.reply_text("❌ API ключ не настроен")
            return
            
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": user_text}],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            json=data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            update.message.reply_text(answer)
        else:
            update.message.reply_text(f"❌ Ошибка API: {response.status_code}")
                    
    except Exception as e:
        logging.error(f"Error: {e}")
        update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")

def main():
    """Основная функция"""
    print("🚀 Запуск бота...")
    
    # Создаем Updater (старая версия API)
    updater = Updater(token=BOT_TOKEN, use_context=True)
    
    # Получаем диспетчер
    dp = updater.dispatcher
    
    # Добавляем обработчики
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    print("🤖 Бот запущен и готов к работе!")
    
    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
