import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Простая база данных прямо в памяти сервера для теста
messages_db = []

@app.route('/')
def home():
    # Отдаем HTML-страницу прямо из Python кода
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Factor X Messenger</title>
        <style>
            body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 50px; }
            .chat-box { border: 1px solid #333; max-width: 400px; margin: 0 auto; padding: 20px; background: #1e1e1e; border-radius: 10px; }
        </style>
    </head>
    <body>
        <div class="chat-box">
            <h2>Factor X</h2>
            <p>Добро пожаловать в мессенджер!</p>
            <p style="color: #4CAF50;">Сервер на Python успешно запущен и работает!</p>
        </div>
    </body>
    </html>
    """

@app.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify(messages_db)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json or {}
    message_text = data.get('message')
    user_id = data.get('user_id', 'Аноним')
    
    if message_text:
        formatted_message = f"{user_id}: {message_text}"
        messages_db.append(formatted_message)
        return jsonify({"status": "success"})
        
    return jsonify({"status": "error"})
