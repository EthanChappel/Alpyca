"""This module wraps the HTTP requests for the ASCOM Alpaca API into pythonic classes with methods.

Attributes:
    DEFAULT_API_VERSION (int): Default Alpaca API spec to use if none is specified when needed.

"""

from datetime import datetime
import requests
from extras import DateTime


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
        return self._put("action", {"Action": action, "Parameters": args})["Value"]

    def commandblind(self, command, raw):
        """Transmit an arbitrary string to the device and does not wait for a response.

        Args:
            command (str): The literal command string to be transmitted.
            raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to transmission.

        """
        return self._put("commandblind", {"Command": command, "Raw": raw})["Value"]

    def commandbool(self, command, raw):
        """Transmit an arbitrary string to the device and wait for a boolean response.
        
        Args:
            command (str): The literal command string to be transmitted.
            raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to transmission.

        """
        return self._put("commandbool", {"Command": command, "Raw": raw})["Value"]

    def commandstring(self, command, raw):
        """Transmit an arbitrary string to the device and wait for a string response.

        Args:
            command (str): The literal command string to be transmitted.
            raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to transmission.

        """
        return self._put("commandstring", {"Command": command, "Raw": raw})["Value"]

    def connected(self, connected=None):
        """Retrieve or set the connected state of the device.

        Args:
            connected (bool): Set True to connect to device hardware.
                Set False to disconnect from device hardware.
                Set None to get connected state (default).
        
        """
        if connected == None:
            return self._get("connected")
        else:
            self._put("connected", {"Connected": connected})

    def description(self):
        """Get description of the device."""
        return self._get("name")

    def driverinfo(self):
        """Get information of the device."""
        return [i.strip() for i in self._get("driverinfo").split(",")]

    def driverversion(self):
        """Get string containing only the major and minor version of the driver."""
        return self._get("driverversion")

    def interfaceversion(self):
        """ASCOM Device interface version number that this device supports."""
        return self._get("interfaceversion")

    def name(self):
        """Get name of the device."""
        return self._get("name")

    def supportedactions(self):
        """Get list of action names supported by this driver."""
        return self._get("supportedactions")

    def _get(self, attribute, data={}):
        """Send an HTTP GET request to an Alpaca server and check response for errors.

        Args:
            attribute (str): Attribute to get from server.
        
        """
        response = requests.get("%s/%s" % (self.base_url, attribute), data=data)
        self.__check_error(response)
        return response.json()["Value"]

    def _put(self, attribute, data={}):
        """Send an HTTP PUT request to an Alpaca server and check response for errors.

        Args:
            attribute (str): Attribute to put to server.
            data: Data to send with request.
        
        """
        response = requests.put("%s/%s" % (self.base_url, attribute), data=data)
        self.__check_error(response)
        return response.json()

    def __check_error(self, response):
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


