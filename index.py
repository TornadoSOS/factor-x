import sqlite3

DB_PATH = "/tmp/factorx_flask.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            nickname TEXT NOT NULL,
            password TEXT NOT NULL,
            avatar TEXT DEFAULT '',
            theme TEXT DEFAULT 'dark'
        )
    ''')
    # Таблица заметок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    # Таблица личных сообщений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sender) REFERENCES users(username),
            FOREIGN KEY(receiver) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()
from flask import Blueprint, request, jsonify
from .db import get_db_connection
import sqlite3

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    nickname = data.get('nickname', '').strip()
    username = data.get('username', '').lower().strip()
    password = data.get('password', '')

    if not nickname or not username or not password:
        return jsonify({"detail": "Все поля обязательны для заполнения"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, nickname, password) VALUES (?, ?, ?)",
            (username, nickname, password)
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Регистрация успешна"})
    except sqlite3.IntegrityError:
        return jsonify({"detail": "Этот @username уже занят"}), 400
    finally:
        conn.close()

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '').lower().strip()
    password = data.get('password', '')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, nickname, avatar, theme FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"detail": "Неверный юзернейм или пароль"}), 401

    return jsonify({
        "status": "success",
        "user": dict(user)
    })
from flask import Blueprint, request, jsonify
from .db import get_db_connection

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/search', methods=['GET'])
def search():
    username = request.args.get('username', '').lower().strip()
    if not username:
        return jsonify({"detail": "Укажите username для поиска"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nickname, username, avatar FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"detail": "Пользователь не найден"}), 404
    return jsonify(dict(user))

@user_bp.route('/api/profile/update', methods=['POST'])
def update_profile():
    data = request.json or {}
    current_user = data.get('current_username', '').lower().strip()
    new_nick = data.get('new_nickname', '').strip()
    new_user = data.get('new_username', '').lower().strip()
    new_avatar = data.get('new_avatar', '').strip()
    new_theme = data.get('new_theme', 'dark').strip()

    if not new_nick or not new_user:
        return jsonify({"detail": "Имя и юзернейм не могут быть пустыми"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    if current_user != new_user:
        cursor.execute("SELECT username FROM users WHERE username = ?", (new_user,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"detail": "Новый юзернейм уже занят"}), 400

    cursor.execute("""
        UPDATE users 
        SET nickname = ?, username = ?, avatar = ?, theme = ? 
        WHERE username = ?
    """, (new_nick, new_user, new_avatar, new_theme, current_user))
    
    cursor.execute("UPDATE notes SET username = ? WHERE username = ?", (new_user, current_user))
    cursor.execute("UPDATE messages SET sender = ? WHERE sender = ?", (new_user, current_user))
    cursor.execute("UPDATE messages SET receiver = ? WHERE receiver = ?", (new_user, current_user))
    
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})
from flask import Blueprint, request, jsonify
from .db import get_db_connection

chats_bp = Blueprint('chats', __name__)

@chats_bp.route('/api/notes', methods=['GET', 'POST'])
def handle_notes():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        username = request.args.get('username', '').lower().strip()
        cursor.execute("SELECT text FROM notes WHERE username = ?", (username,))
        rows = cursor.fetchall()
        conn.close()
        return jsonify({"notes": [row["text"] for row in rows]})

    elif request.method == 'POST':
        data = request.json or {}
        username = data.get('username', '').lower().strip()
        text = data.get('text', '').strip()
        if not text:
            return jsonify({"status": "ignored"})
        
        cursor.execute("INSERT INTO notes (username, text) VALUES (?, ?)", (username, text))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})

@chats_bp.route('/api/dialogs', methods=['GET'])
def get_dialogs():
    username = request.args.get('username', '').lower().strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT CASE WHEN sender = ? THEN receiver ELSE sender END AS peer
        FROM messages WHERE sender = ? OR receiver = ?
    """, (username, username, username))
    
    dialogs = [row["peer"] for row in cursor.fetchall()]
    result = []
    for person in dialogs:
        cursor.execute("SELECT nickname, username, avatar FROM users WHERE username = ?", (person,))
        u_info = cursor.fetchone()
        if u_info:
            result.append(dict(u_info))
            
    conn.close()
    return jsonify({"dialogs": result})

@chats_bp.route('/api/chat/history', methods=['GET'])
def get_history():
    u1 = request.args.get('user1', '').lower().strip()
    u2 = request.args.get('user2', '').lower().strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, receiver, text, timestamp FROM messages 
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
        ORDER BY timestamp ASC
    """, (u1, u2, u2, u1))
    
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"history": history})

@chats_bp.route('/api/chat/send', methods=['POST'])
def send_msg():
    data = request.json or {}
    sender = data.get('sender', '').lower().strip()
    receiver = data.get('receiver', '').lower().strip()
    text = data.get('text', '').strip()

    if not text:
        return jsonify({"detail": "Сообщение пустое"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, receiver, text) VALUES (?, ?, ?)", (sender, receiver, text))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})
from flask import Flask, jsonify
from flask_cors import CORS
from .db import init_db
from .auth import auth_bp
from .user import user_bp
from .chats import chats_bp

app = Flask(__name__)
CORS(app)  # Разрешаем кросс-доменные запросы

# Инициализируем SQLite таблицы
init_db()

# Регистрируем все наши блупринты (модули)
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(chats_router if 'chats_router' in locals() else chats_bp)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "Factor X Flask Backend is Active!"})

# Этот блок нужен для локального тестирования на ПК или телефоне, если запускаешь вручную
if __name__ == '__main__':
    app.run(debug=True, port=5000)
