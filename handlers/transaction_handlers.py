from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from models.transaction import Transaction, Category
from services.transaction_service import TransactionService

# States for ConversationHandler
GET_AMOUNT, GET_CATEGORY, ADD_INCOME_CATEGORY, ADD_EXPENSE_CATEGORY, SETTINGS_MENU, DELETE_CATEGORY = range(6)

def main_menu_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("➕ Доход"), KeyboardButton("➖ Расход")],
        [KeyboardButton("💰 Баланс"), KeyboardButton("📊 Статистика")],
        [KeyboardButton("📋 Категории"), KeyboardButton("⚙ Настройки")]
    ], resize_keyboard=True)

def cancel_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("❌ Отмена")]
    ], resize_keyboard=True)

def categories_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("➕ Добавить категорию доходов")],
        [KeyboardButton("➕ Добавить категорию расходов")],
        [KeyboardButton("📋 Показать все категории")],
        [KeyboardButton("🔙 Назад")]
    ], resize_keyboard=True)

def get_category_keyboard(user_id: int, transaction_type: str) -> ReplyKeyboardMarkup:
    """Создает клавиатуру с доступными категориями и кнопкой создания новой."""
    categories = TransactionService.get_categories(user_id, transaction_type)
    keyboard = []
    
    # Добавляем существующие категории
    for category in categories:
        keyboard.append([KeyboardButton(category)])
    
    # Добавляем кнопки для создания новой категории и отмены
    keyboard.append([KeyboardButton("➕ Создать новую категорию")])
    keyboard.append([KeyboardButton("❌ Отмена")])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def settings_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🗑 Очистить все доходы")],
        [KeyboardButton("🗑 Очистить все расходы")],
        [KeyboardButton("❌ Удалить категории доходов")],
        [KeyboardButton("❌ Удалить категории расходов")],
        [KeyboardButton("🔙 Вернуться в главное меню")]
    ], resize_keyboard=True)

