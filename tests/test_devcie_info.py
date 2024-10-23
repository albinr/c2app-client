import unittest
from unittest.mock import patch, mock_open, MagicMock
import subprocess  # Import subprocess here
from utils.device_info import load_hardware_id, get_installed_apps, get_geolocation, get_device_id
import platform

class TestDeviceInfo(unittest.TestCase):

    @patch('utils.device_info.uuid.uuid1')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_load_hardware_id_existing(self, mock_exists, mock_open_file, mock_uuid):
        mock_exists.return_value = True
        mock_open_file.return_value.read.return_value = "12345-ABCDE"
        hardware_id = load_hardware_id()
        self.assertEqual(hardware_id, "12345-ABCDE")

    @patch('utils.device_info.uuid.uuid1', return_value="12345-ABCDE")
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_load_hardware_id_new(self, mock_exists, mock_open_file, mock_uuid):
        mock_exists.return_value = False
        hardware_id = load_hardware_id()
        self.assertEqual(hardware_id, "12345-ABCDE")
        mock_open_file.assert_called_with('hardware_id.txt', 'w')
        mock_open_file().write.assert_called_once_with("12345-ABCDE")

    @patch('platform.system', return_value='Windows')
    @patch('subprocess.run')
    def test_get_installed_apps_windows(self, mock_subprocess, mock_platform):
        mock_subprocess.return_value.stdout = b'App1\nApp2\nApp3\n'
        apps = get_installed_apps()
        self.assertEqual(apps, ['App1', 'App2', 'App3'])

    @patch('platform.system', return_value='Windows')
    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, ['wmic']))
    def test_get_installed_apps_windows_error(self, mock_subprocess, mock_platform):
        apps = get_installed_apps()
        self.assertIn("Error getting apps from Windows", apps[0])

    @patch('platform.system', return_value='Linux')
    @patch('subprocess.run')
    def test_get_installed_apps_linux(self, mock_subprocess, mock_platform):
        mock_subprocess.return_value.stdout = b'package1\tinstall\npackage2\tinstall\npackage3\tinstall\n'
        apps = get_installed_apps()
        self.assertEqual(apps, ['package1', 'package2', 'package3'])

    @patch('platform.system', return_value='Linux')
    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, ['dpkg']))
    def test_get_installed_apps_linux_error(self, mock_subprocess, mock_platform):
        apps = get_installed_apps()
        self.assertIn("Error getting apps from Linux", apps[0])

    @patch('platform.system', return_value='Darwin')
    def test_get_installed_apps_unsupported_os(self, mock_platform):
        apps = get_installed_apps()
        self.assertEqual(apps, ["Installed apps retrieval is not supported on this OS."])

    @patch('requests.get')
    def test_get_geolocation_success(self, mock_get):
        mock_get.return_value.json.return_value = {'loc': '37.7749,-122.4194'}
        location = get_geolocation()
        self.assertEqual(location, '37.7749,-122.4194')

    @patch('requests.get', side_effect=Exception("Network error"))
    def test_get_geolocation_error(self, mock_get):
        location = get_geolocation()
        self.assertIn("Error retrieving location", location)

if __name__ == '__main__':
    unittest.main()
