import http.server
import socketserver
import psutil
import json
import os

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 將靜態HTML、CSS、JS文件的請求轉向到它們所在的目錄
        if self.path == '/' or self.path.endswith('.html') or self.path.endswith('.css') or self.path.endswith('.js'):
            if self.path == '/':
                self.path = '/dashboard.html'  # 設置預設頁面
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        # 下面是API端點
        elif self.path == '/cpu':
            self.handle_cpu_info()
        elif self.path == '/memory':
            self.handle_memory_info()
        elif self.path == '/disk':
            self.handle_disk_info()
        elif self.path == '/network':
            self.handle_network_info()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Resource not found")

    def handle_cpu_info(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        self.send_json({'CPU Usage': f'{cpu_usage}%'})

    def handle_memory_info(self):
        memory = psutil.virtual_memory()
        memory_info = {
            'Total': memory.total,
            'Used': memory.used,
            'Free': memory.free,
            'Percentage': memory.percent
        }
        self.send_json(memory_info)

    def handle_disk_info(self):
        disk = psutil.disk_usage('/')
        disk_info = {
            'Total': disk.total,
            'Used': disk.used,
            'Free': disk.free,
            'Percentage': disk.percent
        }
        self.send_json(disk_info)

    def handle_network_info(self):
        network = psutil.net_io_counters(pernic=True)
        network_info = {nic: {
            'Bytes Sent': stats.bytes_sent,
            'Bytes Received': stats.bytes_recv
        } for nic, stats in network.items()}
        self.send_json(network_info)

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

# 設置HTTP服務器與處理器
with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
