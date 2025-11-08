import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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

# Инициализируем клиент DeepSeek
client = OpenAI(
    api_key=DEEPSEEK_KEY,
    base_url="https://api.deepseek.com"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *DeepSeek AI Assistant* 🚀\n\n"
        "Задавайте любые вопросы! Я помогу с:\n"
        "• Кодом и программированием\n"
        "• Текстами и переводами\n" 
        "• Идеями и решениями\n"
        "• Обучением и объяснениями",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Показываем индикатор набора
    await update.message.chat.send_action(action="typing")
    
    try:
        if not DEEPSEEK_KEY:
            await update.message.reply_text("❌ API ключ не настроен")
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
        await update.message.reply_text(answer)
                
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")

def main():
    print("🚀 Запуск бота...")
    
    # Создаем Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Бот запущен и готов к работе!")
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
