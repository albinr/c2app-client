# utils/websocket_client.py

import websockets
import asyncio
import json
import subprocess

async def websocket_listener(websocket_uri, hardware_id):
    try:
        async with websockets.connect(websocket_uri) as websocket:
            await send_client_ready_message(websocket, hardware_id)
            while True:
                try:
                    message = await websocket.recv()
                    await process_message(websocket, message, hardware_id)
                except websockets.ConnectionClosedError:
                    return
                except Exception as e:
                    # print(f"Error receiving message: {e}")
                    return

    except websockets.ConnectionClosedError as e:
        # print(f"WebSocket connection closed: {e}. Reconnecting in 5 seconds...")
        await asyncio.sleep(5)
    except Exception as e:
        # print(f"Error in WebSocket listener: {e}. Reconnecting in 5 seconds...")
        await asyncio.sleep(5)

async def send_client_ready_message(websocket, hardware_id):
    """Send the initial 'Client Ready' message."""
    await websocket.send(json.dumps({
        "type": "command_result",
        "hardware_id": hardware_id,
        "result": "> Client Ready"
    }))

async def process_message(websocket, message, hardware_id):
    """Process a message received from the WebSocket."""
    data = json.loads(message)
    if data.get("type") == "command":
        command = data.get("command")
        result = execute_command(command)
        await websocket.send(json.dumps({
            "type": "command_result",
            "hardware_id": hardware_id,
            "result": result
        }))
    elif data.get("type") == "disconnect":
        # print("Server requested disconnect. Closing connection.")
        return
    else:
        print(f"Unknown message type received: {data}")

def execute_command(command):
    """Execute the received command and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/"
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"