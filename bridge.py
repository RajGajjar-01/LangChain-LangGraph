import serial
import asyncio
import websockets
import json

SERIAL_PORT = '/dev/ttyUSB1'
BAUD_RATE   = 115200
WS_PORT     = 8765

latest  = {"pitch": 0, "roll": 0, "yaw": 0}
clients = set()

async def broadcast():
    global latest
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Reading from {SERIAL_PORT}")

    while True:
        try:
            raw = ser.readline()
            if not raw:
                await asyncio.sleep(0.01)
                continue

            line = raw.decode('utf-8', errors='ignore').strip()

            if not line.startswith('{'):
                await asyncio.sleep(0.01)
                continue

            data = json.loads(line)

            # validate all keys exist
            if not all(k in data for k in ('pitch', 'roll', 'yaw')):
                await asyncio.sleep(0.01)
                continue

            latest = data
            print(f"pitch={data['pitch']:.1f}  roll={data['roll']:.1f}  yaw={data['yaw']:.1f}")

            if clients:
                msg = json.dumps(data)
                dead = set()
                for c in clients:
                    try:
                        await c.send(msg)
                    except Exception:
                        dead.add(c)
                clients -= dead

        except json.JSONDecodeError:
            pass   # skip malformed lines silently
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(0.1)

        await asyncio.sleep(0)

async def handler(websocket):
    clients.add(websocket)
    print(f"Browser connected — {len(clients)} client(s)")
    try:
        await websocket.send(json.dumps(latest))
        await websocket.wait_closed()
    finally:
        clients.discard(websocket)
        print(f"Browser disconnected — {len(clients)} client(s)")

async def main():
    print(f"WebSocket server starting on ws://localhost:{WS_PORT}")
    async with websockets.serve(handler, "localhost", WS_PORT):
        await broadcast()

asyncio.run(main())