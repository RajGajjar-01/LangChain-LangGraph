import subprocess
import json
import threading
import time
import os

class LSPClient: 
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.req_id = 0
        self.pending = {}
        self.lock = threading.Lock()
        self._start_server()
        self._initialize()

    def _start_server(self):
        self.process = subprocess.Popen(
            ["pylsp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()

    def _read_loop(self):
        while True:
            headers = {}
            while True:
                line = self.process.stdout.readline().decode("utf-8").strip()
                if not line:
                    break

                key, _, value = line.partition(": ")
                headers[key] = value
            
            if "Content-Length" not in headers:
                continue

            length = int(headers["Content-Length"])
            body = self.process.stdout.read(length).decode("utf-8")
            message = json.loads(body)
        
            if "id" in message:
                with self.lock:
                    self.pendind[message["id"]] = message
    
    def _send_request(self, method: str, params: dict) -> dict:
        self.req_id += 1
        request_id = self.req_id

        message = {
            "jsonprc" : "2.0",
            "id" : request_id,
            "method" : method,
            "params": params
        }

        body = json.dumps(message).encode("utf-8")

        header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
        self.process.stdin.write(header + body)
        self.process.stdin.flush()

        for _ in range(50):
            with self.lock:
                if request_id in self.pending:
                    return self.pending.pop(request_id)
            
            time.sleep(0.1)

        return {}
    
    def _send_notification(self, method: str, params: dict):
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }

        body = json.dumps(message).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
        self.process.stdin.write(header + body)
        self.process.stdin.flush()

    def _initialize(self):
        
    

