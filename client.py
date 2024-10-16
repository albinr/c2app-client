import tkinter as tk
import threading
import platform
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from utils.device_info import load_hardware_id, get_geolocation, get_installed_apps
from utils.network import send_heartbeat, check_server, add_device, upload_file, check_device_can_view_info, check_for_commands, request_watchlist_rejoin

TRAY_SUPPORTED = False

if platform.system() in ['Windows', 'Darwin', 'Linux']:
    try:
        from components.tray import create_tray_icon, update_tray_icon
        TRAY_SUPPORTED = True
    except (ImportError, ValueError):
        print("Tray icon not supported on this platform. Continuing without tray icon.")
        TRAY_SUPPORTED = False

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.is_running = True
        self.root.title("C2 Client")
        # self.root.geometry("300x300")
        
        # Load icon images
        icon_img = ImageTk.PhotoImage(file="images/blueeye.ico")
        self.root.iconphoto(False, icon_img)
        self.blue_eye = Image.open("images/blueeye.ico").convert("RGBA")
        self.red_eye = Image.open("images/redeye.ico").convert("RGBA")
        
        # Device information
        self.device_name = platform.node()
        self.os_version = f"{platform.system()} {platform.release()}"
        self.hardware_id = load_hardware_id()
        self.geo_location = get_geolocation()
        self.installed_apps = get_installed_apps()

        # Create tray icon if supported
        if TRAY_SUPPORTED:
            self.tray_icon = create_tray_icon(self.blue_eye, self.restore_window, 
                                            self.display_device_info, self.handle_upload_file, self.quit_app)
        
        # Setup UI components
        self.setup_ui()

        # Network operations
        check_server(self.update_server_status)
        send_heartbeat(self.hardware_id, self.update_device_status)
        add_device(self.device_name, self.os_version, self.hardware_id, self.geo_location, self.installed_apps)
        check_for_commands(self.hardware_id, self.execute_command)

        # Start background terminal input listener
        threading.Thread(target=self.terminal_input_listener, daemon=True).start()

    def setup_ui(self):
        """Setup UI components like status indicators and buttons."""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.grid(column=0, row=0, padx=30, pady=30)

        self.server_status_label = ttk.Label(self.status_frame, text="Server status:")
        self.server_status_label.grid(column=0, row=0)
        self.server_status_indicator = tk.Canvas(self.status_frame, width=20, height=20)
        self.server_status_indicator.grid(column=1, row=0, padx=5)

        self.device_status_label = ttk.Label(self.status_frame, text="Device connection:")
        self.device_status_label.grid(column=0, row=1)
        self.device_status_indicator = tk.Canvas(self.status_frame, width=20, height=20)
        self.device_status_indicator.grid(column=1, row=1, padx=5)

        # Buttons for user actions
        ttk.Button(self.root, text="Run in background", command=self.minimize_in_background).grid(column=0, row=2, columnspan=2, padx=20, pady=10)
        ttk.Button(self.root, text="Upload a file", command=self.handle_upload_file).grid(column=0, row=3, columnspan=2, padx=20, pady=10)
        ttk.Button(self.root, text="Show Device Info", command=self.display_device_info).grid(column=0, row=4, columnspan=2, padx=20, pady=10)
        ttk.Button(self.root, text="Request Rejoin Watchlist", command=self.request_watchlist_rejoin).grid(column=0, row=5, columnspan=2, padx=20, pady=10)
        ttk.Button(self.root, text="Quit", command=self.quit_app).grid(column=0, row=6, columnspan=2, padx=20, pady=10)

    def terminal_input_listener(self):
        """Listen for terminal input to control the app."""
        while True:
            user_input = input("Type 'summon' to restore the window: ")
            if user_input.lower() == "summon":
                self.restore_window()
            elif user_input.lower() == "quit":
                self.quit_app()

    def minimize_in_background(self):
        """Minimize the application window to the background."""
        self.root.withdraw()

    def restore_window(self, icon=None, item=None):
        """Restore the application window from background."""
        self.root.deiconify()

    def quit_app(self, icon=None, item=None):
        """Quit the application."""
        self.is_running = False
        self.restore_window()
        if TRAY_SUPPORTED:
            self.tray_icon.stop()
        self.root.quit()

    def handle_upload_file(self):
        """Handle file upload from file dialog."""
        file_path = filedialog.askopenfilename()
        if file_path:
            upload_file(self.hardware_id, file_path)

    def display_device_info(self):
        """Display all device information if allowed by the server."""
        can_view = check_device_can_view_info(self.hardware_id)
        if can_view:
            info = (
                f"Device Name: {self.device_name}\n"
                f"\nOS Version: {self.os_version}\n"
                f"\nHardware ID: {self.hardware_id}\n"
                f"\nGeolocation: {self.geo_location}\n"
                f"\nInstalled Apps: \n {', '.join(self.installed_apps)}"
            )
            messagebox.showinfo("Device Information", info)
        else:
            messagebox.showwarning("Access Denied", "You are not allowed to view device information.")

    def update_server_status(self, color):
        """Update server status indicator and tray icon if supported."""
        self.server_status_indicator.delete("all")
        self.server_status_indicator.create_oval(5, 5, 20, 20, fill=color)
        if TRAY_SUPPORTED:
            update_tray_icon(self.tray_icon, color, self.blue_eye, self.red_eye)

    def update_device_status(self, color):
        """Update device status indicator."""
        self.device_status_indicator.delete("all")
        self.device_status_indicator.create_oval(5, 5, 20, 20, fill=color)

    def execute_command(self, command):
        """Execute a command and return the result."""
        result = execute_command(command)
        return result

    def request_watchlist_rejoin(self):
        """Send request to rejoin the watchlist."""
        success = request_watchlist_rejoin(self.hardware_id)
        if success:
            messagebox.showinfo("Request Sent", "Request to rejoin the watchlist sent successfully.")
        else:
            messagebox.showerror("Request Failed", "Failed to send request to rejoin the watchlist.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
