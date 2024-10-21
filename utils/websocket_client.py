# utils/websocket_client.py

import websockets
import asyncio
import json
import subprocess

async def connect_websocket(hardware_id):
    websocket_url = f"ws://localhost:5000/ws/device/{hardware_id}"
    async with websockets.connect(websocket_url) as websocket:
        print(f"Connected to WebSocket as {hardware_id}.")
        try:
            while True:
                # Wait for a message from the server
                message = await websocket.recv()
                try:
                    data = json.loads(message)
                    if data.get("type") == "command":
                        command = data.get("command")
                        print(f"Executing command: {command}")
                        # Execute the command
                        result = execute_command(command)
                        # Send the result back to the server
                        response = {
                            "type": "command_result",
                            "result": result
                        }
                        await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    print("Invalid message format received")
        except websockets.ConnectionClosedError as e:
            print(f"WebSocket connection closed: {e}")
        except Exception as e:
            print(f"WebSocket error: {e}")

def execute_command(command):
    """Execute a system command and return the output or error."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"

# Example usage:
if __name__ == "__main__":
    hardware_id = "your_hardware_id_here"  # Replace with actual hardware ID
    asyncio.run(connect_websocket(hardware_id))
