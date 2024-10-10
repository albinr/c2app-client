# utils/device_info.py

import platform
import uuid
import os
import subprocess
import requests

def get_device_id():
    """Generate a unique device ID."""
    return str(uuid.uuid1())

def load_hardware_id():
    """Load or generate hardware ID."""
    hardware_id_file = 'hardware_id.txt'
    if os.path.exists(hardware_id_file):
        with open(hardware_id_file, 'r') as file:
            return file.read().strip()
    else:
        new_hardware_id = get_device_id()
        with open(hardware_id_file, 'w') as file:
            file.write(new_hardware_id)
        return new_hardware_id

def get_installed_apps():
    """Retrieve the list of installed applications based on the OS."""
    if platform.system() == 'Windows':
        try:
            result = subprocess.run(['wmic', 'product', 'get', 'name'], stdout=subprocess.PIPE, check=True)
            installed_apps = result.stdout.decode('utf-8').split('\n')
            return [app.strip() for app in installed_apps if app.strip()]
        except subprocess.CalledProcessError as e:
            return [f"Error getting apps from Windows: {e}"]
        except Exception as e:
            return [f"Unexpected error on Windows: {e}"]
    elif platform.system() == 'Linux':
        try:
            result = subprocess.run(['dpkg', '--get-selections'], stdout=subprocess.PIPE, check=True)
            installed_apps = result.stdout.decode('utf-8').split('\n')
            installed_apps = [app.split()[0] for app in installed_apps if "install" in app]
            return installed_apps[:10]
        except subprocess.CalledProcessError as e:
            return [f"Error getting apps from Linux: {e}"]
        except Exception as e:
            return [f"Unexpected error on Linux: {e}"]
    else:
        return ["Installed apps retrieval is not supported on this OS."]

def get_geolocation():
    """Fetch geolocation based on IP."""
    try:
        response = requests.get('https://ipinfo.io')
        location_data = response.json()
        return location_data['loc']
    except Exception as e:
        return f"Error retrieving location: {e}"
