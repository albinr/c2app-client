import tkinter as tk

def update_server_status(server_status_indicator, color):
    """
    Updates the server status indicator on the UI.
    
    Args:
        server_status_indicator (tk.Canvas): The canvas widget for displaying the server status.
        color (str): The color to fill the indicator (e.g., 'green' for connected, 'red' for disconnected).
    """
    server_status_indicator.delete("all")
    server_status_indicator.create_oval(5, 5, 20, 20, fill=color)


def update_device_status(device_status_indicator, color):
    """
    Updates the device status indicator on the UI.
    
    Args:
        device_status_indicator (tk.Canvas): The canvas widget for displaying the device status.
        color (str): The color to fill the indicator (e.g., 'green' for connected, 'red' for disconnected).
    """
    device_status_indicator.delete("all")
    device_status_indicator.create_oval(5, 5, 20, 20, fill=color)
