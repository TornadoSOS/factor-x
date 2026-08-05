# messages.py
import base64
from flask import jsonify
import database
# Импортируем твою функцию времени из tools.py
from tools import get_server_time  

# Список запрещенных слов или спам-ссылок (можно дополнять)
SPAM_WORDS = ["http://", "https://", "купи крипту", "выиграй приз"]

def encrypt_text(text):
    """Шифрует текст сообщения в секретный код Base64"""
    text_bytes = text.encode('utf-8')
    base64_bytes = base64.b64encode(text_bytes)
    return base64_bytes.decode('utf-8')

def decrypt_text(encrypted_text):
    """Расшифровывает секретный код обратно в обычный текст"""
    try:
        base64_bytes = encrypted_text.encode('utf-8')
        text_bytes = base64.b64decode(base64_bytes)
        return text_bytes.decode('utf-8')
    except Exception:
        return encrypted_text # Если не зашифровано, возвращаем как есть

def add_new_message(room_id, sender, text):
    """Принимает, проверяет на спам, шифрует и сохраняет сообщение с временем"""
    if not text:
        return {"status": "error", "message": "Нет текста"}, 400
        
    # 1. ФИЛЬТР СПАМА: Проверяем текст на запрещенные слова
    for word in SPAM_WORDS:
        if word in text.lower():
            text = "[Сообщение заблокировано системой безопасности Factor X]"
            break
            
    # 2. ТОЧНОЕ ВРЕМЯ: Берем время через твой tools.py
    current_time = get_server_time() # Например, "22:45"
    
    # 3. ШИФРОВАНИЕ: Кодируем текст перед записью в базу данных
    secure_text = encrypt_text(text)
    
    # Формируем структуру сообщения (храним зашифрованным!)
    msg_data = {
        "sender": sender,
        "text": secure_text,
        "time": current_time
    }
    
    if room_id not in database.rooms_db:
        database.rooms_db[room_id] = []
        
    database.rooms_db[room_id].append(msg_data)
    return {"status": "success"}, 200

def generate_messages_html(room_id):
    """Достает сообщения, расшифровывает их и делает красивый HTML"""
    messages_html = ""
    room_messages = database.rooms_db.get(room_id, [])
    
    for msg in room_messages:
        # Расшифровываем текст для вывода на экран телефона
        clean_text = decrypt_text(msg.get("text", ""))
        sender = msg.get("sender", "Аноним")
        msg_time = msg.get("time", "00:00")
        
        if "Система:" in clean_text:
            messages_html += f'<div class="msg-wrapper center"><div class="msg-item system">{clean_text}</div></div>'
        else:
            # Выводим сообщение с красивым ником и временем отправки!
            messages_html += f'''
            <div class="msg-wrapper">
                <div class="msg-item user">
                    <span class="msg-sender">{sender}</span>
                    <p class="msg-text">{clean_text}</p>
                    <span class="msg-time">{msg_time}</span>
                </div>
            </div>
            '''
            
    return messages_html
