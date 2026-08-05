import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Наша база данных комнат прямо в коде
rooms_db = {
    "main": ["Система: Добро пожаловать в общий чат!"]
}

def clean_room_name(name):
    if not name:
        return "main"
    return str(name).strip().lower()

@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.json or {}
    room_id = clean_room_name(data.get('room', 'main'))
    sender = data.get('sender', 'Аноним')
    text = data.get('text', '')
    
    if room_id not in rooms_db:
        rooms_db[room_id] = []
        
    rooms_db[room_id].append(f"{sender}: {text}")
    return jsonify({"status": "success", "messages": rooms_db[room_id]}), 200

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

    # ТВОЙ РАБОЧИЙ HTML-КОД И ДИЗАЙН ИЗ ACODE
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Factor X // Core</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        body {{ background-color: #020617; color: #f8fafc; padding: 20px; }}
        .chat-container {{ max-width: 600px; margin: 0 auto; background: #0b1329; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
        .logo-text {{ font-size: 24px; font-weight: bold; color: #38bdf8; text-align: center; margin-bottom: 5px; }}
        .system-badge {{ text-align: center; font-size: 12px; color: #10b981; margin-bottom: 20px; }}
        .messages-space {{ height: 350px; overflow-y: auto; background: #0f172a; border-radius: 8px; padding: 15px; margin-bottom: 15px; border: 1px solid #1e293b; }}
        .msg-wrapper {{ margin-bottom: 10px; display: flex; }}
        .msg-wrapper.center {{ justify-content: center; }}
        .msg-item {{ padding: 8px 14px; border-radius: 8px; max-width: 80%; font-size: 15px; }}
        .msg-item.system {{ background: #1e293b; color: #94a3b8; font-size: 13px; text-align: center; }}
        .msg-item.user {{ background: #1e40af; color: #ffffff; }}
        
        input {{ flex: 1; padding: 12px; border-radius: 6px; border: 1px solid #1e293b; background: #0f172a; color: white; font-size: 15px; }}
        button {{ padding: 12px 20px; border-radius: 6px; border: none; background: #38bdf8; color: #020617; font-weight: bold; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="logo-text">FACTOR X</div>
        <div class="system-badge">v1.0 // ACTIVE</div>
        
        <div class="messages-space" id="chatBox">
            {messages_html}
        </div>
        
                <div class="input-area" style="display: flex; gap: 8px; align-items: center;">
            <label for="fileInput" style="padding: 12px; background: #1e293b; border-radius: 6px; cursor: pointer; color: #38bdf8; font-weight: bold; font-size: 18px; display: flex; align-items: center; justify-content: center;">+</label>
            <input type="file" id="fileInput" accept="image/*" style="display: none;">
            <input type="text" id="messageInput" placeholder="Введите сообщение..." style="flex: 1;">
            <button onclick="sendMessage()">СЕНД</button>
        </div>

    

    <script>
        const chatBox = document.getElementById('chatBox');
        const messageInput = document.getElementById('messageInput');
        const urlParams = new URLSearchParams(window.location.search);
        const currentRoom = urlParams.get('room') || 'main';

                async function sendMessage() {
            const text = messageInput.value.trim();
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!text && !file) return;

            let fileData = null;
            let fileName = null;

            if (file) {
                fileName = file.name;
                fileData = await new Promise((resolve) => {
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(reader.result);
                    reader.readAsDataURL(file);
                });
            }

            try {
                let response = await fetch('/api/send_message', {
                    method: 'POST',
                    headers: { 'Content-Type':  body: JSON.stringify({
                        room: currentRoom,
                        sender: 'TornadoSOS',
                        text: text,
                        file_data: fileData,
                        file_name: fileName
                    })
                });
                if (response.ok) {
                    messageInput.value = '';
                    fileInput.value = ''; // Очищаем выбранный файл
                    window.location.reload();
                }}
            } catch (err) { console.error(err); }
        }

    </script>
</body>
</html>"""

if __name__ == '__main__':
    app.run(debug=True)
