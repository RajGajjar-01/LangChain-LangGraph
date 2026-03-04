from lsp_client import LSPClient
import os
import time

def test():
    file_path = os.path.abspath("sample_code.py")
    print(f"Testing LSP for {file_path}")
    client = LSPClient(file_path)
    
    print("Waiting for diagnostics...")
    time.sleep(3)
    
    diagnostics = client.get_diagnostics()
    print(f"Found {len(diagnostics)} diagnostics:")
    for d in diagnostics:
        print(f" - {d}")
    
    client.shutdown()

if __name__ == "__main__":
    test()
