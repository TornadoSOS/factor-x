import os
from flask import Flask, request, jsonify

app = Flask(__name__)

def clean_room_name(name):
    if not name:
        return "main"
    return str(name).strip().lower().replace(" ", "-")

# База данных пользователей и комнат
users_db = {}
rooms_db = {
    "main": ["Система: Добро пожаловать в главный чат Factor X!"]
}

@app.route('/')
def home():
    room_name = request.args.get('room', 'main')
    room_id = clean_room_name(room_name)
    
    if room_id not in rooms_db:
        rooms_db[room_id] = [f"Система: Создана комната #{room_id}"]
        
    messages_html = ""
    for msg in rooms_db[room_id]:
        messages_html += f'<div class="note-item">{msg}</div>'

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
            input {{ width: 85%; padding: 10px; background: #2a2a2a; border: 1px solid #444; border-radius: 5px; color: white; margin-bottom: 10px; font-size: 14px; }}
            button {{ padding: 10px 20px; background: #4CAF50; border: none; border-radius: 5px; color: white; cursor: pointer; font-weight: bold; width: 90%; }}
            .notes-list {{ text-align: left; background: #252525; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto; margin-bottom: 10px; }}
            .note-item {{ border-bottom: 1px solid #333; padding: 5px 0; font-size: 14px; color: #fff; }}
            .room-badge {{ display: inline-block; background: #ff9800; color: black; padding: 3px 8px; border-radius: 3px; font-weight: bold; font-size: 12px; }}
            .hidden {{ display: none; }}
            .logout-btn {{ background: #ff5252; color: white; border: none; padding: 5px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; margin-left: 10px; font-weight: bold; width: auto; display: inline-block; }}
            .logout-btn:hover {{ background: #e04444; }}
        </style>
    </head>
    <body>
        <div class="container">
            
            <!-- ОКНО ВХОДА -->
            <div id="authScreen" class="card">
                <h2>Factor X 🔑</h2>
                <p>Введите имя и пароль для входа или создания аккаунта</p>
                <input type="text" id="usernameInput" placeholder="Ваш никнейм...">
                <input type="password" id="passwordInput" placeholder="Ваш пароль...">
                <button onclick="loginOrRegister()" style="background: #24A1DE;">Войти / Создать аккаунт</button>
                <p id="authError" style="color: #ff5252; font-size: 12px; margin-top: 10px;"></p>
            </div>

            <!-- ИНТЕРФЕЙС МЕССЕНДЖЕРА -->
            <div id="mainScreen" class="hidden">
                <div class="card">
                    <h2>Factor X</h2>
                    <p style="margin-bottom: 5px;">
                        Привет, <span id="userBadge" style="color: #4CAF50; font-weight: bold;"></span>!
                        <button onclick="logoutWithPassword()" class="logout-btn">Выйти</button>
                    </p>
                    <p>Комната: <span class="room-badge">#{room_id}</span></p>
                </div>

                <div class="card">
                    <h3>🔑 Сменить чат</h3>
                    <input type="text" id="roomInput" placeholder="Имя секретного чата...">
                    <button onclick="changeRoom()" style="background: #ff9800; color: black; width: auto;">Перейти</button>
                </div>

                <div class="card">
                    <h3>💬 Чат комнаты</h3>
                    <div class="notes-list" id="notesContainer">
                        {messages_html}
                    </div>
                    <input type="text" id="msgInput" placeholder="Введите сообщение...">
                    <button onclick="sendToServer()">Отправить</button>
                </div>
            </div>

        </div>

        <script>
            const savedUser = localStorage.getItem('fx_user');
            if (savedUser) {{
                showMainScreen(savedUser);
            }}

            function showMainScreen(username) {{
                document.getElementById('authScreen').classList.add('hidden');
                document.getElementById('mainScreen').classList.remove('hidden');
                document.getElementById('userBadge').innerText = username;
            }}

            // Проверка пароля перед выходом
            async function logoutWithPassword() {{
                const currentUser = localStorage.getItem('fx_user');
                const passwordCheck = prompt("Безопасный выход! Введите ваш текущий пароль для подтверждения:");
                
                if (passwordCheck === null) return; // Нажал отмену

                // Отправляем пароль на сервер для сверки
                const response = await fetch('/auth', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ username: currentUser, password: passwordCheck }})
                }});

                const result = await response.json();
                if (result.status === 'success') {{
                    localStorage.removeItem('fx_user');
                    location.reload();
                }} else {{
                    alert("Ошибка! Неверный пароль. Выход заблокирован.");
                }}
            }}

            async function loginOrRegister() {{
                const user = document.getElementById('usernameInput').value.trim();
                const pass = document.getElementById('passwordInput').value.trim();
                const errorBlock = document.getElementById('authError');

                if (!user || !pass) {{
                    errorBlock.innerText = "Заполните все поля!";
                    return;
                }}

                const response = await fetch('/auth', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ username: user, password: pass }})
                }});

                const result = await response.json();
                if (result.status === 'success') {{
                    localStorage.setItem('fx_user', user);
                    showMainScreen(user);
                }} else {{
                    errorBlock.innerText = result.message;
                }}
            }}

            function changeRoom() {{
                const room = document.getElementById('roomInput').value.trim();
                if (room) {{
                    window.location.href = '/?room=' + encodeURIComponent(room);
                }}
            }}

            async function sendToServer() {{
                const input = document.getElementById('msgInput');
                const text = input.value.trim();
                if (!text) return;

                const urlParams = new URLSearchParams(window.location.search);
                const currentRoom = urlParams.get('room') || 'main';
                const currentUser = localStorage.getItem('fx_user') || 'Аноним';

                const response = await fetch('/send_message', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ message: text, room: currentRoom, user: currentUser }})
                }});

                const result = await response.json();
                if (result.status === 'success') {{
                    location.reload();
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json or {}
    user = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not user or not password:
        return jsonify({"status": "error", "message": "Пустые данные"})
        
    if user in users_db:
        if users_db[user] == password:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Неверный пароль!"})
    else:
        users_db[user] = password
        return jsonify({"status": "success"})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json or {}
    message_text = data.get('message')
    room_id = clean_room_name(data.get('room', 'main'))
    user = data.get('user', 'Аноним')
    
    if message_text:
        if room_id not in rooms_db:
            rooms_db[room_id] = []
        rooms_db[room_id].append(f"{user}: {message_text}")
        return jsonify({"status": "success"})
        
    return jsonify({"status": "error"})