class Telescope(Device):
    """Telescope specific methods."""

    def __init__(
        self, address, device_number, protocall="http", api_version=DEFAULT_API_VERSION
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
            True if the mount is stopped in the Home position. Must be False if the telescope does not support homing.
        
        """
        return self._get("athome")

    def atpark(self):
        """Indicate whether the telescope is at the park position.

        Returns:
            True if the telescope has been put into the parked state by the seee park() method. Set False by calling the unpark() method.
        
        """
        return self._get("atpark")

    def azimuth(self):
        """Return the telescope's aperture.
        
        Return:
            Azimuth of the telescope's current position (degrees, North-referenced, positive East/clockwise).

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
            True if this telescope is capable of software-pulsed guiding (via the pulseguide(int, int) method).
        
        """
        return self._get("canpulseguide")

    def cansetdeclinationrate(self):
        """Indicate whether the DeclinationRate property can be changed.

        Returns:
            True if the DeclinationRate property can be changed to provide offset tracking in the declination axis.

        """
        return self._get("cansetdeclinationrate")

    def cansetguiderates(self):
        """Indicate whether the DeclinationRate property can be changed.

        Returns:
            True if the guide rate properties used for pulseguide(int, int) can ba adjusted.

        """
        return self._get("cansetguiderates")

    def cansetpark(self):
        """Indicate whether the telescope park position can be set.

        Returns:
            True if this telescope is capable of programmed setting of its park position (setpark() method)

        """
        return self._get("cansetpark")

    def cansetpierside(self):
        """Indicate whether the telescope SideOfPier can be set.

        Returns:
            True if the SideOfPier property can be set, meaning that the mount can be forced to flip.
        
        """
        return self._get("cansetpierside")

    def cansetrightascensionrate(self):
        """Indicate whether the RightAscensionRate property can be changed.

        Returns:
            True if the RightAscensionRate property can be changed to provide offset tracking in the right ascension axis.
        
        """
        return self._get("cansetrightascensionrate")

    def cansettracking(self):
        """Indicate whether the Tracking property can be changed.

        Returns:
            True if the Tracking property can be changed, turning telescope sidereal tracking on and off.
        
        """
        return self._get("cansettracking")

    def canslew(self):
        """Indicate whether the telescope can slew synchronously.

        Returns:
            True if this telescope is capable of programmed slewing (synchronous or asynchronous) to equatorial coordinates.
        
        """
        return self._get("canslew")

    def canslewaltaz(self):
        """Indicate whether the telescope can slew synchronously to AltAz coordinates.

        Returns:
            True if this telescope is capable of programmed slewing (synchronous or asynchronous) to local horizontal coordinates.

        """
        return self._get("canslewaltaz")

    def canslewaltazasync(self):
        """Indicate whether the telescope can slew asynchronusly to AltAz coordinates.

        Returns:
            True if this telescope is capable of programmed asynchronus slewing (synchronous or asynchronous) to local horizontal coordinates.

        """
        return self._get("canslewaltazasync")

    def cansync(self):
        """Indicate whether the telescope can sync to equatorial coordinates.

        Returns:
            True if this telescope is capable of programmed synching to equatorial coordinates.
        
        """
        return self._get("cansync")

    def cansyncaltaz(self):
        """Indicate whether the telescope can sync to local horizontal coordinates.

        Returns:
            True if this telescope is capable of programmed synching to local horizontal coordinates.
        
        """
        return self._get("cansyncaltaz")

    def declination(self):
        """Return the telescope's declination.

        Returns:
            The declination (degrees) of the telescope's current equatorial coordinates, in the coordinate system given by the EquatorialSystem property.
            Reading the property will raise an error if the value is unavailable.
        
        """
        return self._get("declination")

    def declinationrate(self, declination_rate=None):
        """Set or return the telescope's declination tracking rate.

        Args:
            declination_rate (float): Declination tracking rate (arcseconds per second).
        
        Returns:
            The declination tracking rate (arcseconds per second) if declinatio_rate is None, JSON response if set.
        
        """
        if declination_rate == None:
            return self._get("declinationrate")
        else:
            return self._put("declinationrate", {"DeclinationRate": declination_rate})

    def doesrefraction(self, does_refraction=None):
        """Indicate or determine whether atmospheric refraction is applied to coordinates.

        Args:
            does_refraction (bool): Set True to make the telescope or driver applie atmospheric refraction to coordinates.
        
        Returns:   
            True if the telescope or driver applies atmospheric refraction to coordinates, JSON response if set.

        """
        if does_refraction == None:
            return self._get("doesrefraction")
        else:
            return self._put("doesrefraction", {"DoesRefraction": does_refraction})

    def equatorialsystem(self):
        """Return the current equatorial coordinate system used by this telescope.

        Returns:
            Current equatorial coordinate system used by this telescope (e.g. Topocentric or J2000).

        """
        return self._get("equatorialsystem")

    def focallength(self):
        """Return the telescope's focal length in meters.

        Returns:
            The telescope's focal length in meters.

        """
        return self._get("focallength")

    def guideratedeclination(self, guide_rate_declination=None):
        """Set or return the current Declination rate offset for telescope guiding.

        Args:
            guide_rate_declination (float): Declination movement rate offset (degrees/sec).

        Returns:
            Current declination rate offset for telescope guiding if not set, otherwise JSON response from server.

        """
        if guide_rate_declination == None:
            return self._get("guideratedeclination")
        else:
            return self._put(
                "guideratedeclination", {"GuideRateDeclination": guide_rate_declination}
            )

    def guideraterightascension(self, guide_rate_right_ascension=None):
        """Set or return the current RightAscension rate offset for telescope guiding.

        Args:
            guide_rate_right_ascension (float): RightAscension movement rate offset (degrees/sec).

        Returns:
            Current right ascension rate offset for telescope guiding if not set, otherwise JSON response from server.

        """
        if guide_rate_right_ascension == None:
            return self._get("guideraterightascension")
        else:
            return self._put(
                "guideraterightascension",
                {"GuideRateRightAscension": guide_rate_right_ascension},
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
            The right ascension (hours) of the telescope's current equatorial coordinates, in the coordinate system given by the EquatorialSystem property.

        """
        return self._get("rightascension")

    def rightascensionrate(self, right_ascension_rate=None):
        """Set or return the telescope's right ascension tracking rate.

        Args:
            right_ascension_rate (float): Right ascension tracking rate (arcseconds per second).

        Returns:
            Telescope's right ascension tracking rate if not set, otherwise JSON response from server.

        """
        if right_ascension_rate == None:
            return self._get("rightascensionrate")
        else:
            return self._put(
                "rightascensionrate", {"RightAscensionRate": right_ascension_rate}
            )

    def sideofpier(self, side_of_pier=None):
        """Set or return the mount's pointing state.

        Args:
            side_of_pier (int): New pointing state. 0 = pierEast, 1 = pierWest
        
        Returns:
            Side of pier if not set, otherwise JSON response from server.
        
        """
        if side_of_pier == None:
            return self._get("sideofpier")
        else:
            return self._put("sideofpier", {"SideOfPier": side_of_pier})

    def siderealtime(self):
        """Return the local apparent sidereal time.

        Returns:
            The local apparent sidereal time from the telescope's internal clock (hours, sidereal).

        """
        return self._get("siderealtime")

    def siteelevation(self, site_elevation=None):
        """Set or return the observing site's elevation above mean sea level.

        Args:
            site_elevation (float): Elevation above mean sea level (metres).
        
        Returns:
            Elevation above mean sea level (metres) of the site at which the telescope is located if not set, otherwise JSON response from server.

        """
        if site_elevation == None:
            return self._get("siteelevation")
        else:
            return self._put("siteelevation", {"SiteElevation": site_elevation})

    def sitelatitude(self, site_latitude=None):
        """Set or return the observing site's latitude.

        Args:
            site_latotude (float): Site latitude (degrees).
        
        Returns:
            Geodetic(map) latitude (degrees, positive North, WGS84) of the site at which the telescope is located if not set, otherwise JSON response from server.
        
        """
        if site_latitude == None:
            return self._get("sitelatitude")
        else:
            return self._put("sitelatitude", {"SiteLatitude": site_latitude})

    def sitelongitude(self, site_longitude=None):
        """Set or return the observing site's longitude.

        Args:
            site_longitude (float): Site longitude (degrees, positive East, WGS84)
        
        Returns:
            Longitude (degrees, positive East, WGS84) of the site at which the telescope is located.
        
        """
        if site_longitude == None:
            return self._get("sitelongitude")
        else:
            return self._put("sitelongitude", {"SiteLongitude": site_longitude})

    def slewing(self):
        """Indicate whether the telescope is currently slewing.

        Returns:
            True if telescope is currently moving in response to one of the Slew methods or the moveaxis(int, float) method, False at all other times.

        """
        return self._get("slewing")

    def slewsettletime(self, slew_settle_time=None):
        """Set or return the post-slew settling time.

        Args:
            slew_settle_time (int): Settling time (integer sec.).

        Returns:
            Returns the post-slew settling time (sec.) if not set, otherwise JSON response from server.

        """
        if slew_settle_time == None:
            return self._get("slewsettletime")
        else:
            return self._put("slewsettletime", {"SlewSettleTime": slew_settle_time})

    def targetdeclination(self, target_declination=None):
        """Set or return the target declination of a slew or sync.

        Args:
            target_declination (float): Target declination(degrees)
        
        Returns:
            Declination (degrees, positive North) for the target of an equatorial slew or sync operation, otherwise JSON from server.
        
        """
        if target_declination == None:
            return self._get("targetdeclination")
        else:
            return self._put(
                "targetdeclination", {"TargetDeclination": target_declination}
            )

    def targetrightascension(self, target_right_ascension=None):
        """Set or return the current target right ascension.

        Args:
            target_right_ascension (float): Target right ascension(hours).
        
        Returns:
            Right ascension (hours) for the target of an equatorial slew or sync operation.

        """
        if target_right_ascension == None:
            return self._get("targetrightascension")
        else:
            return self._put(
                "targetrightascension", {"TargetRightAscension": target_right_ascension}
            )

    def tracking(self, tracking=None):
        """Enable, disable, or indicate whether the telescope is tracking.

        Args:
            tracking (bool): Tracking enabled / disabled.
        
        Returns:
            State of the telescope's sidereal tracking drive, otherwise JSON response from server.
        
        """
        if tracking == None:
            return self._get("tracking")
        else:
            return self._put("tracking", {"Tracking": tracking})

    def trackingrate(self, tracking_rate=None):
        """Set or return the current tracking rate.

        Args:
            tracking_rate (int): New tracking rate. 0 = driveSidereal, 1 = driveLunar, 2 = driveSolar, 3 = driveKing.
        
        Returns:
            Current tracking rate of the telescope's sidereal drive if not set, otherwise JSON response from server.
        
        """
        if tracking_rate == None:
            return self._get("trackingrate")
        else:
            return self._put("trackingrate", {"TrackingRate": tracking_rate})

    def trackingrates(self):
        """Return a collection of supported DriveRates values.

        Returns:
            List of supported DriveRates values that describe the permissible values of the TrackingRate property for this telescope type.

        """
        return self._get("trackingrates")

    def utcdate(self, utc_date=None):
        """Set or return the UTC date/time of the telescope's internal clock.

        Args:
            utc_date: UTC date/time.
        
        Returns:
            DateTime of the UTC date/time if not set, otherwise JSON response from server.
        
        """
        if utc_date == None:
            return DateTime(self._get("utcdate"))
        else:
            if type(utc_date) is str:
                data = utc_date
            elif type(utc_date) is datetime:
                data = utc_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            elif type(utc_date) is DateTime:
                data = utc_date.__str__()
            else:
                raise TypeError()

            return self._put("utcdate", {"UTCDate": data})

    def abortslew(self):
        """Immediatley stops a slew in progress.

        Returns:
            JSON response from server.
        
        """
        return self._put("abortslew")

    def axisrates(self, axis):
        """Return the rates at which the telescope may be moved about the specified axis.

        Returns:
            The rates at which the telescope may be moved about the specified axis by the moveaxis(int, float) method.
        
        """
        return self._get("axisrates", {"Axis": axis})

    def canmoveaxis(self, axis):
        """Indicate whether the telescope can move the requested axis.

        Returns:
            True if this telescope can move the requested axis.

        """
        return self._get("canmoveaxis", {"Axis": axis})

    def destinationsideofpier(self, right_ascension, declination):
        """Predicts the pointing state after a German equatorial mount slews to given coordinates.

        Returns:
            Pointing state that a German equatorial mount will be in if it slews to the given coordinates. The return value will be one of - 0 = pierEast, 1 = pierWest, -1 = pierUnknown.

        """
        return self._get(
            "destinationsideofpier",
            {"RightAscension": right_ascension, "Declination": declination},
        )

    def findhome(self):
        """Move the mount to the "home" position.
        
        Returns:
            JSON response from server.
        
        """
        return self._put("findhome")

    def moveaxis(self, axis, rate):
        """Move a telescope axis at the given rate.

        Args:
            axis (int): The axis about which rate information is desired. 0 = axisPrimary, 1 = axisSecondary, 2 = axisTertiary.
            rate (int): The rate of motion (deg/sec) about the specified axis
        
        Returns:
            JSON response from server.

        """
        return self._put("moveaxis", {"Axis": axis, "Rate": rate})

    def park(self):
        """Park the mount.

        Returns:
            JSON response from server.

        """
        return self._put("park")

    def pulseguide(self, direction, duration):
        """Move the scope in the given direction for the given time.

        Returns:
            JSON Response from server.
        
        """
        return self._put("pulseguide", {"Direction": direction, "Duration": duration})

    def setpark(self):
        """Set the telescope's park position.

        Returns:
            JSON response from server.

        """
        return self._put("setpark")

    def slewtoaltaz(self, azimuth, altitude):
        """Slew synchronously to the given local horizontal coordinates.

        Returns:
            JSON response from server.

        """
        return self._put("slewtoaltaz", {"Azimuth": azimuth, "Altitude": altitude})

    def slewtoaltazasync(self, azimuth, altitude):
        """Slew asynchronously to the given local horizontal coordinates.

        Returns:
            JSON Response from server.

        """
        return self._put("slewtoaltazasync", {"Azimuth": azimuth, "Altitude": altitude})

    def slewtocoordinates(self, right_ascension, declination):
        """Slew synchronously to the given equatorial coordinates.

        Returns:
            JSON Response from server.

        """
        return self._put(
            "slewtocoordinates",
            {"RightAscension": right_ascension, "Declination": declination},
        )

    def slewtocoordinatesasync(self, right_ascension, declination):
        """Slew asynchronously to the given equatorial coordinates.

        Returns:
            JSON response from server.
        
        """
        return self._put(
            "slewtocoordinatesasync",
            {"RightAscension": right_ascension, "Declination": declination},
        )

    def slewtotarget(self):
        """Slew synchronously to the TargetRightAscension and TargetDeclination coordinates.

        Returns:
            JSON response from server.

        """
        return self._put("slewtotarget")

    def slewtotargetasync(self):
        """Asynchronously slew to the TargetRightAscension and TargetDeclination coordinates.

        Returns:
           JSON Response from server. 

        """
        return self._put("slewtotargetasync")

    def synctoaltaz(self, azimuth, altitude):
        """Sync to the given local horizontal coordinates.

        Returns:
            JSON response from server.

        """
        return self._put("synctoaltaz", {"Azimuth": azimuth, "Altitude": altitude})

    def synctocoordinates(self, right_ascension, declination):
        """Sync to the given equatorial coordinates.

        Returns:
            JSON response from server.

        """
        return self._put(
            "synctocoordinates",
            {"RightAscension": right_ascension, "Declination": declination},
        )

    def synctotarget(self):
        """Sync to the TargetRightAscension and TargetDeclination coordinates.

        Returns:
            JSON Response from server.
        
        """
        return self._put("synctotarget")

    def unpark(self):
        """Unpark the mount.

        Returns:
            JSON response from server.

        """
        return self._put("unpark")
