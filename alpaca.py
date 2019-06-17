"""Wraps the HTTP requests for the ASCOM Alpaca API into pythonic classes with methods.

Attributes:
    DEFAULT_API_VERSION (int): Default Alpaca API spec to use if none is specified when
    needed.

"""

from datetime import datetime
from typing import Optional, Union, List, Dict, Mapping, Any
import dateutil.parser
import requests


DEFAULT_API_VERSION = 1


class Device:
    """Common methods across all ASCOM Alpaca devices.

    Attributes:
        address (str): Domain name or IP address of Alpaca server.
            Can also specify port number if needed.
        device_type (str): One of the recognised ASCOM device types
            e.g. telescope (must be lower case).
        device_number (int): Zero based device number as set on the server (0 to
            4294967295).
        protocall (str): Protocall used to communicate with Alpaca server.
        api_version (int): Alpaca API version.
        base_url (str): Basic URL to easily append with commands.

    """

    def __init__(
        self,
        address: str,
        device_type: str,
        device_number: int,
        protocall: str,
        api_version: int,
    ):
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

    def action(self, Action: str, *Parameters):
        """Access functionality beyond the built-in capabilities of the ASCOM device interfaces.
        
        Args:
            Action (str): A well known name that represents the action to be carried out.
            *Parameters: List of required parameters or empty if none are required.

        """
        return self._put("action", Action=Action, Parameters=Parameters)["Value"]

    def commandblind(self, Command: str, Raw: bool):
        """Transmit an arbitrary string to the device and does not wait for a response.

        Args:
            Command (str): The literal command string to be transmitted.
            Raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.

        """
        self._put("commandblind", Command=Command, Raw=Raw)

    def commandbool(self, Command: str, Raw: bool):
        """Transmit an arbitrary string to the device and wait for a boolean response.
        
        Args:
            Command (str): The literal command string to be transmitted.
            Raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.

        """
        return self._put("commandbool", Command=Command, Raw=Raw)["Value"]

    def commandstring(self, Command: str, Raw: bool):
        """Transmit an arbitrary string to the device and wait for a string response.

        Args:
            Command (str): The literal command string to be transmitted.
            Raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.

        """
        return self._put("commandstring", Command=Command, Raw=Raw)["Value"]

    def connected(self, Connected: Optional[bool] = None):
        """Retrieve or set the connected state of the device.

        Args:
            Connected (bool): Set True to connect to device hardware.
                Set False to disconnect from device hardware.
                Set None to get connected state (default).
        
        """
        if Connected == None:
            return self._get("connected")
        else:
            self._put("connected", Connected=Connected)

    def description(self) -> str:
        """Get description of the device."""
        return self._get("name")

    def driverinfo(self) -> List[str]:
        """Get information of the device."""
        return [i.strip() for i in self._get("driverinfo").split(",")]

    def driverversion(self) -> str:
        """Get string containing only the major and minor version of the driver."""
        return self._get("driverversion")

    def interfaceversion(self) -> int:
        """ASCOM Device interface version number that this device supports."""
        return self._get("interfaceversion")

    def name(self) -> str:
        """Get name of the device."""
        return self._get("name")

    def supportedactions(self) -> List[str]:
        """Get list of action names supported by this driver."""
        return self._get("supportedactions")

    def _get(self, attribute: str, **data):
        """Send an HTTP GET request to an Alpaca server and check response for errors.

        Args:
            attribute (str): Attribute to get from server.
            **data: Data to send with request.
        
        """
        response = requests.get("%s/%s" % (self.base_url, attribute), data=data)
        self.__check_error(response)
        return response.json()["Value"]

    def _put(self, attribute: str, **data):
        """Send an HTTP PUT request to an Alpaca server and check response for errors.

        Args:
            attribute (str): Attribute to put to server.
            **data: Data to send with request.
        
        """
        response = requests.put("%s/%s" % (self.base_url, attribute), data=data)
        self.__check_error(response)
        return response.json()

    def __check_error(self, response: requests.Response):
        """Check response from Alpaca server for Errors.

        Args:
            response (Response): Response from Alpaca server to check.

        """
        if response.json()["ErrorNumber"] != 0:
            raise Exception(
                "Error %d: %s"
                % (response.json()["ErrorNumber"], response.json()["ErrorMessage"])
            )
        elif response.status_code == 400 or response.status_code == 500:
            raise Exception(response.json()["Value"])


