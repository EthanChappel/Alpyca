"""This module wraps the HTTP requests for the ASCOM Alpaca API into pythonic classes with methods.

Attributes:
    DEFAULT_API_VERSION (int): Default Alpaca API spec to use if none is specified when needed.

"""
import requests


DEFAULT_API_VERSION = 1


class Device:
    """Common methods across all ASCOM Alpaca devices.

    Attributes:
        address (str): Domain name or IP address of Alpaca server.
            Can also specify port number if needed.
        device_type (str): One of the recognised ASCOM device types
            e.g. telescope (must be lower case).
        device_number (int): Zero based device number as set on the server (0 to 4294967295).
        protocall (str): Protocall used to communicate with Alpaca server.
        api_version (int): Alpaca API version.
        base_url (str): Basic URL to easily append with commands.

    """

    def __init__(self, address, device_type, device_number, protocall, api_version):
        """Initialize Device object."""
        self.address = address
        self.device_type = device_type
        self.device_number = device_number
        self.api_version = api_version
        self.base_url = "%s://%s/api/v%d/%s/%d" % (
            protocall,
            address,
            api_version,
            device_type,
            device_number,
        )

    def action(self, action, *args):
        """Access functionality beyond the built-in capabilities of the ASCOM device interfaces.
        
        Args:
            action: A well known name that represents the action to be carried out.
            *args: List of required parameters or empty if none are required.

        """
        return requests.put(
            "%s/action" % self.base_url, data={"Action": action, "Parameters": args}
        )

    def commandblind(self, command, raw):
        """Transmit an arbitrary string to the device and does not wait for a response.

        Args:
            command (str): The literal command string to be transmitted.
            raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to transmission.

        """
        return requests.put(
            "%s/commandblind" % self.base_url, data={"Command": command, "Raw": raw}
        )

    def commandbool(self, command, raw):
        """Transmit an arbitrary string to the device and wait for a boolean response.
        
        Args:
            command (str): The literal command string to be transmitted.
            raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to transmission.

        """
        return bool(
            requests.put(
                "%s/commandbool" % self.base_url, data={"Command": command, "Raw": raw}
            )
        )

    def commandstring(self, command, raw):
        """Transmit an arbitrary string to the device and wait for a string response.

        Args:
            command (str): The literal command string to be transmitted.
            raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to transmission.

        """
        return requests.put(
            "%s/commandstring" % self.base_url, data={"Command": command, "Raw": raw}
        )

    def connected(self, connected=None):
        """Retrieve or set the connected state of the device.

        Args:
            connected (bool): Set True to connect to device hardware.
                Set False to disconnect from device hardware.
                Set None to get connected state (default).
        
        """
        if connected == None:
            return bool(requests.get("%s/connected" % self.base_url).json()["Value"])
        else:
            return requests.put(
                "%s/connected" % self.base_url, data={"Connected": connected}
            )

    def description(self):
        """Get description of the device."""
        return requests.get("%s/description" % self.base_url).json()["Value"]

    def driverinfo(self):
        """Get information of the device."""
        return [
            i.strip()
            for i in requests.get("%s/driverinfo" % self.base_url)
            .json()["Value"]
            .split(",")
        ]

    def driverversion(self):
        """Get string containing only the major and minor version of the driver."""
        return requests.get("%s/driverversion" % self.base_url).json()["Value"]

    def interfaceversion(self):
        """ASCOM Device interface version number that this device supports."""
        return int(requests.get("%s/interfaceversion" % self.base_url).json()["Value"])

    def name(self):
        """Get name of the device."""
        return requests.get("%s/name" % self.base_url).json()["Value"]

    def supportedactions(self):
        """Get list of action names supported by this driver."""
        return requests.get("%s/supportedactions" % self.base_url).json()["Value"]

    def _get(self, attribute):
        """Send an HTTP GET request to an Alpaca server and check response for errors.

        Args:
            attribute (str): Attribute to get from server.
        
        """
        response = requests.get("%s/%s" % (self.base_url, attribute))

        if response.json()["ErrorNumber"] != 0:
            raise Exception(
                "Error %d: %s"
                % (response.json()["ErrorNumber"], response.json()["ErrorMessage"])
            )
        elif response.status_code == 400 or response.status_code == 500:
            raise Exception(response.json()["Value"])

        return response
