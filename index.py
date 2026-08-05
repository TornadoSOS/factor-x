import os
from flask import Flask, request, jsonify, render_template_string
import database

app = Flask(__name__)

def clean_room_name(name):
    if not name:
        return "main"
    return str(name).strip().lower().replace(" ", "-")

@app.route('/')
def home():
    # Берем комнату из ссылки
    r_name = request.args.get('room', 'main')
    room_id = clean_room_name(r_name)
    
    # Если комнаты нет в базе — создаем её
    if room_id not in database.rooms_db:
        sys_msg = f"Система: Создана комната #{room_id}"
        database.rooms_db[room_id] = [sys_msg]
        
    # Генерируем HTML-код для сообщений
    messages_html = ""
    for msg in database.rooms_db[room_id]:
        if "Система:" in msg:
            messages_html += f'<div class="msg-wrapper center"><div class="msg-item system">{msg}</div></div>'
        else:
            messages_html += f'<div class="msg-wrapper"><div class="msg-item user">{msg}</div></div>'
            
    # Тут ниже должен идти твой return """<!DOCTYPE html>...""" со всем дизайном HTML

    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Factor X Messenger</title>
        <style>
            body { background: #0b0f17; color: #e2e8f0; font-family: sans-serif; margin: 0; padding: 0; }
            .container { max-width: 420px; margin: 0 auto; background: #121824; min-height: 100vh; display: flex; flex-direction: column; box-shadow: 0 0 30px rgba(0, 230, 118, 0.1); }
            .header { padding: 15px; background: #121824; border-bottom: 1px solid #1f293d; text-align: left; }
            .header-title { font-size: 22px; font-weight: bold; margin: 0 0 12px 0; display: flex; justify-content: space-between; align-items: center; color: #00e676; text-shadow: 0 0 10px rgba(0, 230, 118, 0.3); }
            .search-bar { width: 90%; padding: 10px 14px; background: #1e293b; border: 1px solid #334155; border-radius: 8px; color: white; font-size: 14px; outline: none; margin-bottom: 10px; }
            .tabs { display: flex; gap: 20px; padding: 0 15px 10px 15px; border-bottom: 1px solid #1f293d; font-size: 14px; color: #64748b; font-weight: bold; }
            .tab { cursor: pointer; padding-bottom: 5px; }
            .tab.active { color: #00e676; border-bottom: 2px solid #00e676; }
            .chats-list { display: flex; flex-direction: column; }
            .chat-row { display: flex; align-items: center; padding: 14px 15px; border-bottom: 1px solid #1f293d; cursor: pointer; text-align: left; }
            .chat-row:hover { background: #1e293b; }
            .avatar { width: 46px; height: 46px; border-radius: 12px; background: #00e676; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; margin-right: 15px; color: #0b0f17; }
            .chat-info { flex-grow: 1; }
            .chat-name { font-weight: bold; font-size: 15px; margin-bottom: 4px; color: #f8fafc; }
            .chat-last-msg { font-size: 13px; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 240px; }
            .badge { background: #00e676; color: #0b0f17; border-radius: 6px; padding: 2px 8px; font-size: 11px; font-weight: bold; }
            .chat-window { display: flex; flex-direction: column; height: 100vh; background: #0b0f17; }
            .chat-header { background: #121824; padding: 12px 15px; display: flex; align-items: center; border-bottom: 1px solid #1f293d; text-align: left; }
            .notes-list { flex-grow: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; background: #0b0f17; }
            .msg-wrapper { display: flex; width: 100%; }
            .msg-wrapper.center { justify-content: center; }
            .msg-item { padding: 10px 14px; border-radius: 12px; font-size: 14px; max-width: 75%; word-break: break-word; }
            .msg-item.system { background: rgba(30, 41, 59, 0.8); color: #94a3b8; font-size: 11px; border-radius: 8px; border: 1px solid #334155; }
            .msg-item.user { background: #1e293b; border: 1px solid #334155; border-bottom-left-radius: 4px; color: #f8fafc; }
            .input-panel { display: flex; gap: 8px; padding: 12px; background: #12121a; border-top: 1px solid #1f293d; }
            .setting-input { width: 85%; padding: 10px; background: #1e293b; border: 1px solid #334155; border-radius: 8px; color: white; margin-bottom: 12px; font-size: 14px; }
            .btn-green { padding: 10px 20px; background: #00e676; border: none; border-radius: 8px; color: #0b0f17; cursor: pointer; font-weight: bold; width: auto; font-size: 14px; }
            .hidden { display: none; }
            .admin-card { border: 1px dashed #ff5252; background: #241414; padding: 12px; margin: 12px; border-radius: 10px; }
            .admin-btn { background: #ff5252; color: white; width: auto; padding: 8px 16px; font-size: 12px; border-radius: 6px; font-weight: bold; border: none; cursor: pointer; }
        </style>
    </head>
    """.replace("{messages_html}", messages_html).replace("{room_id}", room_id)
@app.route('/get_user_profile', methods=['GET'])
def get_user_profile():
    username = request.args.get('username')
    if username in users_db:
        return jsonify({
            "status": "success",
            "display_name": users_db[username].get('display_name', username),
            "avatar": users_db[username].get('avatar', '🥷')
        })
    return jsonify({"status": "error", "message": "Пользователь не найден"})

@app.route('/search_users', methods=['GET'])
def search_users():
    query = request.args.get('query', '').strip().lower()
    found_users = []
    if query:
        for u_name, u_data in users_db.items():
            if query in u_name.lower() or query in u_data.get('display_name', '').lower():
                found_users.append({
                    "username": u_name,
                    "display_name": u_data.get('display_name', u_name),
                    "avatar": u_data.get('avatar', '🥷')
                })
    return jsonify({"status": "success", "users": found_users})

@app.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.json or {}
    user = data.get('username')
    new_name = data.get('display_name', '').strip()
    new_ava = data.get('avatar', '').strip()
    old_pass = data.get('old_password', '').strip()
    new_pass = data.get('new_password', '').strip()

    if user not in users_db:
        return jsonify({"status": "error", "message": "Ошибка профиля!"})
    if users_db[user]["password"] != old_pass:
        return jsonify({"status": "error", "message": "Неверный старый пароль!"})

    if new_name: users_db[user]["display_name"] = new_name
    if new_ava: users_db[user]["avatar"] = new_ava
    if new_pass: users_db[user]["password"] = new_pass

    return jsonify({"status": "success", "message": "Настройки профиля сохранены!"})

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json or {}
    user = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not user or not password:
        return jsonify({"status": "error", "message": "Пустые данные"})
    if user in users_db:
        if users_db[user]["password"] == password:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Неверный пароль!"})
    else:
        users_db[user] = {"password": password, "display_name": user, "avatar": "🥷"}
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
        disp_name = users_db.get(user, {}).get('display_name', user)
        avatar = users_db.get(user, {}).get('avatar', '🥷')
        rooms_db[room_id].append(f"{avatar} {disp_name}: {message_text}")
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/admin/clear', methods=['POST'])
def admin_clear():
    global rooms_db
    rooms_db = {"main": ["Система: Все чаты были полностью очищены Суперадмином!"]}
    return jsonify({"status": "success"})

# Сюда твой 24-й сотрудник перенёс весь интерфейс в текстовом формате для Flask
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r
# Встраиваем HTML-код интерфейса
HTML_TEMPLATE = """
    <body>
        <div class="container">
            
            <!-- ОКНО ВХОДА -->
            <div id="authScreen" class="card" style="padding: 20px; margin: 20px; border-radius: 12px; background: #17212b; border: 1px solid #101c2b; text-align: center;">
                <h2 style="color: #00e676;">Factor X 🔑</h2>
                <p>Введите имя и пароль для входа</p>
                <input type="text" id="usernameInput" class="setting-input" placeholder="Ваш никнейм..." style="width: 85%;">
                <input type="password" id="passwordInput" class="setting-input" placeholder="Ваш пароль..." style="width: 85%;">
                <button onclick="loginOrRegister()" style="background: #00e676; color: #0b0f17; width: auto; padding: 12px 30px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer;">Войти</button>
                <p id="authError" style="color: #ff5252; font-size: 12px; margin-top: 10px;"></p>
            </div>

            <!-- ЭКРАН 1: СПИСОК ЧАТОВ -->
            <div id="chatsScreen" class="hidden">
                <div class="header">
                    <div class="header-title">
                        <span>Factor X</span>
                        <span id="userBadgeHeader" style="color: #00e676; font-size: 14px;"></span>
                    </div>
                    <input type="text" id="searchBarInput" class="search-bar" placeholder="Поиск по юзернейму..." oninput="filterChatsAndUsers()">
                    <div class="tabs">
                        <div class="tab active" id="tab-all">Все чаты</div>
                        <div class="tab" id="tab-private">Личные</div>
                        <div class="tab" id="tab-new">Новые</div>
                    </div>
                </div>

                <div class="chats-list" id="globalChatsList">
                    <div class="chat-row" id="row-management" onclick="openChat('management')">
                        <div class="avatar" style="background: #00e676;">⚙️</div>
                        <div class="chat-info">
                            <div class="chat-name">Factor X Настройки</div>
                            <div class="chat-last-msg">Управление профилем, паролями и авой</div>
                        </div>
                        <div class="badge" style="background: #00e676;">⚙️</div>
                    </div>

                    <div class="chat-row" id="row-favorites" onclick="openChat('favorites')">
                        <div class="avatar" style="background: #ff9800;">⭐</div>
                        <div class="chat-info">
                            <div class="chat-name">Избранное</div>
                            <div class="chat-last-msg">Ваше личное хранилище заметок</div>
                        </div>
                        <div class="badge">1</div>
                    </div>

                    <div class="chat-row" id="row-main" onclick="openChat('main')">
                        <div class="avatar" style="background: #2f6ea7; color: white;">FX</div>
                        <div class="chat-info">
                            <div class="chat-name">Hooligan's Chat (#main)</div>
                            <div class="chat-last-msg">Общий чат для всех пользователей</div>
                        </div>
                    </div>
                    
                    <div id="searchResultsBlock"></div>
                </div>
            </div>

            <!-- ЭКРАН 2: ОКНО ОТКРЫТОГО ЧАТА -->
            <div id="chatWindowScreen" class="chat-window hidden">
                <div class="chat-header">
                    <button onclick="backToChats()" style="width: auto; background: transparent; border: none; color: #00e676; padding: 5px 10px; margin-right: 10px; font-size: 16px; cursor: pointer;">< Назад</button>
                    <div style="text-align: left; flex-grow: 1;">
                        <div id="currentChatName" style="font-weight: bold; font-size: 16px; color: #f8fafc;">Чат</div>
                        <div style="font-size: 12px; color: #94a3b8;">комната: <span id="currentRoomBadge">#main</span></div>
                    </div>
                </div>

                <div id="adminPanel" class="admin-card hidden">
                    <h3 style="color: #ff5252; margin-top: 0; font-size: 14px;">👑 Панель Создателя</h3>
                    <button onclick="clearAllServerData()" class="admin-btn">💥 Очистить все чаты</button>
                </div>

                <div id="managementOptions" class="hidden" style="padding: 15px; text-align: left; background: #121824; margin: 10px; border-radius: 12px; border: 1px solid #1f293d;">
                    <h3 style="color: #00e676; margin-top: 0; font-size: 16px;">⚙️ Настройки аккаунта</h3>
                    <label style="font-size: 12px; color: #94a3b8;">Имя на экране:</label><br>
                    <input type="text" id="editDisplayName" class="setting-input"><br>
                    <label style="font-size: 12px; color: #94a3b8;">Эмодзи-аватарка:</label><br>
                    <input type="text" id="editAvatar" class="setting-input"><br>
                    <hr style="border: 0; border-top: 1px solid #1f293d; margin: 15px 0;">
                    <h4 style="color: #ff5252; margin: 0 0 10px 0; font-size: 14px;">🔑 Изменить пароль</h4>
                    <input type="password" id="oldPasswordInput" class="setting-input" placeholder="Старый пароль..."><br>
                    <input type="password" id="newPasswordInput" class="setting-input" placeholder="Новый пароль..."><br>
                    <div style="text-align: center; margin-top: 10px; display: flex; gap: 10px; justify-content: center;">
                        <button onclick="updateProfileSettings()" class="btn-green">Сохранить</button>
                        <button onclick="logoutWithPassword()" style="background: #ff5252; color: white;" class="btn-green">Выйти</button>
                    </div>
                    <p id="settingsStatus" style="font-size: 12px; text-align: center; margin-top: 10px; color: #00e676;"></p>
                </div>

                <div class="notes-list" id="notesContainer">
                    {messages_html}
                </div>

                <div class="input-panel" id="inputPanelBlock">
                    <input type="text" id="msgInput" placeholder="Введите сообщение..." style="margin: 0; width: 75%;">
                    <button onclick="sendToServer()" style="width: auto; padding: 12px 18px; background: #00e676; color: #0b0f17; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">🚀</button>
                </div>
            </div>

        </div>
"""
# Финальный блок со скриптами JavaScript, встроенный в HTML-шаблон приложения
INTERFACE_SCRIPTS = """
        <script>
            const savedUser = localStorage.getItem('fx_user');
            if (savedUser) {
                showChatsScreen(savedUser);
            }

            function showChatsScreen(username) {
                document.getElementById('authScreen').classList.add('hidden');
                document.getElementById('chatsScreen').classList.remove('hidden');
                document.getElementById('chatWindowScreen').classList.add('hidden');
                document.getElementById('userBadgeHeader').innerText = "@" + username;
                loadProfileFields(username);
                setupTabs();
            }

            function setupTabs() {
                const tabs = [
                    {el: document.getElementById('tab-all'), view: 'all'},
                    {el: document.getElementById('tab-private'), view: 'private'},
                    {el: document.getElementById('tab-new'), view: 'new'}
                ];
                
                tabs.forEach(tab => {
                    if(!tab.el) return;
                    tab.el.onclick = function() {
                        tabs.forEach(t => t.el.classList.remove('active'));
                        this.classList.add('active');
                        
                        const mng = document.getElementById('row-management');
                        const fav = document.getElementById('row-favorites');
                        const mainChat = document.getElementById('row-main');
                        const searchBlock = document.getElementById('searchResultsBlock');

                        if (tab.view === 'private') {
                            if(mng) mng.style.display = 'none';
                            if(fav) fav.style.display = 'none';
                            if(mainChat) mainChat.style.display = 'none';
                            searchBlock.style.display = 'block';
                        } else if (tab.view === 'new') {
                            if(mng) mng.style.display = 'none';
                            if(fav) fav.style.display = 'none';
                            if(mainChat) mainChat.style.display = 'none';
                            searchBlock.style.display = 'none';
                        } else {
                            if(mng) mng.style.display = 'flex';
                            if(fav) fav.style.display = 'flex';
                            if(mainChat) mainChat.style.display = 'flex';
                            searchBlock.style.display = 'block';
                        }
                    };
                });
            }

            async function loadProfileFields(username) {
                const response = await fetch('/get_user_profile?username=' + encodeURIComponent(username));
                const data = await response.json();
                if (data.status === 'success') {
                    document.getElementById('editDisplayName').value = data.display_name;
                    document.getElementById('editAvatar').value = data.avatar;
                }
            }

            async function filterChatsAndUsers() {
                const query = document.getElementById('searchBarInput').value.trim().toLowerCase();
                const resultsBlock = document.getElementById('searchResultsBlock');
                
                if (!query) {
                    resultsBlock.innerHTML = '';
                    return;
                }

                const response = await fetch('/search_users?query=' + encodeURIComponent(query));
                const data = await response.json();
                resultsBlock.innerHTML = '';
                
                if (data.status === 'success' && data.users.length > 0) {
                    data.users.forEach(user => {
                        const row = document.createElement('div');
                        row.className = 'chat-row';
                        row.onclick = () => window.location.href = '/?room=private-' + user.username;
                        row.innerHTML = `
                            <div class="avatar" style="background: #2f6ea7; color: white;">${user.avatar || '🥷'}</div>
                            <div class="chat-info">
                                <div class="chat-name">${user.display_name}</div>
                                <div class="chat-last-msg">Юзернейм: @${user.username}</div>
                            </div>
                        `;
                        resultsBlock.appendChild(row);
                    });
                }
            }

            function openChat(type) {
                document.getElementById('chatsScreen').classList.add('hidden');
                document.getElementById('chatWindowScreen').classList.remove('hidden');
                
                const chatName = document.getElementById('currentChatName');
                const roomBadge = document.getElementById('currentRoomBadge');
                const inputBlock = document.getElementById('inputPanelBlock');
                const mngOptions = document.getElementById('managementOptions');
                const adminPanel = document.getElementById('adminPanel');
                const currentUser = localStorage.getItem('fx_user');

                inputBlock.classList.remove('hidden');
                mngOptions.classList.add('hidden');
                adminPanel.classList.add('hidden');

                if (type === 'management') {
                    chatName.innerText = "Factor X Настройки";
                    roomBadge.innerText = "system-settings";
                    inputBlock.classList.add('hidden'); 
                    mngOptions.classList.remove('hidden'); 
                    if (currentUser === 'TornadoSOS') adminPanel.classList.remove('hidden');
                } else if (type === 'favorites') {
                    chatName.innerText = "Избранное";
                    roomBadge.innerText = "favorites";
                    const urlParams = new URLSearchParams(window.location.search);
                    if (urlParams.get('room') !== 'favorites') window.location.href = '/?room=favorites';
                } else {
                    chatName.innerText = "Hooligan's Chat";
                    roomBadge.innerText = "main";
                    const urlParams = new URLSearchParams(window.location.search);
                    if (urlParams.get('room') !== 'main' && urlParams.get('room') !== null) window.location.href = '/?room=main';
                }

                const container = document.getElementById('notesContainer');
                container.scrollTop = container.scrollHeight;
            }

            const urlParams = new URLSearchParams(window.location.search);
            const currentRoom = urlParams.get('room') || 'main';
            if (savedUser && (currentRoom === 'favorites' || currentRoom.startsWith('private-') || window.location.search.includes('room'))) {
                showChatsScreen(savedUser);
                if (currentRoom === 'favorites') openChat('favorites');
                else openChat('main');
            }

            function backToChats() {
                const urlParams = new URLSearchParams(window.location.search);
                if (urlParams.get('room') === 'favorites' || urlParams.get('room').startsWith('private-')) {
                    window.location.href = '/'; 
                } else {
                    showChatsScreen(localStorage.getItem('fx_user'));
                }
            }

            async function updateProfileSettings() {
                const currentUser = localStorage.getItem('fx_user');
                const newName = document.getElementById('editDisplayName').value.trim();
                const newAva = document.getElementById('editAvatar').value.trim();
                const oldPass = document.getElementById('oldPasswordInput').value.trim();
                const newPass = document.getElementById('newPasswordInput').value.trim();
                const statusBlock = document.getElementById('settingsStatus');

                if (!oldPass) {
                    statusBlock.style.color = '#ff5252';
                    statusBlock.innerText = "Введите текущий пароль!";
                    return;
                }

                const response = await fetch('/update_profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: currentUser, display_name: newName, avatar: newAva, old_password: oldPass, new_password: newPass
                    })
                });

                const result = await response.json();
                statusBlock.innerText = result.message;
                if (result.status === 'success') {
                    statusBlock.style.color = '#00e676';
                    document.getElementById('oldPasswordInput').value = '';
                    document.getElementById('newPasswordInput').value = '';
                } else {
                    statusBlock.style.color = '#ff5252';
                }
            }

            async function clearAllServerData() {
                if (!confirm("Вы уверены, что хотите сбросить ВСЕ сообщения на сервере?")) return;
                const response = await fetch('/admin/clear', { method: 'POST' });
                const result = await response.json();
                if (result.status === 'success') window.location.href = '/';
            }

            async function logoutWithPassword() {
                const currentUser = localStorage.getItem('fx_user');
                const passwordCheck = prompt("Введите ваш текущий пароль для подтверждения выхода:");
                if (passwordCheck === null) return;

