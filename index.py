import os
from flask import Flask, request, jsonify
from tools import get_server_time

app = Flask(__name__)

# Наша серверная база данных (пока сервер работает, она всё помнит)
favorites_db = ["Первое системное сообщение Factor X"]

@app.route('/')
def home():
    current_time = get_server_time()
    
    # Сюда мы передадим все заметки из базы данных Python
    notes_html = ""
    for note in favorites_db:
        notes_html += f'<div class="note-item">{note}</div>'

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Factor X Messenger</title>
        <style>
            body {{ background: #121212; color: white; font-family: sans-serif; text-align: center; padding: 20px; }}
            .container {{ max-width: 400px; margin: 0 auto; }}
            .card {{ border: 1px solid #333; padding: 20px; background: #1e1e1e; border-radius: 10px; margin-bottom: 20px; }}
            h2 {{ margin-top: 0; color: #4CAF50; }}
            input {{ width: 80%; padding: 10px; background: #2a2a2a; border: 1px solid #444; border-radius: 5px; color: white; margin-bottom: 10px; }}
            button {{ padding: 10px 20px; background: #4CAF50; border: none; border-radius: 5px; color: white; cursor: pointer; font-weight: bold; }}
            .tg-button {{ display: inline-block; padding: 12px 24px; background: #24A1DE; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 10px; }}
            .notes-list {{ text-align: left; background: #252525; padding: 10px; border-radius: 5px; max-height: 150px; overflow-y: auto; }}
            .note-item {{ border-bottom: 1px solid #333; padding: 5px 0; font-size: 14px; color: #fff; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h2>Factor X</h2>
                <p>Добро пожаловать в мессенджер!</p>
                <p style="color: #4CAF50; font-size: 14px;">Время запуска сервера: {current_time}</p>
            </div>

            <div class="card">
                <h3>📁 Избранное (База Python)</h3>
                <input type="text" id="noteInput" placeholder="Напишите заметку...">
                <button onclick="sendToServer()">Отправить в базу</button>
                <div style="margin-top: 15px;">
                    <div class="notes-list" id="notesContainer">
                        {notes_html}
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>🤖 Помощь по проекту</h3>
                <p style="font-size: 14px; color: #aaa;">Нужна помощь? Переходи к нашему официальному инструктору в Telegram.</p>
                <a href="https://t.me" target="_blank" class="tg-button">Factor X Инструктор</a>
            </div>
        </div>

        <script>
            // Функция отправляет текст на твой Python-сервер
            async function sendToServer() {{
                const input = document.getElementById('noteInput');
                const text = input.value.trim();
                if (!text) return;

                // Отправляем POST-запрос в Python
                const response = await fetch('/send_message', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ message: text, user_id: 'Пользователь' }})
                }});

                const result = await response.json();
                if (result.status === 'success') {{
                    // Просто обновляем страницу, чтобы сервер прислал новый список из базы
                    location.reload();
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json or {}
    message_text = data.get('message')
    
    if message_text:
        # Добавляем в нашу базу данных на Python!
        favorites_db.append(message_text)
        return jsonify({"status": "success"})
        
    return jsonify({"status": "error"})
