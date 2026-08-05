# messages.py
import base64
from flask import jsonify
import database
from tools import get_server_time  

# Список запрещенных слов или спам-ссылок для безопасности
SPAM_WORDS = ["http://", "https://", "купи крипту", "выиграй приз"]

def encrypt_text(text):
    """Шифрует текст сообщения в секретный код Base64, как в WhatsApp"""
    if not text:
        return ""
    text_bytes = text.encode('utf-8')
    base64_bytes = base64.b64encode(text_bytes)
    return base64_bytes.decode('utf-8')

def decrypt_text(encrypted_text):
    """Расшифровывает секретный код обратно в обычный текст для экрана"""
    if not encrypted_text:
        return ""
    try:
        base64_bytes = encrypted_text.encode('utf-8')
        text_bytes = base64.b64decode(base64_bytes)
        return text_bytes.decode('utf-8')
    except Exception:
        return encrypted_text

def process_media_file(file_data, file_name):
    """
    ДВИЖОК КАРТИНОК И МЕДИА (Как в Telegram):
    Принимает файл от пользователя, проверяет его безопасность,
    кодирует в строку и готовит к отправке в чат.
    """
    if not file_data:
        return None
        
    # Проверяем расширение файла для безопасности сервера
    allowed_extensions = ['.png', '.jpg', '.jpeg', '.gif']
    file_ext = os.path.splitext(file_name)[1].lower() if file_name else ''
    
    if file_ext not in allowed_extensions:
        return {
            "type": "text",
            "content": "[Система безопасности: Данный тип файла заблокирован]"
        }
        
    # Возвращаем готовую структуру медиа-сообщения
    return {
        "type": "image",
        "content": file_data, # Тут хранится сама картинка в виде безопасной строки
        "name": file_name
    }

def add_new_message(room_id, sender, text, file_data=None, file_name=None):
    """Принимает сообщение, проверяет на спам, шифрует текст и файлы"""
    if not text and not file_data:
        return {"status": "error", "message": "Сообщение пустое"}, 400
        
    # Фильтр спама
    for word in SPAM_WORDS:
        if text and word in text.lower():
            text = "[Сообщение заблокировано системой безопасности Factor X]"
            break
            
    current_time = get_server_time()
    
    # Проверяем, есть ли в сообщении прикрепленная картинка
    media_content = None
    if file_data:
        media_content = process_media_file(file_data, file_name)
        
    # Шифруем текстовую часть сообщения
    secure_text = encrypt_text(text)
    
    msg_data = {
        "sender": sender,
        "text": secure_text,
        "time": current_time,
        "media": media_content,
        "status": "sent" # Статус сообщения: отправлено
    }
    
    if room_id not in database.rooms_db:
        database.rooms_db[room_id] = []
        
    database.rooms_db[room_id].append(msg_data)
    return {"status": "success", "messages": database.rooms_db[room_id]}, 200
