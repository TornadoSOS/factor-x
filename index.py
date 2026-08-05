import os
from flask import Flask, request, jsonify, render_template
import database
import messages

app = Flask(__name__)

def clean_room_name(name):
    if not name:
        return "main"
    return str(name).strip().lower()

@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.json
    if not data:
        return jsonify({"status": "error"}), 400
    r_id = clean_room_name(data.get('room', 'main'))
    snd = data.get('sender', 'Аноним')
    txt = data.get('text', '')
    res, status = messages.add_new_message(r_id, snd, txt)
    return jsonify(res), status

@app.route('/')
def home():
    r_name = request.args.get('room', 'main')
    room_id = clean_room_name(r_name)
    
    if room_id not in database.rooms_db:
        sys_msg = f"Система: Создана комната #{room_id}"
        database.rooms_db[room_id] = [{"sender": "Система", "text": sys_msg}]
        
    messages_html = messages.generate_messages_html(room_id)
    return render_template('index.html', messages_html=messages_html, room_id=room_id)

if __name__ == '__main__':
    app.run(debug=True)
