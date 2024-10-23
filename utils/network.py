# utils/network.py

import requests
import time
import threading
from tkinter import messagebox

SERVER_URL = 'http://localhost:5000'

def add_device(device_name, os_version, hardware_id, geo_location, installed_apps):
    """Register device with the server."""
    try:
        data = {
            'device_name': device_name,
            'os_version': os_version,
            'hardware_id': hardware_id,
            'geo_location': geo_location,
            'installed_apps': installed_apps
        }
        response = requests.post(f"{SERVER_URL}/device", json=data)

        if response.status_code == 201:
            # print("Device added!")
            pass

        elif response.status_code == 400 and 'already exists' in response.text:
            # print("Device already exists.")
            pass

        else:
            raise Exception(f"Failed to add device: {response.text}")

    except Exception as e:
        # print(f"Could not connect to the server: {e}")
        pass

def send_heartbeat(hardware_id, update_device_status_callback, show_rejoin_button_callback, 
    hide_rejoin_button_callback, start_websocket_listener_callback, stop_websocket_listener_callback):
    """Send heartbeat to the server at regular intervals and stop if device is off the watchlist."""
    def background_heartbeat():
        while True:
            try:
                response = requests.post(f"{SERVER_URL}/device/heartbeat", json={"hardware_id": hardware_id})
                if response.status_code == 200:
                    result = response.json()
                    # print(result)
                    on_watchlist = result.get('on_watchlist', True)
                    open_socket = result.get('open_socket', False)

                    if on_watchlist:
                        # print("Heartbeat sent")
                        update_device_status_callback("green")
                        hide_rejoin_button_callback()

                        if open_socket:
                            start_websocket_listener_callback()
                        else:
                            stop_websocket_listener_callback()

                    else:
                        # print("Device is off the watchlist.")
                        update_device_status_callback("red")
                        show_rejoin_button_callback()
                        stop_websocket_listener_callback()

                else:
                    # print("Heartbeat denied")
                    update_device_status_callback("red")
                    show_rejoin_button_callback()
                    stop_websocket_listener_callback()

            except Exception as e:
                # print(f"Error sending heartbeat: {e}")
                update_device_status_callback("red")
                stop_websocket_listener_callback()

            time.sleep(10)

    threading.Thread(target=background_heartbeat, daemon=True).start()

def check_server(update_server_status_callback):
    """Periodically check server status."""
    def background_check():
        while True:
            try:
                response = requests.get(f"{SERVER_URL}/ping")
                # print("Server pinged")
                if response.status_code == 200:
                    update_server_status_callback("green")

                else:
                    update_server_status_callback("red")

            except Exception as e:
                # print(f"Failed to ping server: {e}")
                update_server_status_callback("red")

            time.sleep(20)

    threading.Thread(target=background_check, daemon=True).start()

def upload_file(hardware_id, file_path):
    """Upload a file to the server."""
    if file_path:
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                data = {'hardware_id': hardware_id}
                response = requests.post(f"{SERVER_URL}/upload", files=files, data=data)

                if response.status_code == 200:
                    messagebox.showinfo("Success", "File uploaded successfully!")

                else:
                    messagebox.showerror("Error", f"Failed to upload file: {response.text}")

        except Exception as e:
            messagebox.showerror("Error", f"Error uploading file: {e}")

def check_device_can_view_info(hardware_id):
        """Check with the server if the device can view its own information."""
        try:
            response = requests.post(f"{SERVER_URL}/device/can_view", json={"hardware_id": hardware_id})
            if response.status_code == 200:
                result = response.json()
                return result.get('can_view', False)
            else:
                # print(f"Error: Received status code {response.status_code}")
                # print(f"Response content: {response.text}")
                messagebox.showerror("Error", f"Failed to check permission with the server. Status code: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            # print(f"Error details: {e}")
            messagebox.showerror("Error", f"Error connecting to the server: {e}")
            return False

def request_watchlist_rejoin(hardware_id):
    """Send a request to rejoin the watchlist."""
    try:
        response = requests.post(f"{SERVER_URL}/device/rejoin", json={"hardware_id": hardware_id})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Request to rejoin the watchlist sent successfully.")
            return True
        elif response.status_code == 400:
            messagebox.showwarning("Warning", "Device is already on the watchlist or the request is pending.")
            return False
        else:
            messagebox.showerror("Error", f"Failed to submit request. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error connecting to the server: {e}")
        return False

