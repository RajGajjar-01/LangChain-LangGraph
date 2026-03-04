import subprocess
import json
import threading
import time
import os

class LSPClient: 
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.req_id = 0
        self.doc_version = 1
        self.pending = {}
        self.diagnostics = {}
        self.lock = threading.Lock()
        self._start_server()
        self._initialize()

    def _start_server(self):
        # Prefer the venv's pylsp if it exists
        venv_pylsp = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".venv", "bin", "pylsp")
        command = [venv_pylsp] if os.path.exists(venv_pylsp) else ["pylsp"]
        
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()
        
        self._stderr_thread = threading.Thread(target=self._stderr_loop, daemon=True)
        self._stderr_thread.start()

    def _stderr_loop(self):
        while True:
            line = self.process.stderr.readline()
            if not line:
                break
            # You can log this to a file if needed
            # with open("lsp_stderr.log", "a") as f:
            #     f.write(line.decode("utf-8"))
            pass


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
                    self.pending[message["id"]] = message
            elif "method" in message:
                if message["method"] == "textDocument/publishDiagnostics":
                    params = message.get("params", {})
                    uri = params.get("uri")
                    diagnostics = params.get("diagnostics", [])
                    with self.lock:
                        self.diagnostics[uri] = diagnostics
    
    def _send_request(self, method: str, params: dict) -> dict:
        self.req_id += 1
        request_id = self.req_id

        message = {
            "jsonrpc" : "2.0",
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
        self._send_request("initialize", {
            "processId": os.getpid(),
            "rootUri": f"file://{os.path.dirname(os.path.abspath(self.file_path))}",
            "capabilities": {
                "textDocument": {
                    "synchronization": {"didSave": True},
                    "hover": {"contentFormat": ["markdown", "plaintext"]},
                    "definition": {"dynamicRegistration": True},
                    "diagnostic": {"dynamicRegistration": True},
                    "publishDiagnostics": {"relatedInformation": True},
                    "completion": {"completionItem": {"snippetSupport": True}}
                },
                "workspace": {
                    "configuration": True,
                    "didChangeConfiguration": {"dynamicRegistration": True}
                }
            }, 
        })

        self._send_notification("initialized", {})

        # Send configuration to enable plugins
        self._send_notification("workspace/didChangeConfiguration", {
            "settings": {
                "pylsp": {
                    "plugins": {
                        "pyflakes": {"enabled": True},
                        "pycodestyle": {"enabled": True},
                        "pylint": {"enabled": True},
                        "mccabe": {"enabled": True}
                    }
                }
            }
        })

        with open(self.file_path, "r") as f:
            text = f.read()

        self._send_notification("textDocument/didOpen", {
            "textDocument": {
                "uri": f"file://{os.path.abspath(self.file_path)}",
                "languageId": "python",
                "version": 1,
                "text": text,
            }
        })

        time.sleep(2)

    def get_diagnostics(self) -> list:
        # Pylsp usually pushes diagnostics after didOpen or didChange
        # We trigger a change to ensure fresh diagnostics
        with open(self.file_path, "r") as f:
            text = f.read()

        self.doc_version += 1
        self._send_notification("textDocument/didChange", {
            "textDocument": {
                "uri": f"file://{os.path.abspath(self.file_path)}",
                "version": self.doc_version,
            },
            "contentChanges": [{"text": text}],
        })

        # Wait a bit for the server to process and send publishDiagnostics
        time.sleep(1)

        # Also try the pull-based request if supported
        uri = f"file://{os.path.abspath(self.file_path)}"
        response = self._send_request("textDocument/diagnostic", {
            "textDocument": {"uri": uri}
        })

        if response and "result" in response:
            result = response["result"]
            if isinstance(result, dict) and "items" in result:
                return result["items"]

        # Fallback to push-based diagnostics
        with self.lock:
            return self.diagnostics.get(uri, [])
    
    def hover(self, line: int, character: int) -> str:
        response = self._send_request("textDocument/hover", {
            "textDocument": {
                "uri": f"file://{os.path.abspath(self.file_path)}"
            },
            "position": {
                "line": line - 1,        # LSP is 0-indexed, humans are 1-indexed
                "character": character
            }
        })
        result = response.get("result")
        if result and result.get("contents"):
            contents = result["contents"]
            if isinstance(contents, dict):
                return contents.get("value", "")
            return str(contents)
        return "No hover info found."
    
    def get_completions(self, line: int, character: int) -> list:

        response = self._send_request("textDocument/completion", {
            "textDocument": {
                "uri": f"file://{os.path.abspath(self.file_path)}"
            },
            "position": {
                "line": line - 1,
                "character": character
            }
        })
        result = response.get("result", {})
        if isinstance(result, dict):
            items = result.get("items", [])
        else:
            items = result or []


        return [item.get("label", "") for item in items[:10]]  # top 10

    def go_to_definition(self, line: int, character: int) -> dict:
        response = self._send_request("textDocument/definition", {
            "textDocument": {
                "uri": f"file://{os.path.abspath(self.file_path)}"
            },
            "position": {
                "line": line - 1,
                "character": character
            }
        })
        result = response.get("result")
        if result:
            if isinstance(result, list) and len(result) > 0:
                loc = result[0]
                return {
                    "line": loc["range"]["start"]["line"] + 1,
                    "file": loc["uri"].replace("file://", "")
                }
        return {}

    def shutdown(self):
        self._send_request("shutdown", {})
        self._send_notification("exit", {})
        self.process.terminate()
    