class Switch(Device):
    """Switch specific methods."""

    def __init__(
        self,
        address: str,
        device_number: int,
        protocall: str = "http",
        api_version: int = DEFAULT_API_VERSION,
    ):
        """Initialize Switch object."""
        super().__init__(address, "switch", device_number, protocall, api_version)

    def maxswitch(self) -> int:
        """Count of switch devices managed by this driver.

        Returns:
            Number of switch devices managed by this driver. Devices are numbered from 0
            to MaxSwitch - 1.
        
        """
        return self._get("maxswitch")

    def canwrite(self, Id: Optional[int] = 0) -> bool:
        """Indicate whether the specified switch device can be written to.

        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.

        Args:
            Id (int): The device number.

        Returns:
            Whether the specified switch device can be written to, default true. This is
            false if the device cannot be written to, for example a limit switch or a
            sensor.
        
        """
        return self._get("canwrite", Id=Id)

    def getswitch(self, Id: Optional[int] = 0) -> bool:
        """Return the state of switch device id as a boolean.

        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.

        Args:
            Id (int): The device number.
        
        Returns:
            State of switch device id as a boolean.
        
        """
        return self._get("getswitch", Id=Id)

    def getswitchdescription(self, Id: Optional[int] = 0) -> str:
        """Get the description of the specified switch device.

        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.

        Args:
            Id (int): The device number.
        
        Returns:
            Description of the specified switch device.
        
        """
        return self._get("getswitchdescription", Id=Id)

    def getswitchname(self, Id: Optional[int] = 0) -> str:
        """Get the name of the specified switch device.

        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.

        Args:
            Id (int): The device number.
        
        Returns:
            Name of the specified switch device.
        
        """
        return self._get("getswitchname", Id=Id)

    def getswitchvalue(self, Id: Optional[int] = 0) -> str:
        """Get the value of the specified switch device as a double.

        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.

        Args:
            Id (int): The device number.
        
        Returns:
            Value of the specified switch device.
        
        """
        return self._get("getswitchvalue", Id=Id)

    def minswitchvalue(self, Id: Optional[int] = 0) -> str:
        """Get the minimum value of the specified switch device as a double.

        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.

        Args:
            Id (int): The device number.
        
        Returns:
            Minimum value of the specified switch device as a double.
        
        """
        return self._get("minswitchvalue", Id=Id)

    def setswitch(self, Id: int, State: bool):
        """Set a switch controller device to the specified state, True or False.

        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.

        Args:
            Id (int): The device number.
            State (bool): The required control state (True or False).

        """
        self._put("setswitch", Id=Id, State=State)

    def setswitchname(self, Id: int, Name: str):
        """Set a switch device name to the specified value.

        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.

        Args:
            Id (int): The device number.
            Name (str): The name of the device.

        """
        self._put("setswitchname", Id=Id, Name=Name)

    def setswitchvalue(self, Id: int, Value: float):
        """Set a switch device value to the specified value.

        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.

        Args:
            Id (int): The device number.
            Value (float): Value to be set, between MinSwitchValue and MaxSwitchValue.

        """
        self._put("setswitchvalue", Id=Id, Value=Value)

    def switchstep(self, Id: Optional[int] = 0) -> str:
        """Return the step size that this device supports.

        Return the step size that this device supports (the difference between
        successive values of the device).

        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.

        Args:
            Id (int): The device number.
        
        Returns:
            Maximum value of the specified switch device as a double.
        
        """
        return self._get("switchstep", Id=Id)


class SafetyMonitor(Device):
    """Safety monitor specific methods."""

    def __init__(
        self,
        address: str,
        device_number: int,
        protocall: str = "http",
        api_version: int = DEFAULT_API_VERSION,
    ):
        """Initialize SafetyMonitor object."""
        super().__init__(
            address, "safetymonitor", device_number, protocall, api_version
        )

    def issafe(self) -> bool:
        """Indicate whether the monitored state is safe for use.

        Returns:
            True if the state is safe, False if it is unsafe.
        
        """
        return self._get("issafe")


