# server_BLE.py

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Biến lưu trữ dữ liệu mới nhất
latest_data = {'temperature': None, 'humidity': None}

# Danh sách lưu trữ lịch sử dữ liệu
history_data = []

# Route cho trang chủ
@app.route('/')
def index():
    return render_template('index.html')

# API nhận dữ liệu từ gateway_BLE.py
@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    if data:
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        latest_data['temperature'] = temperature
        latest_data['humidity'] = humidity
        latest_data['timestamp'] = timestamp

        # Thêm dữ liệu vào lịch sử
        history_data.append({
            'temperature': temperature,
            'humidity': humidity,
            'timestamp': timestamp
        })

        # Giới hạn kích thước lịch sử (tùy chọn, ví dụ: 50 bản ghi)
        if len(history_data) > 50:
            history_data.pop(0)

        print(f"📥 Nhận dữ liệu từ client: {latest_data}")
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'no data received'}), 400

# API trả về dữ liệu mới nhất cho trang web
@app.route('/api/data', methods=['GET'])
def send_data():
    return jsonify(latest_data), 200

# API trả về lịch sử dữ liệu cho biểu đồ
@app.route('/api/history', methods=['GET'])
def send_history():
    return jsonify(history_data), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
