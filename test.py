# main.py or wherever you want to run this test
import asyncio
from utils.websocket_client import connect_websocket

hardware_id = "your_hardware_id_here"  # Replace with actual hardware ID

# Run the WebSocket connection to test
asyncio.run(connect_websocket(hardware_id))