class Dome(Device):
    """Dome specific methods."""

    def __init__(
        self,
        address: str,
        device_number: int,
        protocall: str = "http",
        api_version: int = DEFAULT_API_VERSION,
    ):
        """Initialize Dome object."""
        super().__init__(address, "dome", device_number, protocall, api_version)

    def altitude(self) -> float:
        """Dome altitude.

        Returns:
            Dome altitude (degrees, horizon zero and increasing positive to 90 zenith).
        
        """
        return self._get("altitude")

    def athome(self) -> bool:
        """Indicate whether the dome is in the home position.

        Notes:
            This is normally used following a findhome() operation. The value is reset
            with any azimuth slew operation that moves the dome away from the home
            position. athome() may also become true durng normal slew operations, if the
            dome passes through the home position and the dome controller hardware is
            capable of detecting that; or at the end of a slew operation if the dome
            comes to rest at the home position.

        Returns:
            True if dome is in the home position.
        
        """
        return self._get("athome")

    def atpark(self) -> bool:
        """Indicate whether the telescope is at the park position.

        Notes:
            Set only following a park() operation and reset with any slew operation.

        Returns:
            True if the dome is in the programmed park position.

        """
        return self._get("atpark")

    def azimuth(self) -> float:
        """Dome azimuth.

        Returns:
            Dome azimuth (degrees, North zero and increasing clockwise, i.e., 90 East,
            180 South, 270 West).

        """
        return self._get("azimuth")

    def canfindhome(self) -> bool:
        """Indicate whether the dome can find the home position.

        Returns:
            True if the dome can move to the home position.
        
        """
        return self._get("canfindhome")

    def canpark(self) -> bool:
        """Indicate whether the dome can be parked.

        Returns:
            True if the dome is capable of programmed parking (park() method).
        
        """
        return self._get("canpark")

    def cansetaltitude(self) -> bool:
        """Indicate whether the dome altitude can be set.

        Returns:
            True if driver is capable of setting the dome altitude.
        
        """
        return self._get("cansetaltitude")

    def cansetazimuth(self) -> bool:
        """Indicate whether the dome azimuth can be set.

        Returns:
            True if driver is capable of setting the dome azimuth.
        
        """
        return self._get("cansetazimuth")

    def cansetpark(self) -> bool:
        """Indicate whether the dome park position can be set.

        Returns:
            True if driver is capable of setting the dome park position.
        
        """
        return self._get("cansetpark")

    def cansetshutter(self) -> bool:
        """Indicate whether the dome shutter can be opened.

        Returns:
            True if driver is capable of automatically operating shutter.

        """
        return self._get("cansetshutter")

    def canslave(self) -> bool:
        """Indicate whether the dome supports slaving to a telescope.

        Returns:
            True if driver is capable of slaving to a telescope.
        
        """
        return self._get("canslave")

    def cansyncazimuth(self) -> bool:
        """Indicate whether the dome azimuth position can be synched.

        Notes:
            True if driver is capable of synchronizing the dome azimuth position using
            the synctoazimuth(float) method.
        
        Returns:
            True or False value.
        
        """
        return self._get("cansyncazimuth")

    def shutterstatus(self) -> int:
        """Status of the dome shutter or roll-off roof.

        Notes:
            0 = Open, 1 = Closed, 2 = Opening, 3 = Closing, 4 = Shutter status error.
        
        Returns:
            Status of the dome shutter or roll-off roof.

        """
        return self._get("shutterstatus")

    def slaved(self, Slaved: Optional[bool] = None) -> bool:
        """Set or indicate whether the dome is slaved to the telescope.
        
        Returns:
            True or False value in not set.
        
        """
        if Slaved == None:
            return self._get("slaved")
        else:
            self._put("slaved", Slaved=Slaved)

    def slewing(self) -> bool:
        """Indicate whether the any part of the dome is moving.

        Notes:
            True if any part of the dome is currently moving, False if all dome
            components are steady.
        
        Return:
            True or False value.
        
        """
        return self._get("slewing")

    def abortslew(self):
        """Immediately cancel current dome operation.

        Notes:
            Calling this method will immediately disable hardware slewing (Slaved will
            become False).

        """
        self._put("abortslew")

    def closeshutter(self):
        """Close the shutter or otherwise shield telescope from the sky."""
        self._put("closeshutter")

    def findhome(self):
        """Start operation to search for the dome home position.

        Notes:
            After home position is established initializes azimuth to the default value
            and sets the athome flag.
        
        """
        self._put("findhome")

    def openshutter(self):
        """Open shutter or otherwise expose telescope to the sky."""
        self._put("openshutter")

    def park(self):
        """Rotate dome in azimuth to park position.

        Notes:
            After assuming programmed park position, sets atpark flag.
        
        """
        self._put("park")

    def setpark(self):
        """Set current azimuth, altitude position of dome to be the park position."""
        self._put("setpark")

    def slewtoaltitude(self, Altitude: float):
        """Slew the dome to the given altitude position."""
        self._put("slewtoaltitude", Altitude=Altitude)

    def slewtoazimuth(self, Azimuth: float):
        """Slew the dome to the given azimuth position.
        
        Args:
            Azimuth (float): Target dome azimuth (degrees, North zero and increasing
                clockwise. i.e., 90 East, 180 South, 270 West).

        """
        self._put("slewtoazimuth", Azimuth=Azimuth)

    def synctoazimuth(self, Azimuth: float):
        """Synchronize the current position of the dome to the given azimuth.

        Args:
            Azimuth (float): Target dome azimuth (degrees, North zero and increasing
                clockwise. i.e., 90 East, 180 South, 270 West).
        
        """
        self._put("synctoazimuth", Azimuth=Azimuth)


