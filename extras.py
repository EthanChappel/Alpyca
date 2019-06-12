"""This module contains extra classes that are needed to achieve certain capabilities in Alpyca that aren't possible with the standard library."""

import re
from datetime import datetime


class DateTime:
    """Store a date with time from an ISO compliant string.
    
    Attributes:
        year (int): Number of years.
        month (int): Number of months.
        day (int): Number of days.
        hour (int): Number of hours.
        minute (int): Number of minutes.
        second (int): Number of seconds.
        microsecond (int): Number of microseconds.
    
    """

    def __init__(self, iso_str):
        """Initialize DateTime object with an ISO compliant date time string.
        
        Args:
            iso_str (str): ISO compliant date and time string.
        
        """
        match = re.match(
            r"(\d.*)-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})[.](\d{1,7})Z?", iso_str
        )

        self.year = int(match.group(1))
        self.month = int(match.group(2))
        self.day = int(match.group(3))
        self.hour = int(match.group(4))
        self.minute = int(match.group(5))
        self.second = int(match.group(6))
        self.microsecond = int(match.group(7))

    def datetime(self):
        """Get a standard library datetime object from this DateTime object."""
        ds = re.match(
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[.])(\d{7})Z", self.__str__()
        )
        return datetime.strptime(
            "%s%sUTC" % (ds.group(1), ds.group(2)[:-1]), "%Y-%m-%dT%H:%M:%S.%f%Z"
        )

    def __str__(self):
        """Get an ISO compliant string from this DateTime object."""
        return "%d-%02d-%02dT%02d:%02d:%02d.%dZ" % (
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
        )
