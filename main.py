import os

from telegram.ext import Application
from dotenv import load_dotenv
from database.db import init_db
from handlers.transaction_handlers import get_handlers

# Load environment variables
load_dotenv()

# Initialize database
init_db()

def main():
    # Create application
    application = Application.builder().token(os.getenv('BOT_TOKEN')).build()

    # Add handlers
    for handler in get_handlers():
        application.add_handler(handler)

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    print("Bot is running...")
    application.run_polling()

async def error_handler(update, context):
    """Log errors and notify users."""
    from traceback import format_exc
    print(f"Error occurred: {format_exc()}")
    if update and update.message:
        await update.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

if __name__ == '__main__':
    main() 