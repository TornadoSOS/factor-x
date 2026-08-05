import datetime

def get_server_time():
    """Функция возвращает текущее время сервера"""
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

def format_username(username):
    """Функция красиво оформляет имя пользователя"""
    if not username.startswith("@"):
        return f"@{username}"
    return username
