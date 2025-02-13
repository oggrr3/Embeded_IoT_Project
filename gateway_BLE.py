
import asyncio
from bleak import BleakScanner, BleakClient
import sys
import os
import requests  # Thêm import requests

# Đảm bảo hỗ trợ UTF-8 cho Windows
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình
HM10_NAME = "HMSoft"  # Thay thế bằng tên HM-10 của bạn nếu cần
SERVER_URL = "https://ble-api-iot.onrender.com/api/data"  # Đảm bảo URL đúng
RETRY_INTERVAL = 5

# Biến bộ đệm để ghép nối dữ liệu
buffer = ""

# Tìm thiết bị HM-10
async def find_hm10_device():
    print("🔍 Đang tìm kiếm thiết bị HM-10...")
    devices = await BleakScanner.discover()
    for device in devices:
        if device.name and HM10_NAME in device.name:
            print(f"✅ Đã tìm thấy HM-10: {device.name} (Địa chỉ: {device.address})")
            return device.address
    print("❌ Không tìm thấy thiết bị HM-10!")
    return None

# Kết nối và đọc dữ liệu từ HM-10
async def connect_and_read(address):
    try:
        async with BleakClient(address) as client:
            print(f"✅ Kết nối với {address} thành công!")

            # UUID của HM-10
            CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

            # Bắt đầu nhận thông báo
            def notification_handler(sender, data):
                global buffer
                decoded_data = data.decode("utf-8")
                buffer += decoded_data
                # Kiểm tra xem có ký tự kết thúc thông điệp không (giả sử là '\n')
                if '\n' in buffer:
                    messages = buffer.split('\n')
                    for message in messages[:-1]:
                        print(f"📥 Nhận dữ liệu: {message}")
                        # Xử lý và gửi dữ liệu
                        asyncio.create_task(process_and_send_data(message))
                    buffer = messages[-1]  # Giữ lại phần dữ liệu chưa hoàn chỉnh

            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
            print("📡 Đã bắt đầu nhận thông báo từ HM-10...")
            # Giữ cho chương trình chạy
            while True:
                await asyncio.sleep(1)

    except Exception as e:
        print(f"🔥 Lỗi kết nối hoặc đọc dữ liệu: {e}")
        await asyncio.sleep(RETRY_INTERVAL)

# Xử lý và gửi dữ liệu
async def process_and_send_data(data):
    try:
        print(f"✅ Dữ liệu hoàn chỉnh nhận được: {data}")
        # Phân tích dữ liệu
        data_parts = data.split(", ")
        temp = data_parts[0].split(": ")[1].replace('C', '')
        humidity = data_parts[1].split(": ")[1].replace('%', '')
        payload = {
            'temperature': float(temp),
            'humidity': float(humidity)
        }
        print(payload)
        send_to_server(payload)
    except Exception as e:
        print(f"🔥 Lỗi xử lý dữ liệu: {e}")

# Gửi dữ liệu lên server
def send_to_server(data):
    try:
        response = requests.post(SERVER_URL, json=data)
        if response.status_code == 200:
            print("📤 Đã gửi dữ liệu lên server thành công!")
        else:
            print(f"❌ Lỗi gửi dữ liệu: HTTP {response.status_code}")
    except Exception as e:
        print(f"🌐 Lỗi kết nối server: {e}")

# Hàm chính
async def main():
    address = await find_hm10_device()
    if address:
        await connect_and_read(address)
    else:
        print("🔴 Không tìm thấy địa chỉ thiết bị. Dừng chương trình.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Dừng chương trình...")
