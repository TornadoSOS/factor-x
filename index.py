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
    "main": ["Система: Добро пожаловать в главный чат Factor X!"],
    "roblox": ["Система: Чат для любителей Роблокс открыт"],
    "games": ["Система: Игровой хаб Factor X"]
}

@app.route('/')
def home():
    room_name = request.args.get('room', 'main')
    room_id = clean_room_name(room_name)
    
    if room_id not in rooms_db:
        rooms_db[room_id] = [f"Система: Создана комната #{room_id}"]
        
    messages_html = ""
    for msg in rooms_db[room_id]:
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
            body {{ background: #0e1621; color: white; font-family: sans-serif; margin: 0; padding: 0; }}
            .container {{ max-width: 420px; margin: 0 auto; background: #17212b; min-height: 100vh; display: flex; flex-direction: column; }}
            
            /* ВЕРХНЯЯ ПАНЕЛЬ ИЗ ТЕЛЕГРАМА */
            .header {{ padding: 15px; background: #17212b; border-bottom: 1px solid #101c2b; text-align: left; }}
            .header-title {{ font-size: 20px; font-weight: bold; margin: 0 0 10px 0; display: flex; justify-content: space-between; align-items: center; }}
            .search-bar {{ width: 90%; padding: 8px 12px; background: #24313f; border: none; border-radius: 8px; color: white; font-size: 14px; outline: none; margin-bottom: 10px; }}
            
            /* ВКЛАДКИ ЧАТОВ */
            .tabs {{ display: flex; gap: 15px; padding: 0 15px 10px 15px; border-bottom: 1px solid #101c2b; font-size: 14px; color: #7f9fc2; font-weight: bold; }}
            .tab.active {{ color: #5288c1; border-bottom: 2px solid #5288c1; padding-bottom: 5px; }}
            
            /* СПИСОК ЧАТОВ С АВАТАРКАМИ */
            .chats-list {{ display: flex; flex-direction: column; }}
            .chat-row {{ display: flex; align-items: center; padding: 12px 15px; border-bottom: 1px solid #101c2b; cursor: pointer; text-align: left; }}
            .chat-row:hover {{ background: #202b36; }}
            .avatar {{ width: 45px; height: 45px; border-radius: 50%; background: #2f6ea7; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 16px; margin-right: 15px; color: white; }}
            .chat-info {{ flex-grow: 1; }}
            .chat-name {{ font-weight: bold; font-size: 15px; margin-bottom: 4px; }}
            .chat-last-msg {{ font-size: 13px; color: #7f9fc2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 250px; }}
            .badge {{ background: #5288c1; color: white; border-radius: 10px; padding: 2px 7px; font-size: 11px; font-weight: bold; }}

            /* ОКНО САМОГО ЧАТА */
            .chat-window {{ display: flex; flex-direction: column; height: 100vh; background: #0e1621; }}
            .chat-header {{ background: #17212b; padding: 10px 15px; display: flex; align-items: center; border-bottom: 1px solid #101c2b; text-align: left; }}
            .notes-list {{ flex-grow: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }}
            .msg-wrapper {{ display: flex; width: 100%; }}
            .msg-wrapper.center {{ justify-content: center; }}
            .msg-item {{ padding: 8px 14px; border-radius: 12px; font-size: 14px; max-width: 75%; word-break: break-word; }}
            .msg-item.system {{ background: rgba(36, 51, 67, 0.6); color: #7f9fc2; font-size: 11px; }}
            .msg-item.user {{ background: #182533; border: 1px solid #203040; border-bottom-left-radius: 4px; }}
            .input-panel {{ display: flex; gap: 8px; padding: 10px; background: #17212b; border-top: 1px solid #101c2b; }}
            
            .hidden {{ display: none; }}
            .logout-btn {{ background: #ec5b5b; color: white; border: none; padding: 4px 8px; border-radius: 5px; font-size: 11px; cursor: pointer; font-weight: bold; }}
            .admin-card {{ border: 1px dashed #ec5b5b; background: #241a1a; padding: 10px; margin: 10px; border-radius: 8px; }}
        </style>
    </head> <body>
        <div class="container">
            
            <!-- ОКНО ВХОДА -->
            <div id="authScreen" class="card" style="padding: 20px; margin: 20px; border-radius: 12px; background: #17212b; border: 1px solid #101c2b;">
                <h2 style="color: #5288c1;">Factor X 🔑</h2>
                <p>Введите имя и пароль для входа в мессенджер</p>
                <input type="text" id="usernameInput" placeholder="Ваш никнейм...">
                <input type="password" id="passwordInput" placeholder="Ваш пароль...">
                <button onclick="loginOrRegister()" style="background: #24a1de; width: auto; padding: 12px 30px;">Войти</button>
                <p id="authError" style="color: #ec5b5b; font-size: 12px; margin-top: 10px;"></p>
            </div>

            <!-- ЭКРАН 1: СПИСОК ЧАТОВ (КАК НА ТВОЕМ СКРИНШОТЕ) -->
            <div id="chatsScreen" class="hidden">
                <div class="header">
                    <div class="header-title">
                        <span>Factor X</span>
                        <span id="userBadgeHeader" style="color: #5288c1; font-size: 14px;"></span>
                    </div>
                    <input type="text" class="search-bar" placeholder="Поиск чатов">
                    <div class="tabs">
                        <div class="tab active">Все чаты</div>
                        <div class="tab">Личные</div>
                        <div class="tab">Новые</div>
                    </div>
                </div>

                <div class="chats-list">
                    <!-- БОТ 1: УПРАВЛЕНИЕ АККАУНТОМ -->
                    <div class="chat-row" onclick="openChat('management')">
                        <div class="avatar" style="background: #ec5b5b;">⚙️</div>
                        <div class="chat-info">
                            <div class="chat-name">Factor X Управление</div>
                            <div class="chat-last-msg">Бот: Безопасность и настройки аккаунта</div>
                        </div>
                        <div class="badge" style="background: #ec5b5b;">⚙️</div>
                    </div>

                    <!-- БОТ 2: ИЗБРАННОЕ -->
                    <div class="chat-row" onclick="openChat('favorites')">
                        <div class="avatar" style="background: #ff9800;">⭐</div>
                        <div class="chat-info">
                            <div class="chat-name">Избранное</div>
                            <div class="chat-last-msg">Ваше личное хранилище заметок</div>
                        </div>
                        <div class="badge">1</div>
                    </div>

                    <!-- ГЛАВНЫЙ ОБЩИЙ ЧАТ -->
                    <div class="chat-row" onclick="openChat('main')">
                        <div class="avatar" style="background: #5288c1;">FX</div>
                        <div class="chat-info">
                            <div class="chat-name">Hooligan's Chat (#main)</div>
                            <div class="chat-last-msg">Общий чат для всех пользователей</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ЭКРАН 2: ОКНО ОТКРЫТОГО ЧАТА -->
            <div id="chatWindowScreen" class="chat-window hidden">
                <div class="chat-header">
                    <button onclick="backToChats()" style="width: auto; background: transparent; color: #5288c1; padding: 5px 10px; margin-right: 10px; font-size: 16px;">< Назад</button>
                    <div style="text-align: left; flex-grow: 1;">
                        <div id="currentChatName" style="font-weight: bold; font-size: 16px;">Чат</div>
                        <div style="font-size: 12px; color: #7f9fc2;">комната: <span id="currentRoomBadge">#main</span></div>
                    </div>
                </div>

                <!-- СЕКРЕТНАЯ ПАНЕЛЬ АДМИНИСТРАТОРА (ВНУТРИ ЧАТА УПРАВЛЕНИЯ) -->
                <div id="adminPanel" class="admin-card hidden">
                    <h3 style="color: #ec5b5b; margin-top: 0; font-size: 14px;">👑 Панель Создателя</h3>
                    <button onclick="clearAllServerData()" class="admin-btn">💥 Очистить все чаты</button>
                </div>

                <!-- БЛОК ДЛЯ КНОПКИ ВЫХОДА В ЧАТЕ УПРАВЛЕНИЯ -->
                <div id="managementOptions" class="hidden" style="padding: 20px; text-align: center;">
                    <p style="color: #aaa; font-size: 14px;">Вы можете безопасно выйти из своего профиля:</p>
                    <button onclick="logoutWithPassword()" style="background: #ec5b5b; width: auto; padding: 10px 25px;">Выйти из аккаунта</button>
                </div>

                <!-- ЛЕНТА СООБЩЕНИЙ ЧАТА -->
                <div class="notes-list" id="notesContainer">
                    {messages_html}
                </div>

                <!-- ПАНЕЛЬ ОТПРАВКИ -->
                <div class="input-panel" id="inputPanelBlock">
                    <input type="text" id="msgInput" placeholder="Введите сообщение..." style="margin: 0; width: 75%;">
                    <button onclick="sendToServer()" style="width: auto; padding: 12px 18px;">🚀</button>
                </div>
            </div>

        </div>
        <script>
            const savedUser = localStorage.getItem('fx_user');
            if (savedUser) {{
                showChatsScreen(savedUser);
            }}

            function showChatsScreen(username) {{
                document.getElementById('authScreen').classList.add('hidden');
                document.getElementById('chatsScreen').classList.remove('hidden');
                document.getElementById('chatWindowScreen').classList.add('hidden');
                document.getElementById('userBadgeHeader').innerText = "@" + username;
            }}

            // Функция открытия конкретного чата
            function openChat(type) {{
                document.getElementById('chatsScreen').classList.add('hidden');
                document.getElementById('chatWindowScreen').classList.remove('hidden');
                
                const chatName = document.getElementById('currentChatName');
                const roomBadge = document.getElementById('currentRoomBadge');
                const inputBlock = document.getElementById('inputPanelBlock');
                const mngOptions = document.getElementById('managementOptions');
                const adminPanel = document.getElementById('adminPanel');
                const currentUser = localStorage.getItem('fx_user');

                // Прячем всё по умолчанию
                inputBlock.classList.remove('hidden');
                mngOptions.classList.add('hidden');
                adminPanel.classList.add('hidden');

                if (type === 'management') {{
                    chatName.innerText = "Factor X Управление";
                    roomBadge.innerText = "system-control";
                    inputBlock.classList.add('hidden'); // Боту управления нельзя писать руками
                    mngOptions.classList.remove('hidden'); // Показываем кнопку Выхода
                    
                    // Если зашел сам Создатель, открываем ему админку прямо тут
                    if (currentUser === 'TornadoSOS') {{
                        adminPanel.classList.remove('hidden');
                    }}
                }} else if (type === 'favorites') {{
                    chatName.innerText = "Избранное";
                    roomBadge.innerText = "favorites";
                    // Перенаправляем на комнату избранного, если мы еще не в ней
                    const urlParams = new URLSearchParams(window.location.search);
                    if (urlParams.get('room') !== 'favorites') {{
                        window.location.href = '/?room=favorites';
                    }}
                }} else {{
                    chatName.innerText = "Hooligan's Chat";
                    roomBadge.innerText = "main";
                    const urlParams = new URLSearchParams(window.location.search);
                    if (urlParams.get('room') !== 'main' && urlParams.get('room') !== null) {{
                        window.location.href = '/?room=main';
                    }}
                }}

                // Скроллим чат вниз
                const container = document.getElementById('notesContainer');
                container.scrollTop = container.scrollHeight;
            }}

            // Проверяем при загрузке, в какой комнате мы находимся, чтобы открыть нужный экран
            const urlParams = new URLSearchParams(window.location.search);
            const currentRoom = urlParams.get('room') || 'main';
            if (savedUser && (currentRoom === 'favorites' || window.location.search.includes('room'))) {{
                showChatsScreen(savedUser);
                if (currentRoom === 'favorites') openChat('favorites');
                else openChat('main');
            }}

            function backToChats() {{
                const urlParams = new URLSearchParams(window.location.search);
                if (urlParams.get('room') === 'favorites') {{
                    window.location.href = '/'; // Сбрасываем комнату при выходе в общий список
                }} else {{
                    showChatsScreen(localStorage.getItem('fx_user'));
                }}
            }}

            async function clearAllServerData() {{
                if (!confirm("Вы уверены, что хотите сбросить ВСЕ сообщения на сервере?")) return;
                const response = await fetch('/admin/clear', {{ method: 'POST' }});
                const result = await response.json();
                if (result.status === 'success') {{
                    window.location.href = '/';
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
                    window.location.href = '/';
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
                    showChatsScreen(user);
                }} else {{
                    errorBlock.innerText = result.message;
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
        "main": ["Система: Все чаты были полностью очищены Суперадмином!"],
        "roblox": ["Система: Чат очищен"],
        "games": ["Система: Чат очищен"]
    }
    return jsonify({"status": "success"})
