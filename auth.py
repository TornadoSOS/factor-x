# auth.py
import json
import os

# Путь к файлу, где пользователи будут храниться "навсегда"
DATA_FILE = "users_storage.json"

def load_users():
    """Загружает пользователей из файла"""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    """Сохраняет пользователей в файл на диске"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False

def register_or_login(username, password):
    """
    Система авторизации: если юзера нет — регистрирует,
    если есть — проверяет пароль.
    """
    if not username or not password:
        return {"status": "error", "message": "Заполните все поля"}, 400
        
    username = str(username).strip().lower()
    users = load_users()
    
    # ЕСЛИ ПОЛЬЗОВАТЕЛЬ УЖЕ ЕСТЬ
    if username in users:
        if users[username]["password"] == password:
            return {
                "status": "success", 
                "message": "Вход выполнен успешно", 
                "username": users[username]["display_name"]
            }, 200
        else:
            return {"status": "error", "message": "Неверный пароль"}, 401
            
    # ЕСЛИ ПОЛЬЗОВАТЕЛЯ НЕТ — РЕГИСТРИРУЕМ НА 20 ЛЕТ
    users[username] = {
        "password": password,
        "display_name": username
    }
    
    if save_users(users):
        return {
            "status": "success", 
            "message": "Аккаунт успешно создан на 20 лет!", 
            "username": username
        }, 201
    else:
        return {"status": "error", "message": "Ошибка записи в базу данных"}, 500
