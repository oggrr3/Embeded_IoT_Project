# server.py

import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Cho phép CORS để website có thể truy cập API

# Biến lưu trữ dữ liệu
latest_data = {'temperature': None, 'humidity': None}

# Route cho trang chủ
@app.route('/')
def index():
    return render_template('index.html')

# API nhận dữ liệu từ gateway_BLE.py
@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    if data:
        latest_data['temperature'] = data.get('temperature')
        latest_data['humidity'] = data.get('humidity')
        print(f"📥 Nhận dữ liệu từ client: {latest_data}")
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'no data received'}), 400

@app.route('/api/data', methods=['GET'])
def send_data():
    return jsonify(latest_data), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