class FilterWheel(Device):
    """Filter wheel specific methods."""

    def __init__(
        self,
        address: str,
        device_number: int,
        protocall: str = "http",
        api_version: int = DEFAULT_API_VERSION,
    ):
        """Initialize FilterWheel object."""
        super().__init__(address, "filterwheel", device_number, protocall, api_version)

    def focusoffsets(self) -> List[int]:
        """Filter focus offsets.

        Returns:
            An integer array of filter focus offsets.
        
        """
        return self._get("focusoffsets")

    def names(self) -> List[str]:
        """Filter wheel filter names.

        Returns:
            Names of the filters.

        """
        return self._get("names")

    def position(self, Position: Optional[int] = None):
        """Set or return the filter wheel position.

        Args:
            Position (int): Number of the filter wheel position to select.

        Returns:
            Returns the current filter wheel position.
        
        """
        if Position == None:
            return self._get("position")
        else:
            self._put("position", Position=Position)


class Telescope(Device):
    """Telescope specific methods."""

    def __init__(
        self,
        address: str,
        device_number: int,
        protocall: str = "http",
        api_version: int = DEFAULT_API_VERSION,
    ):
        """Initialize Telescope object."""
        super().__init__(address, "telescope", device_number, protocall, api_version)

    def alignmentmode(self):
        """Return the current mount alignment mode.

        Returns:
            Alignment mode of the mount (Alt/Az, Polar, German Polar).
        
        """
        return self._get("alignmentmode")

    def altitude(self):
        """Return the mount's Altitude above the horizon.

        Returns:
            Altitude of the telescope's current position (degrees, positive up).

        """
        return self._get("altitude")

    def aperturearea(self):
        """Return the telescope's aperture.

        Returns:
            Area of the telescope's aperture (square meters).

        """
        return self._get("aperturearea")

    def aperturediameter(self):
        """Return the telescope's effective aperture.

        Returns:
            Telescope's effective aperture diameter (meters).

        """
        return self._get("aperturediameter")

    def athome(self):
        """Indicate whether the mount is at the home position.

        Returns:
            True if the mount is stopped in the Home position. Must be False if the
            telescope does not support homing.
        
        """
        return self._get("athome")

    def atpark(self):
        """Indicate whether the telescope is at the park position.

        Returns:
            True if the telescope has been put into the parked state by the seee park()
            method. Set False by calling the unpark() method.
        
        """
        return self._get("atpark")

    def azimuth(self):
        """Return the telescope's aperture.
        
        Return:
            Azimuth of the telescope's current position (degrees, North-referenced,
            positive East/clockwise).

        """
        return self._get("azimuth")

    def canfindhome(self):
        """Indicate whether the mount can find the home position.
        
        Returns:
            True if this telescope is capable of programmed finding its home position.
        
        """
        return self._get("canfindhome")

    def canpark(self):
        """Indicate whether the telescope can be parked.

        Returns:
            True if this telescope is capable of programmed parking.
        
        """
        return self._get("canpark")

    def canpulseguide(self):
        """Indicate whether the telescope can be pulse guided.

        Returns:
            True if this telescope is capable of software-pulsed guiding (via the
            pulseguide(int, int) method).
        
        """
        return self._get("canpulseguide")

    def cansetdeclinationrate(self):
        """Indicate whether the DeclinationRate property can be changed.

        Returns:
            True if the DeclinationRate property can be changed to provide offset
            tracking in the declination axis.

        """
        return self._get("cansetdeclinationrate")

    def cansetguiderates(self):
        """Indicate whether the DeclinationRate property can be changed.

        Returns:
            True if the guide rate properties used for pulseguide(int, int) can ba
            adjusted.

        """
        return self._get("cansetguiderates")

    def cansetpark(self):
        """Indicate whether the telescope park position can be set.

        Returns:
            True if this telescope is capable of programmed setting of its park position
            (setpark() method).

        """
        return self._get("cansetpark")

    def cansetpierside(self):
        """Indicate whether the telescope SideOfPier can be set.

        Returns:
            True if the SideOfPier property can be set, meaning that the mount can be
            forced to flip.
        
        """
        return self._get("cansetpierside")

    def cansetrightascensionrate(self):
        """Indicate whether the RightAscensionRate property can be changed.

        Returns:
            True if the RightAscensionRate property can be changed to provide offset
            tracking in the right ascension axis.
        
        """
        return self._get("cansetrightascensionrate")

    def cansettracking(self):
        """Indicate whether the Tracking property can be changed.

        Returns:
            True if the Tracking property can be changed, turning telescope sidereal
            tracking on and off.
        
        """
        return self._get("cansettracking")

    def canslew(self):
        """Indicate whether the telescope can slew synchronously.

        Returns:
            True if this telescope is capable of programmed slewing (synchronous or
            asynchronous) to equatorial coordinates.
        
        """
        return self._get("canslew")

    def canslewaltaz(self):
        """Indicate whether the telescope can slew synchronously to AltAz coordinates.

        Returns:
            True if this telescope is capable of programmed slewing (synchronous or
            asynchronous) to local horizontal coordinates.

        """
        return self._get("canslewaltaz")

    def canslewaltazasync(self):
        """Indicate whether the telescope can slew asynchronusly to AltAz coordinates.

        Returns:
            True if this telescope is capable of programmed asynchronus slewing
            (synchronous or asynchronous) to local horizontal coordinates.

        """
        return self._get("canslewaltazasync")

    def cansync(self):
        """Indicate whether the telescope can sync to equatorial coordinates.

        Returns:
            True if this telescope is capable of programmed synching to equatorial
            coordinates.
        
        """
        return self._get("cansync")

    def cansyncaltaz(self):
        """Indicate whether the telescope can sync to local horizontal coordinates.

        Returns:
            True if this telescope is capable of programmed synching to local horizontal
            coordinates.
        
        """
        return self._get("cansyncaltaz")

    def declination(self):
        """Return the telescope's declination.

        Notes:
            Reading the property will raise an error if the value is unavailable.

        Returns:
            The declination (degrees) of the telescope's current equatorial coordinates,
            in the coordinate system given by the EquatorialSystem property.
        
        """
        return self._get("declination")

    def declinationrate(self, DeclinationRate: Optional[float] = None):
        """Set or return the telescope's declination tracking rate.

        Args:
            DeclinationRate (float): Declination tracking rate (arcseconds per second).
        
        Returns:
            The declination tracking rate (arcseconds per second) if DeclinatioRate is
            not set.
        
        """
        if DeclinationRate == None:
            return self._get("declinationrate")
        else:
            self._put("declinationrate", DeclinationRate=DeclinationRate)

    def doesrefraction(self, DoesRefraction: Optional[bool] = None):
        """Indicate or determine if atmospheric refraction is applied to coordinates.

        Args:
            DoesRefraction (bool): Set True to make the telescope or driver apply
                atmospheric refraction to coordinates.
        
        Returns:   
            True if the telescope or driver applies atmospheric refraction to
            coordinates.

        """
        if DoesRefraction == None:
            return self._get("doesrefraction")
        else:
            self._put("doesrefraction", DoesRefraction=DoesRefraction)

    def equatorialsystem(self):
        """Return the current equatorial coordinate system used by this telescope.

        Returns:
            Current equatorial coordinate system used by this telescope
            (e.g. Topocentric or J2000).

        """
        return self._get("equatorialsystem")

    def focallength(self):
        """Return the telescope's focal length in meters.

        Returns:
            The telescope's focal length in meters.

        """
        return self._get("focallength")

    def guideratedeclination(self, GuideRateDeclination: Optional[float] = None):
        """Set or return the current Declination rate offset for telescope guiding.

        Args:
            GuideRateDeclination (float): Declination movement rate offset
                (degrees/sec).

        Returns:
            Current declination rate offset for telescope guiding if not set.

        """
        if GuideRateDeclination == None:
            return self._get("guideratedeclination")
        else:
            self._put("guideratedeclination", GuideRateDeclination=GuideRateDeclination)

    def guideraterightascension(self, GuideRateRightAscension: Optional[float] = None):
        """Set or return the current RightAscension rate offset for telescope guiding.

        Args:
            GuideRateRightAscension (float): RightAscension movement rate offset
                (degrees/sec).

        Returns:
            Current right ascension rate offset for telescope guiding if not set.

        """
        if GuideRateRightAscension == None:
            return self._get("guideraterightascension")
        else:
            self._put(
                "guideraterightascension",
                GuideRateRightAscension=GuideRateRightAscension,
            )

    def ispulseguiding(self):
        """Indicate whether the telescope is currently executing a PulseGuide command.

        Returns:
            True if a pulseguide(int, int) command is in progress, False otherwise.
        
        """
        return self._get("ispulseguiding")

    def rightascension(self):
        """Return the telescope's right ascension coordinate.

        Returns:
            The right ascension (hours) of the telescope's current equatorial
            coordinates, in the coordinate system given by the EquatorialSystem
            property.

        """
        return self._get("rightascension")

    def rightascensionrate(self, RightAscensionRate: Optional[float] = None):
        """Set or return the telescope's right ascension tracking rate.

        Args:
            RightAscensionRate (float): Right ascension tracking rate (arcseconds per
                second).

        Returns:
            Telescope's right ascension tracking rate if not set.

        """
        if RightAscensionRate == None:
            return self._get("rightascensionrate")
        else:
            self._put("rightascensionrate", RightAscensionRate=RightAscensionRate)

    def sideofpier(self, SideOfPier: Optional[int] = None):
        """Set or return the mount's pointing state.

        Args:
            SideOfPier (int): New pointing state. 0 = pierEast, 1 = pierWest
        
        Returns:
            Side of pier if not set.
        
        """
        if SideOfPier == None:
            return self._get("sideofpier")
        else:
            self._put("sideofpier", SideOfPier=SideOfPier)

    def siderealtime(self):
        """Return the local apparent sidereal time.

        Returns:
            The local apparent sidereal time from the telescope's internal clock (hours,
            sidereal).

        """
        return self._get("siderealtime")

    def siteelevation(self, SiteElevation: Optional[float] = None):
        """Set or return the observing site's elevation above mean sea level.

        Args:
            SiteElevation (float): Elevation above mean sea level (metres).
        
        Returns:
            Elevation above mean sea level (metres) of the site at which the telescope
            is located if not set.

        """
        if SiteElevation == None:
            return self._get("siteelevation")
        else:
            self._put("siteelevation", SiteElevation=SiteElevation)

    def sitelatitude(self, SiteLatitude: Optional[float] = None):
        """Set or return the observing site's latitude.

        Args:
            SiteLatitude (float): Site latitude (degrees).
        
        Returns:
            Geodetic(map) latitude (degrees, positive North, WGS84) of the site at which
            the telescope is located if not set.
        
        """
        if SiteLatitude == None:
            return self._get("sitelatitude")
        else:
            self._put("sitelatitude", SiteLatitude=SiteLatitude)

    def sitelongitude(self, SiteLongitude: Optional[float] = None):
        """Set or return the observing site's longitude.

        Args:
            SiteLongitude (float): Site longitude (degrees, positive East, WGS84)
        
        Returns:
            Longitude (degrees, positive East, WGS84) of the site at which the telescope
            is located.
        
        """
        if SiteLongitude == None:
            return self._get("sitelongitude")
        else:
            self._put("sitelongitude", SiteLongitude=SiteLongitude)

    def slewing(self):
        """Indicate whether the telescope is currently slewing.

        Returns:
            True if telescope is currently moving in response to one of the Slew methods
            or the moveaxis(int, float) method, False at all other times.

        """
        return self._get("slewing")

    def slewsettletime(self, SlewSettleTime: Optional[int] = None):
        """Set or return the post-slew settling time.

        Args:
            SlewSettleTime (int): Settling time (integer sec.).

        Returns:
            Returns the post-slew settling time (sec.) if not set.

        """
        if SlewSettleTime == None:
            return self._get("slewsettletime")
        else:
            self._put("slewsettletime", SlewSettleTime=SlewSettleTime)

    def targetdeclination(self, TargetDeclination: Optional[float] = None):
        """Set or return the target declination of a slew or sync.

        Args:
            TargetDeclination (float): Target declination(degrees)
        
        Returns:
            Declination (degrees, positive North) for the target of an equatorial slew
            or sync operation.
        
        """
        if TargetDeclination == None:
            return self._get("targetdeclination")
        else:
            self._put("targetdeclination", TargetDeclination=TargetDeclination)

    def targetrightascension(self, TargetRightAscension: Optional[float] = None):
        """Set or return the current target right ascension.

        Args:
            TargetRightAscension (float): Target right ascension (hours).
        
        Returns:
            Right ascension (hours) for the target of an equatorial slew or sync
            operation.

        """
        if TargetRightAscension == None:
            return self._get("targetrightascension")
        else:
            self._put("targetrightascension", TargetRightAscension=TargetRightAscension)

    def tracking(self, Tracking: Optional[bool] = None):
        """Enable, disable, or indicate whether the telescope is tracking.

        Args:
            Tracking (bool): Tracking enabled / disabled.
        
        Returns:
            State of the telescope's sidereal tracking drive.
        
        """
        if Tracking == None:
            return self._get("tracking")
        else:
            self._put("tracking", Tracking=Tracking)

    def trackingrate(self, TrackingRate: Optional[int] = None):
        """Set or return the current tracking rate.

        Args:
            TrackingRate (int): New tracking rate. 0 = driveSidereal, 1 = driveLunar,
                2 = driveSolar, 3 = driveKing.
        
        Returns:
            Current tracking rate of the telescope's sidereal drive if not set.
        
        """
        if TrackingRate == None:
            return self._get("trackingrate")
        else:
            self._put("trackingrate", TrackingRate=TrackingRate)

    def trackingrates(self):
        """Return a collection of supported DriveRates values.

        Returns:
            List of supported DriveRates values that describe the permissible values of
            the TrackingRate property for this telescope type.

        """
        return self._get("trackingrates")

    def utcdate(self, UTCDate: Optional[Union[str, datetime]] = None):
        """Set or return the UTC date/time of the telescope's internal clock.

        Args:
            UTCDate: UTC date/time as an str or datetime.
        
        Returns:
            datetime of the UTC date/time if not set.
        
        """
        if UTCDate == None:
            return dateutil.parser.parse(self._get("utcdate"))
        else:
            if type(UTCDate) is str:
                data = UTCDate
            elif type(UTCDate) is datetime:
                data = UTCDate.isoformat()
            else:
                raise TypeError()

            self._put("utcdate", UTCDate=data)

    def abortslew(self):
        """Immediatley stops a slew in progress."""
        self._put("abortslew")

    def axisrates(self, Axis: int):
        """Return rates at which the telescope may be moved about the specified axis.

        Returns:
            The rates at which the telescope may be moved about the specified axis by
            the moveaxis(int, float) method.
        
        """
        return self._get("axisrates", Axis=Axis)

    def canmoveaxis(self, Axis: int):
        """Indicate whether the telescope can move the requested axis.

        Returns:
            True if this telescope can move the requested axis.

        """
        return self._get("canmoveaxis", Axis=Axis)

    def destinationsideofpier(self, RightAscension: float, Declination: float):
        """Predict the pointing state after a German equatorial mount slews to given coordinates.

        Args:
            RightAscension (float): Right Ascension coordinate (0.0 to 23.99999999
                hours).
            Declination (float): Declination coordinate (-90.0 to +90.0 degrees).

        Returns:
            Pointing state that a German equatorial mount will be in if it slews to the
            given coordinates. The return value will be one of - 0 = pierEast,
            1 = pierWest, -1 = pierUnknown.

        """
        return self._get(
            "destinationsideofpier",
            RightAscension=RightAscension,
            Declination=Declination,
        )

    def findhome(self):
        """Move the mount to the "home" position."""
        self._put("findhome")

    def moveaxis(self, Axis: int, Rate: float):
        """Move a telescope axis at the given rate.

        Args:
            Axis (int): The axis about which rate information is desired.
                0 = axisPrimary, 1 = axisSecondary, 2 = axisTertiary.
            Rate (float): The rate of motion (deg/sec) about the specified axis

        """
        self._put("moveaxis", Axis=Axis, Rate=Rate)

    def park(self):
        """Park the mount."""
        self._put("park")

    def pulseguide(self, Direction: int, Duration: int):
        """Move the scope in the given direction for the given time.

        Notes:
            0 = guideNorth, 1 = guideSouth, 2 = guideEast, 3 = guideWest.

        Args:
            Direction (int): Direction in which the guide-rate motion is to be made.
            Duration (int): Duration of the guide-rate motion (milliseconds).
        
        """
        self._put("pulseguide", Direction=Direction, Duration=Duration)

    def setpark(self):
        """Set the telescope's park position."""
        self._put("setpark")

    def slewtoaltaz(self, Azimuth: float, Altitude: float):
        """Slew synchronously to the given local horizontal coordinates.

        Args:
            Azimuth (float): Azimuth coordinate (degrees, North-referenced, positive
                East/clockwise).
            Altitude (float): Altitude coordinate (degrees, positive up).

        """
        self._put("slewtoaltaz", Azimuth=Azimuth, Altitude=Altitude)

    def slewtoaltazasync(self, Azimuth: float, Altitude: float):
        """Slew asynchronously to the given local horizontal coordinates.

        Args:
            Azimuth (float): Azimuth coordinate (degrees, North-referenced, positive
                East/clockwise).
            Altitude (float): Altitude coordinate (degrees, positive up).

        """
        self._put("slewtoaltazasync", Azimuth=Azimuth, Altitude=Altitude)

    def slewtocoordinates(self, RightAscension: float, Declination: float):
        """Slew synchronously to the given equatorial coordinates.

        Args:
            RightAscension (float): Right Ascension coordinate (hours).
            Declination (float): Declination coordinate (degrees).

        """
        self._put(
            "slewtocoordinates", RightAscension=RightAscension, Declination=Declination
        )

    def slewtocoordinatesasync(self, RightAscension: float, Declination: float):
        """Slew asynchronously to the given equatorial coordinates.

        Args:
            RightAscension (float): Right Ascension coordinate (hours).
            Declination (float): Declination coordinate (degrees).
        
        """
        self._put(
            "slewtocoordinatesasync",
            RightAscension=RightAscension,
            Declination=Declination,
        )

    def slewtotarget(self):
        """Slew synchronously to the TargetRightAscension and TargetDeclination coordinates."""
        self._put("slewtotarget")

    def slewtotargetasync(self):
        """Asynchronously slew to the TargetRightAscension and TargetDeclination coordinates."""
        self._put("slewtotargetasync")

    def synctoaltaz(self, Azimuth: float, Altitude: float):
        """Sync to the given local horizontal coordinates.

        Args:
            Azimuth (float): Azimuth coordinate (degrees, North-referenced, positive
                East/clockwise).
            Altitude (float): Altitude coordinate (degrees, positive up).

        """
        self._put("synctoaltaz", Azimuth=Azimuth, Altitude=Altitude)

    def synctocoordinates(self, RightAscension: float, Declination: float):
        """Sync to the given equatorial coordinates.

        Args:
            RightAscension (float): Right Ascension coordinate (hours).
            Declination (float): Declination coordinate (degrees).

        """
        self._put(
            "synctocoordinates", RightAscension=RightAscension, Declination=Declination
        )

    def synctotarget(self):
        """Sync to the TargetRightAscension and TargetDeclination coordinates."""
        self._put("synctotarget")

    def unpark(self):
        """Unpark the mount."""
        self._put("unpark")
