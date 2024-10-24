import unittest
from unittest.mock import patch, MagicMock
from utils.network import add_device, send_heartbeat, check_server, upload_file, check_device_can_view_info, request_watchlist_rejoin
import time

SERVER_URL = 'http://localhost:5000'

class TestNetwork(unittest.TestCase):

    @patch('utils.network.requests.post')
    def test_add_device_success(self, mock_post):
        mock_post.return_value.status_code = 201
        mock_post.return_value.text = "Device added!"
        add_device("Test Device", "OS", "12345", "Geo", ["App1", "App2"])
        mock_post.assert_called_once_with(f"{SERVER_URL}/device", json={
            'device_name': "Test Device",
            'os_version': "OS",
            'hardware_id': "12345",
            'geo_location': "Geo",
            'installed_apps': ["App1", "App2"]
        })

    @patch('utils.network.requests.post')
    def test_add_device_already_exists(self, mock_post):
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Device already exists."
        add_device("Test Device", "OS", "12345", "Geo", ["App1", "App2"])
        mock_post.assert_called_once()

    @patch('utils.network.requests.get')
    def test_check_server_success(self, mock_get):
        mock_get.return_value.status_code = 200
        update_server_status_callback = MagicMock()
        check_server(update_server_status_callback)
        
        time.sleep(0.1)

        mock_get.assert_called_once_with(f"{SERVER_URL}/ping")
        update_server_status_callback.assert_called_with("green")

    @patch('utils.network.requests.get')
    def test_check_server_failure(self, mock_get):
        mock_get.side_effect = Exception("Connection error")
        update_server_status_callback = MagicMock()
        check_server(update_server_status_callback)
        
        time.sleep(0.1)

        update_server_status_callback.assert_called_with("red")

    @patch('utils.network.requests.post')
    @patch('builtins.open', new_callable=MagicMock)
    def test_upload_file_success(self, mock_open, mock_post):
        mock_open.return_value.__enter__.return_value = MagicMock()
        mock_post.return_value.status_code = 200
        upload_file("12345", "path/to/file")
        mock_post.assert_called_once()

    @patch('utils.network.requests.post')
    def test_check_device_can_view_info(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'can_view': True}
        result = check_device_can_view_info("12345")
        self.assertTrue(result)
        mock_post.assert_called_once_with(f"{SERVER_URL}/device/can_view", json={"hardware_id": "12345"})

    @patch('utils.network.requests.post')
    def test_request_watchlist_rejoin_success(self, mock_post):
        mock_post.return_value.status_code = 200
        result = request_watchlist_rejoin("12345")
        self.assertTrue(result)
        mock_post.assert_called_once_with(f"{SERVER_URL}/device/rejoin", json={"hardware_id": "12345"})

    @patch('utils.network.requests.post')
    def test_request_watchlist_rejoin_already_on_watchlist(self, mock_post):
        mock_post.return_value.status_code = 400
        result = request_watchlist_rejoin("12345")
        self.assertFalse(result)
        mock_post.assert_called_once_with(f"{SERVER_URL}/device/rejoin", json={"hardware_id": "12345"})

    @patch('utils.network.requests.post')
    def test_send_heartbeat(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'on_watchlist': True,
            'open_socket': False
        }
        # Mocking the callbacks
        update_device_status_callback = MagicMock()
        show_rejoin_button_callback = MagicMock()
        hide_rejoin_button_callback = MagicMock()
        start_websocket_listener_callback = MagicMock()
        stop_websocket_listener_callback = MagicMock()

        send_heartbeat(
            "12345",
            update_device_status_callback,
            show_rejoin_button_callback,
            hide_rejoin_button_callback,
            start_websocket_listener_callback,
            stop_websocket_listener_callback
        )
        
        mock_post.assert_called_with(f"{SERVER_URL}/device/heartbeat", json={"hardware_id": "12345"})
        update_device_status_callback.assert_called_with("green")
        hide_rejoin_button_callback.assert_called_once()
        stop_websocket_listener_callback.assert_called_once()

if __name__ == '__main__':
    unittest.main()
