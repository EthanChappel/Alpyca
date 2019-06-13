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

    def action(self, action: str, *args):
        """Access functionality beyond the built-in capabilities of the ASCOM device interfaces.
        
        Args:
            action (str): A well known name that represents the action to be carried out.
            *args: List of required parameters or empty if none are required.

        """
        return self._put("action", Action=action, Parameters=args)["Value"]

    def commandblind(self, command: str, raw: bool):
        """Transmit an arbitrary string to the device and does not wait for a response.

        Args:
            command (str): The literal command string to be transmitted.
            raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.

        """
        self._put("commandblind", Command=command, Raw=raw)

    def commandbool(self, command: str, raw: bool):
        """Transmit an arbitrary string to the device and wait for a boolean response.
        
        Args:
            command (str): The literal command string to be transmitted.
            raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.

        """
        return self._put("commandbool", Command=command, Raw=raw)["Value"]

    def commandstring(self, command: str, raw: bool):
        """Transmit an arbitrary string to the device and wait for a string response.

        Args:
            command (str): The literal command string to be transmitted.
            raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.

        """
        return self._put("commandstring", Command=command, Raw=raw)["Value"]

    def connected(self, connected: Optional[bool] = None):
        """Retrieve or set the connected state of the device.

        Args:
            connected (bool): Set True to connect to device hardware.
                Set False to disconnect from device hardware.
                Set None to get connected state (default).
        
        """
        if connected == None:
            return self._get("connected")
        else:
            self._put("connected", Connected=connected)

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

    def slaved(self, slaved: Optional[bool] = None) -> bool:
        """Set or indicate whether the dome is slaved to the telescope.
        
        Returns:
            True or False value in not set.
        
        """
        if slaved == None:
            return self._get("slaved")
        else:
            self._put("slaved", Slaved=slaved)

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

    def slewtoaltitude(self, altitude: float):
        """Slew the dome to the given altitude position."""
        self._put("slewtoaltitude", Altitude=altitude)

    def slewtoazimuth(self, azimuth: float):
        """Slew the dome to the given azimuth position.
        
        Args:
            azimuth (float): Target dome azimuth (degrees, North zero and increasing
                clockwise. i.e., 90 East, 180 South, 270 West).

        """
        self._put("slewtoazimuth", Azimuth=azimuth)

    def synctoazimuth(self, azimuth: float):
        """Synchronize the current position of the dome to the given azimuth.

        Args:
            azimuth (float): Target dome azimuth (degrees, North zero and increasing
                clockwise. i.e., 90 East, 180 South, 270 West).
        
        """
        self._put("synctoazimuth", Azimuth=azimuth)


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

    def position(self, position: Optional[int] = None):
        """Set or return the filter wheel position.

        Args:
            position (int): Number of the filter wheel position to select.

        Returns:
            Returns the current filter wheel position.
        
        """
        if position == None:
            return self._get("position")
        else:
            self._put("position", Position=position)


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

    def declinationrate(self, declination_rate: Optional[float] = None):
        """Set or return the telescope's declination tracking rate.

        Args:
            declination_rate (float): Declination tracking rate (arcseconds per second).
        
        Returns:
            The declination tracking rate (arcseconds per second) if declinatio_rate is
            not set.
        
        """
        if declination_rate == None:
            return self._get("declinationrate")
        else:
            self._put("declinationrate", DeclinationRate=declination_rate)

    def doesrefraction(self, does_refraction: Optional[bool] = None):
        """Indicate or determine if atmospheric refraction is applied to coordinates.

        Args:
            does_refraction (bool): Set True to make the telescope or driver apply
            atmospheric refraction to coordinates.
        
        Returns:   
            True if the telescope or driver applies atmospheric refraction to
            coordinates.

        """
        if does_refraction == None:
            return self._get("doesrefraction")
        else:
            self._put("doesrefraction", DoesRefraction=does_refraction)

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

    def guideratedeclination(self, guide_rate_declination: Optional[float] = None):
        """Set or return the current Declination rate offset for telescope guiding.

        Args:
            guide_rate_declination (float): Declination movement rate offset
                (degrees/sec).

        Returns:
            Current declination rate offset for telescope guiding if not set.

        """
        if guide_rate_declination == None:
            return self._get("guideratedeclination")
        else:
            self._put(
                "guideratedeclination", GuideRateDeclination=guide_rate_declination
            )

    def guideraterightascension(
        self, guide_rate_right_ascension: Optional[float] = None
    ):
        """Set or return the current RightAscension rate offset for telescope guiding.

        Args:
            guide_rate_right_ascension (float): RightAscension movement rate offset
                (degrees/sec).

        Returns:
            Current right ascension rate offset for telescope guiding if not set.

        """
        if guide_rate_right_ascension == None:
            return self._get("guideraterightascension")
        else:
            self._put(
                "guideraterightascension",
                GuideRateRightAscension=guide_rate_right_ascension,
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

    def rightascensionrate(self, right_ascension_rate: Optional[float] = None):
        """Set or return the telescope's right ascension tracking rate.

        Args:
            right_ascension_rate (float): Right ascension tracking rate (arcseconds per
                second).

        Returns:
            Telescope's right ascension tracking rate if not set.

        """
        if right_ascension_rate == None:
            return self._get("rightascensionrate")
        else:
            self._put("rightascensionrate", RightAscensionRate=right_ascension_rate)

    def sideofpier(self, side_of_pier: Optional[int] = None):
        """Set or return the mount's pointing state.

        Args:
            side_of_pier (int): New pointing state. 0 = pierEast, 1 = pierWest
        
        Returns:
            Side of pier if not set.
        
        """
        if side_of_pier == None:
            return self._get("sideofpier")
        else:
            self._put("sideofpier", SideOfPier=side_of_pier)

    def siderealtime(self):
        """Return the local apparent sidereal time.

        Returns:
            The local apparent sidereal time from the telescope's internal clock (hours,
            sidereal).

        """
        return self._get("siderealtime")

    def siteelevation(self, site_elevation: Optional[float] = None):
        """Set or return the observing site's elevation above mean sea level.

        Args:
            site_elevation (float): Elevation above mean sea level (metres).
        
        Returns:
            Elevation above mean sea level (metres) of the site at which the telescope
            is located if not set.

        """
        if site_elevation == None:
            return self._get("siteelevation")
        else:
            self._put("siteelevation", SiteElevation=site_elevation)

    def sitelatitude(self, site_latitude: Optional[float] = None):
        """Set or return the observing site's latitude.

        Args:
            site_latotude (float): Site latitude (degrees).
        
        Returns:
            Geodetic(map) latitude (degrees, positive North, WGS84) of the site at which
            the telescope is located if not set.
        
        """
        if site_latitude == None:
            return self._get("sitelatitude")
        else:
            self._put("sitelatitude", SiteLatitude=site_latitude)

    def sitelongitude(self, site_longitude: Optional[float] = None):
        """Set or return the observing site's longitude.

        Args:
            site_longitude (float): Site longitude (degrees, positive East, WGS84)
        
        Returns:
            Longitude (degrees, positive East, WGS84) of the site at which the telescope
            is located.
        
        """
        if site_longitude == None:
            return self._get("sitelongitude")
        else:
            self._put("sitelongitude", SiteLongitude=site_longitude)

    def slewing(self):
        """Indicate whether the telescope is currently slewing.

        Returns:
            True if telescope is currently moving in response to one of the Slew methods
            or the moveaxis(int, float) method, False at all other times.

        """
        return self._get("slewing")

    def slewsettletime(self, slew_settle_time: Optional[int] = None):
        """Set or return the post-slew settling time.

        Args:
            slew_settle_time (int): Settling time (integer sec.).

        Returns:
            Returns the post-slew settling time (sec.) if not set.

        """
        if slew_settle_time == None:
            return self._get("slewsettletime")
        else:
            self._put("slewsettletime", SlewSettleTime=slew_settle_time)

    def targetdeclination(self, target_declination: Optional[float] = None):
        """Set or return the target declination of a slew or sync.

        Args:
            target_declination (float): Target declination(degrees)
        
        Returns:
            Declination (degrees, positive North) for the target of an equatorial slew
            or sync operation.
        
        """
        if target_declination == None:
            return self._get("targetdeclination")
        else:
            self._put("targetdeclination", TargetDeclination=target_declination)

    def targetrightascension(self, target_right_ascension: Optional[float] = None):
        """Set or return the current target right ascension.

        Args:
            target_right_ascension (float): Target right ascension(hours).
        
        Returns:
            Right ascension (hours) for the target of an equatorial slew or sync
            operation.

        """
        if target_right_ascension == None:
            return self._get("targetrightascension")
        else:
            self._put(
                "targetrightascension", TargetRightAscension=target_right_ascension
            )

    def tracking(self, tracking: Optional[bool] = None):
        """Enable, disable, or indicate whether the telescope is tracking.

        Args:
            tracking (bool): Tracking enabled / disabled.
        
        Returns:
            State of the telescope's sidereal tracking drive.
        
        """
        if tracking == None:
            return self._get("tracking")
        else:
            self._put("tracking", Tracking=tracking)

    def trackingrate(self, tracking_rate: Optional[int] = None):
        """Set or return the current tracking rate.

        Args:
            tracking_rate (int): New tracking rate. 0 = driveSidereal, 1 = driveLunar,
                2 = driveSolar, 3 = driveKing.
        
        Returns:
            Current tracking rate of the telescope's sidereal drive if not set.
        
        """
        if tracking_rate == None:
            return self._get("trackingrate")
        else:
            self._put("trackingrate", TrackingRate=tracking_rate)

    def trackingrates(self):
        """Return a collection of supported DriveRates values.

        Returns:
            List of supported DriveRates values that describe the permissible values of
            the TrackingRate property for this telescope type.

        """
        return self._get("trackingrates")

    def utcdate(self, utc_date: Optional[Union[str, datetime]] = None):
        """Set or return the UTC date/time of the telescope's internal clock.

        Args:
            utc_date: UTC date/time as an str or datetime.
        
        Returns:
            datetime of the UTC date/time if not set.
        
        """
        if utc_date == None:
            return dateutil.parser.parse(self._get("utcdate"))
        else:
            if type(utc_date) is str:
                data = utc_date
            elif type(utc_date) is datetime:
                data = utc_date.isoformat()
            else:
                raise TypeError()

            self._put("utcdate", UTCDate=data)

    def abortslew(self):
        """Immediatley stops a slew in progress."""
        self._put("abortslew")

    def axisrates(self, axis: int):
        """Return rates at which the telescope may be moved about the specified axis.

        Returns:
            The rates at which the telescope may be moved about the specified axis by
            the moveaxis(int, float) method.
        
        """
        return self._get("axisrates", Axis=axis)

    def canmoveaxis(self, axis: int):
        """Indicate whether the telescope can move the requested axis.

        Returns:
            True if this telescope can move the requested axis.

        """
        return self._get("canmoveaxis", Axis=axis)

    def destinationsideofpier(self, right_ascension: float, declination: float):
        """Predicts the pointing state after a German equatorial mount slews to given coordinates.

        Args:
            right_ascension (float): Right Ascension coordinate (0.0 to 23.99999999
                hours).
            declination (float): Declination coordinate (-90.0 to +90.0 degrees).

        Returns:
            Pointing state that a German equatorial mount will be in if it slews to the
            given coordinates. The return value will be one of - 0 = pierEast,
            1 = pierWest, -1 = pierUnknown.

        """
        return self._get(
            "destinationsideofpier",
            RightAscension=right_ascension,
            Declination=declination,
        )

    def findhome(self):
        """Move the mount to the "home" position."""
        self._put("findhome")

    def moveaxis(self, axis: int, rate: float):
        """Move a telescope axis at the given rate.

        Args:
            axis (int): The axis about which rate information is desired.
                0 = axisPrimary, 1 = axisSecondary, 2 = axisTertiary.
            rate (float): The rate of motion (deg/sec) about the specified axis

        """
        self._put("moveaxis", Axis=axis, Rate=rate)

    def park(self):
        """Park the mount."""
        self._put("park")

    def pulseguide(self, direction: int, duration: int):
        """Move the scope in the given direction for the given time.

        Notes:
            0 = guideNorth, 1 = guideSouth, 2 = guideEast, 3 = guideWest.

        Args:
            direction (int): Direction in which the guide-rate motion is to be made.
            duration (int): Duration of the guide-rate motion (milliseconds).
        
        """
        self._put("pulseguide", Direction=direction, Duration=duration)

    def setpark(self):
        """Set the telescope's park position."""
        self._put("setpark")

    def slewtoaltaz(self, azimuth: float, altitude: float):
        """Slew synchronously to the given local horizontal coordinates.

        Args:
            azimuth (float): Azimuth coordinate (degrees, North-referenced, positive
                East/clockwise).
            altitude (float): Altitude coordinate (degrees, positive up).

        """
        self._put("slewtoaltaz", Azimuth=azimuth, Altitude=altitude)

    def slewtoaltazasync(self, azimuth: float, altitude: float):
        """Slew asynchronously to the given local horizontal coordinates.

        Args:
            azimuth (float): Azimuth coordinate (degrees, North-referenced, positive
                East/clockwise).
            altitude (float): Altitude coordinate (degrees, positive up).

        """
        self._put("slewtoaltazasync", Azimuth=azimuth, Altitude=altitude)

    def slewtocoordinates(self, right_ascension: float, declination: float):
        """Slew synchronously to the given equatorial coordinates.

        Args:
            right_ascension (float): Right Ascension coordinate (hours).
            declination (float): Declination coordinate (degrees).

        """
        self._put(
            "slewtocoordinates", RightAscension=right_ascension, Declination=declination
        )

    def slewtocoordinatesasync(self, right_ascension: float, declination: float):
        """Slew asynchronously to the given equatorial coordinates.

        Args:
            right_ascension (float): Right Ascension coordinate (hours).
            declination (float): Declination coordinate (degrees).
        
        """
        self._put(
            "slewtocoordinatesasync",
            RightAscension=right_ascension,
            Declination=declination,
        )

    def slewtotarget(self):
        """Slew synchronously to the TargetRightAscension and TargetDeclination coordinates."""
        self._put("slewtotarget")

    def slewtotargetasync(self):
        """Asynchronously slew to the TargetRightAscension and TargetDeclination coordinates."""
        self._put("slewtotargetasync")

    def synctoaltaz(self, azimuth: float, altitude: float):
        """Sync to the given local horizontal coordinates.

        Args:
            azimuth (float): Azimuth coordinate (degrees, North-referenced, positive
                East/clockwise).
            altitude (float): Altitude coordinate (degrees, positive up).

        """
        self._put("synctoaltaz", Azimuth=azimuth, Altitude=altitude)

    def synctocoordinates(self, right_ascension: float, declination: float):
        """Sync to the given equatorial coordinates.

        Args:
            right_ascension (float): Right Ascension coordinate (hours).
            declination (float): Declination coordinate (degrees).

        """
        self._put(
            "synctocoordinates", RightAscension=right_ascension, Declination=declination
        )

    def synctotarget(self):
        """Sync to the TargetRightAscension and TargetDeclination coordinates."""
        self._put("synctotarget")

    def unpark(self):
        """Unpark the mount."""
        self._put("unpark")
