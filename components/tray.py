# components/tray.py

import pystray
from pystray import MenuItem as item

def create_tray_icon(blue_eye, restore_window, display_device_info, upload_file, quit_app):
    """Create a tray icon with context menu."""
    tray_icon = pystray.Icon("C2 Client", blue_eye, "C2 Client", menu=pystray.Menu(
        item('Open', restore_window),
        item('Show info', display_device_info),
        item('Upload file', upload_file),
        item('Quit', quit_app)
    ))
    tray_icon.run_detached()
    return tray_icon

def update_tray_icon(tray_icon, status, blue_eye, red_eye):
    """Update the tray icon based on status."""
    if status == "green":
        tray_icon.icon = blue_eye
    else:
        tray_icon.icon = red_eye
    tray_icon.update()
