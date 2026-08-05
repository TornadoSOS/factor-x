import os
from flask import Flask, request, jsonify
# Подключаем функцию из твоего нового файла tools.py!
from tools import get_server_time

app = Flask(__name__)

favorites_db = []

@app.route('/')
def home():
    # Получаем точное время с сервера через твой скрипт
    current_time = get_server_time()
    
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
            .note-item {{ border-bottom: 1px solid #333; padding: 5px 0; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Чат Factor X + Время из tools.py -->
            <div class="card">
                <h2>Factor X</h2>
                <p>Добро пожаловать в мессенджер!</p>
                <p style="color: #4CAF50; font-size: 14px;">Время запуска сервера: {current_time}</p>
            </div>

            <!-- Избранное -->
            <div class="card">
                <h3>📁 Избранное</h3>
                <input type="text" id="noteInput" placeholder="Напишите заметку...">
                <button onclick="saveNote()">Сохранить</button>
                <div style="margin-top: 15px;">
                    <div class="notes-list" id="notesContainer">
                        <div class="note-item" style="color: #888;">Заметок пока нет...</div>
                    </div>
                </div>
            </div>

            <!-- Инструктор в ТГ -->
            <div class="card">
                <h3>🤖 Помощь по проекту</h3>
                <p style="font-size: 14px; color: #aaa;">Нужна помощь? Переходи к нашему официальному инструктору в Telegram.</p>
                <a href="https://t.me" target="_blank" class="tg-button">Factor X Инструктор</a>
            </div>
        </div>

        <script>
            function saveNote() {{
                const input = document.getElementById('noteInput');
                const text = input.value.trim();
                if (!text) return;

                const container = document.getElementById('notesContainer');
                if (container.innerText === 'Заметок пока нет...') {{
                    container.innerHTML = '';
                }}

                const div = document.createElement('div');
                div.className = 'note-item';
                div.innerText = text;
                container.appendChild(div);

                input.value = '';
            }}
        </script>
    </body>
    </html>
    """

@app.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify(favorites_db)
