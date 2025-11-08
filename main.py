import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import aiohttp

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

async def start(update: Update, context):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🤖 *DeepSeek AI Assistant запущен!*\n\n"
        "Задавайте любые вопросы и я помогу!",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context):
    """Обработка всех сообщений"""
    user_text = update.message.text
    
    # Показываем индикатор набора
    await update.message.chat.send_action(action="typing")
    
    try:
        if not DEEPSEEK_KEY:
            await update.message.reply_text("❌ API ключ не настроен")
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
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                json=data,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    answer = result["choices"][0]["message"]["content"]
                    await update.message.reply_text(answer)
                else:
                    error_text = await response.text()
                    await update.message.reply_text(f"❌ Ошибка API: {response.status}")
                    
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")

def main():
    """Основная функция"""
    print("🚀 Запуск бота...")
    
    # Создаем приложение
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
