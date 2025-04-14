# Budget Bot

A Telegram bot for personal finance management that helps users track their income and expenses, manage categories, and analyze their spending habits.

## Features

- 💰 Track income and expenses
- 📊 View balance and statistics
- 📋 Manage categories for income and expenses
- ⚙️ Settings for data management
- 🔄 Easy-to-use interface with keyboard buttons

## Project Structure

```
Budget_Bot/
├── handlers/
│   ├── transaction_handlers.py  # Main bot handlers for transactions
│   └── ...
├── models/
│   ├── transaction.py          # Transaction model
│   └── category.py            # Category model
├── services/
│   ├── transaction_service.py  # Business logic for transactions
│   └── ...
├── config.py                  # Configuration and environment variables
├── main.py                    # Bot entry point
└── requirements.txt           # Project dependencies
```

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Budget_Bot.git
cd Budget_Bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
# Create necessary tables and initial data
python setup_database.py
```

## Running the Bot

1. Start the bot:
```bash
python main.py
```

## Main Commands

- `/start` - Start the bot and show main menu
- `➕ Доход` - Add income
- `➖ Расход` - Add expense
- `💰 Баланс` - View current balance
- `📊 Статистика` - View spending statistics
- `📋 Категории` - Manage categories
- `⚙ Настройки` - Access settings

## Settings Menu Options

- 🗑 Очистить все доходы - Clear all income records
- 🗑 Очистить все расходы - Clear all expense records
- ❌ Удалить категории доходов - Delete income categories
- ❌ Удалить категории расходов - Delete expense categories
- 🔙 Вернуться в главное меню - Return to main menu

## Development

### Adding New Features

1. Create new handlers in the `handlers` directory
2. Add necessary models in the `models` directory
3. Implement business logic in the `services` directory
4. Update the conversation handler in `main.py`


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Additional Information

### Security Considerations

- Never commit your `.env` file
- Keep your bot token secure
- Use environment variables for sensitive data
- Implement rate limiting for API calls

### Performance Tips

- Use database indexes for frequently queried fields
- Implement caching for frequently accessed data
- Use batch operations for bulk data processing

### Best Practices

- Keep transaction records atomic
- Implement proper error handling
- Use logging for debugging
- Follow PEP 8 style guide
- Write meaningful commit messages 