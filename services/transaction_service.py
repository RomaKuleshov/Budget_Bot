from datetime import datetime
from typing import List, Optional
from database.db import get_db_connection
from models.transaction import Transaction, Category, MonthlyStats

class TransactionService:
    @staticmethod
    def add_transaction(transaction: Transaction) -> None:
        conn = get_db_connection()
        c = conn.cursor()

        # Add transaction
        c.execute("""INSERT INTO transactions 
                     (user_id, type, amount, category, description, date) 
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (transaction.user_id, transaction.type, transaction.amount,
                   transaction.category, transaction.description, transaction.date))

        # Update monthly stats
        date = datetime.strptime(transaction.date, '%Y-%m-%d %H:%M:%S')
        year = date.year
        month = date.month

        if transaction.type == 'income':
            c.execute("""INSERT OR IGNORE INTO monthly_stats 
                         (user_id, year, month, total_income, total_expense)
                         VALUES (?, ?, ?, 0, 0)""", (transaction.user_id, year, month))
            c.execute("""UPDATE monthly_stats 
                         SET total_income = total_income + ? 
                         WHERE user_id = ? AND year = ? AND month = ?""",
                      (transaction.amount, transaction.user_id, year, month))
        else:
            c.execute("""INSERT OR IGNORE INTO monthly_stats 
                         (user_id, year, month, total_income, total_expense)
                         VALUES (?, ?, ?, 0, 0)""", (transaction.user_id, year, month))
            c.execute("""UPDATE monthly_stats 
                         SET total_expense = total_expense + ? 
                         WHERE user_id = ? AND year = ? AND month = ?""",
                      (transaction.amount, transaction.user_id, year, month))

        conn.commit()
        conn.close()

    @staticmethod
    def get_balance(user_id: int) -> float:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT type, amount FROM transactions WHERE user_id = ?", (user_id,))
        transactions = c.fetchall()
        income = sum(amount for typ, amount in transactions if typ == 'income')
        expense = sum(amount for typ, amount in transactions if typ == 'expense')
        conn.close()
        return income - expense

    @staticmethod
    def get_monthly_stats(user_id: int, year: Optional[int] = None, month: Optional[int] = None) -> MonthlyStats:
        conn = get_db_connection()
        c = conn.cursor()

        now = datetime.now()
        query_year = year or now.year
        query_month = month or now.month

        c.execute("""SELECT total_income, total_expense 
                     FROM monthly_stats 
                     WHERE user_id = ? AND year = ? AND month = ?""",
                  (user_id, query_year, query_month))

        result = c.fetchone()
        conn.close()

        if result:
            return MonthlyStats(
                user_id=user_id,
                year=query_year,
                month=query_month,
                total_income=result[0],
                total_expense=result[1]
            )
        return MonthlyStats(
            user_id=user_id,
            year=query_year,
            month=query_month,
            total_income=0,
            total_expense=0
        )

    @staticmethod
    def get_transactions_by_category(user_id: int, category: str, transaction_type: str) -> List[Transaction]:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""SELECT user_id, type, amount, category, description, date
                     FROM transactions
                     WHERE user_id = ? AND category = ? AND type = ?""",
                  (user_id, category, transaction_type))
        transactions = [Transaction(*row) for row in c.fetchall()]
        conn.close()
        return transactions

    @staticmethod
    def get_category_stats(user_id: int, year: Optional[int] = None, month: Optional[int] = None) -> dict:
        conn = get_db_connection()
        c = conn.cursor()

        now = datetime.now()
        query_year = year or now.year
        query_month = month or now.month

        # Get income by category
        c.execute("""SELECT category, SUM(amount)
                     FROM transactions
                     WHERE user_id = ? AND type = 'income'
                     AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
                     GROUP BY category""",
                  (user_id, str(query_year), f"{query_month:02d}"))
        income_by_category = dict(c.fetchall())

        # Get expenses by category
        c.execute("""SELECT category, SUM(amount)
                     FROM transactions
                     WHERE user_id = ? AND type = 'expense'
                     AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
                     GROUP BY category""",
                  (user_id, str(query_year), f"{query_month:02d}"))
        expense_by_category = dict(c.fetchall())

        conn.close()
        return {
            'income_by_category': income_by_category,
            'expense_by_category': expense_by_category
        }

    @staticmethod
    def add_category(category: Category) -> None:
        """Добавление новой категории."""
        conn = get_db_connection()
        c = conn.cursor()

        table = 'income_categories' if category.type == 'income' else 'expense_categories'
        c.execute(f"INSERT INTO {table} (user_id, name) VALUES (?, ?)", 
                 (category.user_id, category.name))

        conn.commit()
        conn.close()

    @staticmethod
    def get_categories(user_id: int, category_type: str) -> List[str]:
        """Получение списка категорий пользователя."""
        conn = get_db_connection()
        c = conn.cursor()

        table = 'income_categories' if category_type == 'income' else 'expense_categories'
        c.execute(f"SELECT name FROM {table} WHERE user_id = ?", (user_id,))
        
        categories = [row[0] for row in c.fetchall()]
        conn.close()
        return categories

    @staticmethod
    def delete_category(user_id: int, category_name: str, category_type: str) -> bool:
        """Удаление категории."""
        conn = get_db_connection()
        c = conn.cursor()

        table = 'income_categories' if category_type == 'income' else 'expense_categories'
        c.execute(f"DELETE FROM {table} WHERE user_id = ? AND name = ?", 
                 (user_id, category_name))
        
        success = c.rowcount > 0
        conn.commit()
        conn.close()
        return success

    @staticmethod
    def clear_transactions(user_id: int, transaction_type: Optional[str] = None) -> None:
        """Очистка транзакций пользователя."""
        conn = get_db_connection()
        c = conn.cursor()

        if transaction_type:
            c.execute("DELETE FROM transactions WHERE user_id = ? AND type = ?", 
                     (user_id, transaction_type))
        else:
            c.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))

        # Обновляем статистику
        c.execute("DELETE FROM monthly_stats WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()

    @staticmethod
    def clear_categories(user_id: int, category_type: Optional[str] = None) -> None:
        """Очистка категорий пользователя."""
        conn = get_db_connection()
        c = conn.cursor()

        if category_type:
            table = 'income_categories' if category_type == 'income' else 'expense_categories'
            c.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
        else:
            c.execute("DELETE FROM income_categories WHERE user_id = ?", (user_id,))
            c.execute("DELETE FROM expense_categories WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close() 