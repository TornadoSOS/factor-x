import os
from flask import Flask, request, jsonify, render_template
import vercel_kv

app = Flask(__name__)

# Подключаемся к базе данных Vercel KV
try:
    kv = vercel_kv.KV()
except Exception as e:
    kv = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_messages', methods=['GET'])
def get_messages():
    """Загружаем сообщения из вечной базы данных"""
    if kv:
        messages = kv.lrange('factorx_chat', 0, -1) or []
        messages = [m.decode('utf-8') if isinstance(m, bytes) else m for m in messages]
        return jsonify(messages)
    return jsonify(["База данных еще не подключена"])

@app.route('/send_message', methods=['POST'])
def send_message():
    """Сохраняем новое сообщение навсегда"""
    data = request.json
    message_text = data.get('message', '').strip()
    user_id = data.get('user_id', 'Аноним')
    
    if message_text and kv:
        formatted_message = f"{user_id}: {message_text}"
        kv.rpush('factorx_chat', formatted_message)
        return jsonify({"status": "success"})
        
    return jsonify({"status": "error"})

if __name__ == '__main__':
    app.run(debug=True)
