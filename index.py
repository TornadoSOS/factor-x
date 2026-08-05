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
        # Проверяем, кто отправитель, чтобы красиво прижать сообщение
        if "Система:" in msg:
            messages_html += f'<div class="msg-wrapper center"><div class="msg-item system">{msg}</div></div>'
        else:
            messages_html += f'<div class="msg-wrapper"><div class="msg-item user">{msg}</div></div>'

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Factor X Messenger</title>
        <style>
            body {{ background: #0e1621; color: white; font-family: sans-serif; text-align: center; padding: 15px; margin: 0; }}
            .container {{ max-width: 420px; margin: 0 auto; display: flex; flex-direction: column; }}
            .card {{ border: 1px solid #101c2b; padding: 15px; background: #17212b; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }}
            h2 {{ margin-top: 0; color: #5288c1; font-size: 22px; }}
            input {{ width: 85%; padding: 12px; background: #24313f; border: 1px solid #1c2a38; border-radius: 8px; color: white; margin-bottom: 10px; font-size: 14px; outline: none; }}
            input:focus {{ border-color: #5288c1; }}
            button {{ padding: 12px 20px; background: #5288c1; border: none; border-radius: 8px; color: white; cursor: pointer; font-weight: bold; width: 90%; font-size: 14px; }}
            
            /* СТИЛИ ЛЕНТЫ ТЕЛЕГРАМ */
            .notes-list {{ text-align: left; background: #0e1621; padding: 10px; border-radius: 10px; max-height: 280px; overflow-y: auto; margin-bottom: 10px; display: flex; flex-direction: column; gap: 8px; border: 1px solid #1c2a38; }}
            .msg-wrapper {{ display: flex; width: 100%; }}
            .msg-wrapper.center {{ justify-content: center; }}
            
            .msg-item {{ padding: 8px 14px; border-radius: 12px; font-size: 14px; max-width: 75%; word-break: break-word; line-height: 1.4; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }}
            .msg-item.system {{ background: rgba(36, 51, 67, 0.6); color: #7f9fc2; font-size: 12px; text-align: center; border-radius: 8px; padding: 4px 10px; }}
            .msg-item.user {{ background: #182533; border: 1px solid #203040; border-bottom-left-radius: 4px; color: #f5f5f5; }}
            
            .room-badge {{ display: inline-block; background: #2f6ea7; color: white; padding: 3px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }}
            .hidden {{ display: none; }}
            .logout-btn {{ background: #ec5b5b; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; margin-left: 10px; font-weight: bold; width: auto; display: inline-block; }}
            .admin-card {{ border: 1px dashed #ec5b5b; background: #241a1a; }}
            .admin-btn {{ background: #ec5b5b; width: auto; padding: 8px 15px; font-size: 12px; border-radius: 6px; }}
        </style>
    </head> <body>
        <div class="container">
            
            <!-- СЕКРЕТНАЯ ПАНЕЛЬ АДМИНИСТРАТОРА -->
            <div id="adminPanel" class="card admin-card hidden">
                <h3 style="color: #ec5b5b; margin-top: 0;">👑 Панель Создателя</h3>
                <p style="font-size: 13px; color: #aaa;">Вам доступно управление сервером Factor X.</p>
                <button onclick="clearAllServerData()" class="admin-btn">💥 Очистить все чаты</button>
            </div>

            <!-- ОКНО ВХОДА -->
            <div id="authScreen" class="card">
                <h2>Factor X 🔑</h2>
                <p>Введите имя и пароль для входа или создания аккаунта</p>
                <input type="text" id="usernameInput" placeholder="Ваш никнейм...">
                <input type="password" id="passwordInput" placeholder="Ваш пароль...">
                <button onclick="loginOrRegister()" style="background: #24a1de; width: auto; padding: 12px 30px;">Войти / Создать</button>
                <p id="authError" style="color: #ec5b5b; font-size: 12px; margin-top: 10px;"></p>
            </div>

            <!-- ИНТЕРФЕЙС МЕССЕНДЖЕРА -->
            <div id="mainScreen" class="hidden">
                <div class="card">
                    <h2 style="margin-bottom: 10px;">Factor X</h2>
                    <p style="margin: 0; font-size: 14px; color: #aaa;">
                        Привет, <span id="userBadge" style="color: #5288c1; font-weight: bold;"></span>!
                        <button onclick="logoutWithPassword()" class="logout-btn">Выйти</button>
                    </p>
                    <p style="margin: 8px 0 0 0; font-size: 14px;">Комната: <span class="room-badge">#{room_id}</span></p>
                </div>

                <div class="card">
                    <h3 style="margin-top: 0; font-size: 16px; color: #5288c1;">🔑 Сменить чат</h3>
                    <input type="text" id="roomInput" placeholder="Имя секретного чата..." style="margin-bottom: 8px;">
                    <button onclick="changeRoom()" style="background: #2f6ea7; color: white; width: auto; padding: 8px 20px;">Перейти</button>
                </div>

                <div class="card" style="flex-grow: 1;">
                    <h3 style="margin-top: 0; font-size: 16px; color: #5288c1;">💬 Чат комнаты</h3>
                    <div class="notes-list" id="notesContainer">
                        {messages_html}
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center; justify-content: center;">
                        <input type="text" id="msgInput" placeholder="Введите сообщение..." style="margin: 0; width: 70%;">
                        <button onclick="sendToServer()" style="width: auto; padding: 12px 15px;">🚀</button>
                    </div>
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
                
                if (username === 'TornadoSOS') {{
                    document.getElementById('adminPanel').classList.remove('hidden');
                }} else {{
                    document.getElementById('adminPanel').classList.add('hidden');
                }}
                
                // Прокрутка чата вниз при загрузке
                const container = document.getElementById('notesContainer');
                container.scrollTop = container.scrollHeight;
            }}

            async function clearAllServerData() {{
                if (!confirm("Вы уверены, что хотите сбросить ВСЕ сообщения на сервере?")) return;
                const response = await fetch('/admin/clear', {{ method: 'POST' }});
                const result = await response.json();
                if (result.status === 'success') {{
                    location.reload();
                }}
            }}

            async function logoutWithPassword() {{
                const currentUser = localStorage.getItem('fx_user');
                const passwordCheck = prompt("Введите ваш текущий пароль для подтверждения выхода:");
                if (passwordCheck === null) return;

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
                    alert("Неверный пароль!");
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

@app.route('/admin/clear', methods=['POST'])
def admin_clear():
    global rooms_db
    rooms_db = {
        "main": ["Система: Все чаты были полностью очищены Суперадмином!"]
    }
    return jsonify({"status": "success"})
