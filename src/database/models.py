"""
Модели базы данных для Customs Calculator Bot.
Использует SQLite для локальной разработки.
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

class Database:
    """Простой менеджер базы данных SQLite."""
    
    def __init__(self, db_path="data/customs_bot.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Возвращает соединение с базой данных."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Инициализирует таблицы базы данных."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            free_calculations_left INTEGER DEFAULT 3,
            last_calculation_date TEXT,
            subscription_end_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Таблица расчётов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            car_data TEXT NOT NULL,
            result_data TEXT NOT NULL,
            is_paid BOOLEAN DEFAULT FALSE,
            payment_amount INTEGER,
            payment_currency TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')
        
        # Таблица платежей (mock для тестирования)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            currency TEXT DEFAULT 'KZT',
            status TEXT DEFAULT 'pending',
            kaspi_transaction_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_or_create_user(self, telegram_id, username=None, first_name=None, last_name=None):
        """Получает или создаёт пользователя."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Проверяем существование пользователя
        cursor.execute(
            'SELECT * FROM users WHERE telegram_id = ?',
            (telegram_id,)
        )
        user = cursor.fetchone()
        
        if user:
            # Обновляем информацию если нужно
            if username or first_name or last_name:
                cursor.execute('''
                UPDATE users 
                SET username = COALESCE(?, username),
                    first_name = COALESCE(?, first_name),
                    last_name = COALESCE(?, last_name),
                    updated_at = CURRENT_TIMESTAMP
                WHERE telegram_id = ?
                ''', (username, first_name, last_name, telegram_id))
                conn.commit()
            
            conn.close()
            return dict(user)
        else:
            # Создаём нового пользователя
            cursor.execute('''
            INSERT INTO users (telegram_id, username, first_name, last_name, free_calculations_left)
            VALUES (?, ?, ?, ?, 3)
            ''', (telegram_id, username, first_name, last_name))
            user_id = cursor.lastrowid
            conn.commit()
            
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            new_user = cursor.fetchone()
            conn.close()
            
            return dict(new_user) if new_user else None
    
    def get_user_calculations_left(self, telegram_id):
        """Возвращает количество оставшихся бесплатных расчётов."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT free_calculations_left FROM users WHERE telegram_id = ?',
            (telegram_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        return result['free_calculations_left'] if result else 3
    
    def use_free_calculation(self, telegram_id):
        """Использует один бесплатный расчёт."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Проверяем, есть ли бесплатные расчёты
        cursor.execute(
            'SELECT free_calculations_left FROM users WHERE telegram_id = ?',
            (telegram_id,)
        )
        result = cursor.fetchone()
        
        if not result or result['free_calculations_left'] <= 0:
            conn.close()
            return False
        
        # Уменьшаем количество бесплатных расчётов
        cursor.execute('''
        UPDATE users 
        SET free_calculations_left = free_calculations_left - 1,
            last_calculation_date = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE telegram_id = ?
        ''', (telegram_id,))
        
        conn.commit()
        conn.close()
        return True
    
    def reset_free_calculations_monthly(self):
        """Сбрасывает бесплатные расчёты в начале месяца."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Сбрасываем только если последний расчёт был в прошлом месяце
        cursor.execute('''
        UPDATE users 
        SET free_calculations_left = 3,
            updated_at = CURRENT_TIMESTAMP
        WHERE (last_calculation_date IS NULL OR 
               strftime('%Y-%m', last_calculation_date) < strftime('%Y-%m', 'now'))
        ''')
        
        conn.commit()
        conn.close()
    
    def save_calculation(self, telegram_id, car_data, result_data, is_paid=False):
        """Сохраняет расчёт в базу данных."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Получаем user_id
        cursor.execute('SELECT id FROM users WHERE telegram_id = ?', (telegram_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return None
        
        user_id = user['id']
        
        # Сохраняем расчёт
        cursor.execute('''
        INSERT INTO calculations (user_id, car_data, result_data, is_paid)
        VALUES (?, ?, ?, ?)
        ''', (
            user_id,
            json.dumps(car_data, ensure_ascii=False),
            json.dumps(result_data, ensure_ascii=False),
            is_paid
        ))
        
        calculation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return calculation_id
    
    def get_user_calculations(self, telegram_id, limit=10):
        """Возвращает историю расчётов пользователя."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Получаем user_id
        cursor.execute('SELECT id FROM users WHERE telegram_id = ?', (telegram_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return []
        
        user_id = user['id']
        
        # Получаем расчёты
        cursor.execute('''
        SELECT id, car_data, result_data, is_paid, created_at
        FROM calculations 
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''', (user_id, limit))
        
        calculations = []
        for row in cursor.fetchall():
            calculations.append({
                'id': row['id'],
                'car_data': json.loads(row['car_data']),
                'result_data': json.loads(row['result_data']),
                'is_paid': bool(row['is_paid']),
                'created_at': row['created_at']
            })
        
        conn.close()
        return calculations
    
    def create_mock_payment(self, telegram_id, amount, currency='KZT'):
        """Создаёт mock-платёж для тестирования."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Получаем user_id
        cursor.execute('SELECT id FROM users WHERE telegram_id = ?', (telegram_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return None
        
        user_id = user['id']
        
        # Создаём платёж
        cursor.execute('''
        INSERT INTO payments (user_id, amount, currency, status)
        VALUES (?, ?, ?, 'completed')
        ''', (user_id, amount, currency))
        
        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return payment_id

# Глобальный экземпляр базы данных
db = Database()

# Тестирование
if __name__ == "__main__":
    # Инициализация
    db.init_database()
    
    # Тестовый пользователь
    user = db.get_or_create_user(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
        last_name="User"
    )
    print(f"User: {user}")
    
    # Проверка бесплатных расчётов
    calculations_left = db.get_user_calculations_left(123456789)
    print(f"Free calculations left: {calculations_left}")
    
    # Использование бесплатного расчёта
    used = db.use_free_calculation(123456789)
    print(f"Used free calculation: {used}")
    
    calculations_left = db.get_user_calculations_left(123456789)
    print(f"Free calculations left after use: {calculations_left}")
    
    print("✅ Database test completed")