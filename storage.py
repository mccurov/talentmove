import sqlite3
import threading
import logging

logger = logging.getLogger(__name__)

DB_NAME = 'vacancies.db'
db_lock = threading.Lock()

def init_db():
    with db_lock:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vacancies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    position TEXT,
                    company TEXT,
                    experience TEXT,
                    salary TEXT,
                    description TEXT,
                    status TEXT
                )
            ''')
            logger.info("Таблица 'vacancies' проверена или создана.")
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")
        finally:
            conn.commit()
            conn.close()

def save_vacancy(vacancy):
    with db_lock:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO vacancies (user_id, username, position, company, experience, salary, description, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vacancy['user_id'],
                vacancy['username'],
                vacancy['position'],
                vacancy['company'],
                vacancy['experience'],
                vacancy['salary'],
                vacancy['description'],
                'pending'
            ))
            vacancy_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Вакансия {vacancy_id} сохранена в базе данных")
            return vacancy_id
        except Exception as e:
            logger.error(f"Ошибка при сохранении вакансии: {e}")
            return None
        finally:
            conn.close()

def get_vacancy(vacancy_id):
    with db_lock:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM vacancies WHERE id = ?', (vacancy_id,))
            row = cursor.fetchone()
            return row_to_dict(row) if row else None
        finally:
            conn.close()

def update_vacancy_status(vacancy_id, status):
    with db_lock:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE vacancies SET status = ? WHERE id = ?', (status, vacancy_id))
            conn.commit()
            logger.info(f"Статус вакансии {vacancy_id} обновлен на {status}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса вакансии {vacancy_id}: {e}")
        finally:
            conn.close()

def get_all_vacancies(status=None):
    with db_lock:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            if status:
                cursor.execute('SELECT * FROM vacancies WHERE status = ?', (status,))
            else:
                cursor.execute('SELECT * FROM vacancies')
            rows = cursor.fetchall()
            return [row_to_dict(row) for row in rows]
        finally:
            conn.close()

def row_to_dict(row):
    return {
        'id': row[0],
        'user_id': row[1],
        'username': row[2],
        'position': row[3],
        'company': row[4],
        'experience': row[5],
        'salary': row[6],
        'description': row[7],
        'status': row[8]
    }

# Функции для сохранения и загрузки TARGET_GROUP_ID
def save_target_group_id(chat_id):
    with db_lock:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)')
        cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', ('TARGET_GROUP_ID', str(chat_id)))
        conn.commit()
        conn.close()

def load_target_group_id():
    with db_lock:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)')
        cursor.execute('SELECT value FROM config WHERE key = ?', ('TARGET_GROUP_ID',))
        row = cursor.fetchone()
        conn.close()
    return int(row[0]) if row else None