def category_selection_keyboard(user_id: int, category_type: str):
    categories = TransactionService.get_categories(user_id, category_type)
    keyboard = []
    
    for category in categories:
        keyboard.append([KeyboardButton(category)])
    
    keyboard.append([KeyboardButton("❌ Отмена")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 <b>Бот для учета личных финансов</b>\n\n"
        "Выберите действие:",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )

async def add_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['transaction_type'] = 'income'
    await update.message.reply_text(
        "Введите сумму дохода:",
        reply_markup=cancel_keyboard()
    )
    return GET_AMOUNT

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['transaction_type'] = 'expense'
    await update.message.reply_text(
        "Введите сумму расхода:",
        reply_markup=cancel_keyboard()
    )
    return GET_AMOUNT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отмены для всех состояний."""
    await update.message.reply_text(
        "Действие отменено",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Отмена":
        return await cancel(update, context)

    try:
        amount = float(update.message.text)
        if amount <= 0:
            await update.message.reply_text("Сумма должна быть больше нуля!")
            return GET_AMOUNT

        context.user_data['amount'] = amount
        user_id = update.message.from_user.id
        transaction_type = context.user_data['transaction_type']
        
        # Получаем клавиатуру с категориями
        keyboard = get_category_keyboard(user_id, transaction_type)
        
        await update.message.reply_text(
            "Выберите категорию или создайте новую:",
            reply_markup=keyboard
        )
        return GET_CATEGORY
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректную сумму!")
        return GET_AMOUNT

async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Отмена":
        return await cancel(update, context)

    user_id = update.message.from_user.id
    transaction_type = context.user_data['transaction_type']
    amount = context.user_data['amount']
    category = update.message.text

    if category == "➕ Создать новую категорию":
        context.user_data['amount'] = amount  # Сохраняем сумму для использования после создания категории
        if transaction_type == 'income':
            await update.message.reply_text(
                "Введите название новой категории доходов:",
                reply_markup=cancel_keyboard()
            )
            return ADD_INCOME_CATEGORY
        else:
            await update.message.reply_text(
                "Введите название новой категории расходов:",
                reply_markup=cancel_keyboard()
            )
            return ADD_EXPENSE_CATEGORY

    transaction = Transaction(
        user_id=user_id,
        type=transaction_type,
        amount=amount,
        category=category
    )
    TransactionService.add_transaction(transaction)

    await update.message.reply_text(
        f"✅ {'Доход' if transaction_type == 'income' else 'Расход'} "
        f"на сумму {amount:.2f} руб. успешно добавлен!"
        f"{' (Категория: ' + category + ')' if category else ''}",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def skip_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    transaction_type = context.user_data['transaction_type']
    amount = context.user_data['amount']

    transaction = Transaction(
        user_id=user_id,
        type=transaction_type,
        amount=amount
    )
    TransactionService.add_transaction(transaction)

    await update.message.reply_text(
        f"✅ {'Доход' if transaction_type == 'income' else 'Расход'} "
        f"на сумму {amount:.2f} руб. успешно добавлен!",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    balance = TransactionService.get_balance(user_id)
    await update.message.reply_text(
        f"Ваш текущий баланс: <b>{balance:.2f} руб.</b>",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    stats = TransactionService.get_monthly_stats(user_id)
    category_stats = TransactionService.get_category_stats(user_id)

    message = (
        "📊 <b>Статистика за текущий месяц</b>\n\n"
        f"Доходы: <b>{stats.total_income:.2f} руб.</b>\n"
        f"Расходы: <b>{stats.total_expense:.2f} руб.</b>\n"
        f"Баланс: <b>{stats.balance:.2f} руб.</b>\n\n"
    )

    if category_stats['income_by_category']:
        message += "<b>Доходы по категориям:</b>\n"
        for category, amount in category_stats['income_by_category'].items():
            message += f"• {category}: {amount:.2f} руб.\n"

    if category_stats['expense_by_category']:
        message += "\n<b>Расходы по категориям:</b>\n"
        for category, amount in category_stats['expense_by_category'].items():
            message += f"• {category}: {amount:.2f} руб.\n"

    await update.message.reply_text(
        message,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )

async def categories_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 <b>Управление категориями</b>",
        reply_markup=categories_keyboard(),
        parse_mode="HTML"
    )

async def add_income_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите название новой категории доходов:",
        reply_markup=cancel_keyboard()
    )
    return ADD_INCOME_CATEGORY

async def add_expense_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите название новой категории расходов:",
        reply_markup=cancel_keyboard()
    )
    return ADD_EXPENSE_CATEGORY

async def handle_new_income_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Отмена":
        return await cancel(update, context)

    user_id = update.message.from_user.id
    category_name = update.message.text.strip()
    amount = context.user_data.get('amount')

    category = Category(
        user_id=user_id,
        name=category_name,
        type='income'
    )
    TransactionService.add_category(category)

    if amount is not None:
        # Если категория создается в процессе добавления транзакции
        transaction = Transaction(
            user_id=user_id,
            type='income',
            amount=amount,
            category=category_name
        )
        TransactionService.add_transaction(transaction)
        
        await update.message.reply_text(
            f"✅ Категория доходов '{category_name}' успешно создана!\n"
            f"Доход на сумму {amount:.2f} руб. успешно добавлен!",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END
    else:
        # Если категория создается отдельно
        await update.message.reply_text(
            f"✅ Категория доходов '{category_name}' успешно добавлена!",
            reply_markup=categories_keyboard()
        )
        return ConversationHandler.END

async def handle_new_expense_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Отмена":
        return await cancel(update, context)

    user_id = update.message.from_user.id
    category_name = update.message.text.strip()
    amount = context.user_data.get('amount')

    category = Category(
        user_id=user_id,
        name=category_name,
        type='expense'
    )
    TransactionService.add_category(category)

    if amount is not None:
        # Если категория создается в процессе добавления транзакции
        transaction = Transaction(
            user_id=user_id,
            type='expense',
            amount=amount,
            category=category_name
        )
        TransactionService.add_transaction(transaction)
        
        await update.message.reply_text(
            f"✅ Категория расходов '{category_name}' успешно создана!\n"
            f"Расход на сумму {amount:.2f} руб. успешно добавлен!",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END
    else:
        # Если категория создается отдельно
        await update.message.reply_text(
            f"✅ Категория расходов '{category_name}' успешно добавлена!",
            reply_markup=categories_keyboard()
        )
        return ConversationHandler.END

async def show_all_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    income_categories = TransactionService.get_categories(user_id, 'income')
    expense_categories = TransactionService.get_categories(user_id, 'expense')

    message = "📋 <b>Ваши категории:</b>\n\n"
    
    if income_categories:
        message += "<b>Доходы:</b>\n"
        for category in income_categories:
            message += f"• {category}\n"
    
    if expense_categories:
        message += "\n<b>Расходы:</b>\n"
        for category in expense_categories:
            message += f"• {category}\n"
    
    if not income_categories and not expense_categories:
        message += "У вас пока нет категорий. Добавьте их через меню категорий."

    await update.message.reply_text(
        message,
        reply_markup=categories_keyboard(),
        parse_mode="HTML"
    )

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚙ <b>Настройки</b>\n\n"
        "Выберите действие:",
        reply_markup=settings_keyboard(),
        parse_mode="HTML"
    )
    return SETTINGS_MENU

async def handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    action = update.message.text

    if action == "🔙 Вернуться в главное меню":
        await update.message.reply_text(
            "Возврат в главное меню",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END

    if action == "🗑 Очистить все доходы":
        TransactionService.clear_transactions(user_id, 'income')
        await update.message.reply_text(
            "✅ Все доходы успешно удалены!",
            reply_markup=settings_keyboard()
        )
        return SETTINGS_MENU

    if action == "🗑 Очистить все расходы":
        TransactionService.clear_transactions(user_id, 'expense')
        await update.message.reply_text(
            "✅ Все расходы успешно удалены!",
            reply_markup=settings_keyboard()
        )
        return SETTINGS_MENU

    if action == "❌ Удалить категории доходов":
        categories = TransactionService.get_categories(user_id, 'income')
        if not categories:
            await update.message.reply_text(
                "У вас нет категорий доходов для удаления.",
                reply_markup=settings_keyboard()
            )
            return SETTINGS_MENU
        
        context.user_data['category_type'] = 'income'
        await update.message.reply_text(
            "Выберите категорию для удаления:",
            reply_markup=category_selection_keyboard(user_id, 'income')
        )
        return DELETE_CATEGORY

    if action == "❌ Удалить категории расходов":
        categories = TransactionService.get_categories(user_id, 'expense')
        if not categories:
            await update.message.reply_text(
                "У вас нет категорий расходов для удаления.",
                reply_markup=settings_keyboard()
            )
            return SETTINGS_MENU
        
        context.user_data['category_type'] = 'expense'
        await update.message.reply_text(
            "Выберите категорию для удаления:",
            reply_markup=category_selection_keyboard(user_id, 'expense')
        )
        return DELETE_CATEGORY

async def handle_category_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Отмена":
        await update.message.reply_text(
            "Возврат в настройки",
            reply_markup=settings_keyboard()
        )
        return SETTINGS_MENU

    user_id = update.message.from_user.id
    category_name = update.message.text
    category_type = context.user_data['category_type']

    if TransactionService.delete_category(user_id, category_name, category_type):
        await update.message.reply_text(
            f"✅ Категория '{category_name}' успешно удалена!",
            reply_markup=settings_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Ошибка при удалении категории.",
            reply_markup=settings_keyboard()
        )
    return SETTINGS_MENU

def get_handlers():
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^➕ Доход$"), add_income),
            MessageHandler(filters.Regex("^➖ Расход$"), add_expense),
            MessageHandler(filters.Regex("^➕ Добавить категорию доходов$"), add_income_category),
            MessageHandler(filters.Regex("^➕ Добавить категорию расходов$"), add_expense_category),
            MessageHandler(filters.Regex("^📋 Показать все категории$"), show_all_categories),
            MessageHandler(filters.Regex("^⚙ Настройки$"), settings_menu)
        ],
        states={
            GET_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount),
                MessageHandler(filters.Regex("^❌ Отмена$"), cancel)
            ],
            GET_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_category),
                MessageHandler(filters.Regex("^❌ Отмена$"), cancel)
            ],
            ADD_INCOME_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_income_category),
                MessageHandler(filters.Regex("^❌ Отмена$"), cancel)
            ],
            ADD_EXPENSE_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_expense_category),
                MessageHandler(filters.Regex("^❌ Отмена$"), cancel)
            ],
            SETTINGS_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_settings),
                MessageHandler(filters.Regex("^❌ Отмена$"), cancel)
            ],
            DELETE_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_category_deletion),
                MessageHandler(filters.Regex("^❌ Отмена$"), cancel)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    return [
        CommandHandler("start", start),
        conv_handler,
        MessageHandler(filters.Regex("^💰 Баланс$"), show_balance),
        MessageHandler(filters.Regex("^📊 Статистика$"), show_stats),
        MessageHandler(filters.Regex("^📋 Категории$"), categories_menu),
        MessageHandler(filters.Regex("^🔙 Назад$"), start)
    ] 