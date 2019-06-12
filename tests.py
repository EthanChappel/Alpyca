"""This module contains test cases for Alpyca."""

from datetime import datetime
from pytest import fixture
from extras import DateTime


class TestDateTime:
    """Test DateTime class."""

    @fixture
    def date_time(self):
        """Object for TestDateTime class."""
        return DateTime("2016-03-04T17:45:31.1234567Z")

    def test_three_digit_microsecond_no_timezone(self):
        """Test initialization with three digit microseconds and no timezone."""
        assert DateTime("2019-06-12T06:12:52.452")

    def test_year(self, date_time):
        """Test year attribute in DateTime fixture."""
        assert date_time.year == 2016

    def test_month(self, date_time):
        """Test month attribute in DateTime fixture."""
        assert date_time.month == 3

    def test_day(self, date_time):
        """Test day attribute in DateTime fixture."""
        assert date_time.day == 4

    def test_hour(self, date_time):
        """Test hour attribute in DateTime fixture."""
        assert date_time.hour == 17

    def test_minute(self, date_time):
        """Test minute attribute in DateTime fixture."""
        assert date_time.minute == 45

    def test_second(self, date_time):
        """Test second attribute in DateTime fixture."""
        assert date_time.second == 31

    def test_microsecond(self, date_time):
        """Test microsecond attribute in DateTime fixture."""
        assert date_time.microsecond == 1234567

    def test_datetime(self, date_time):
        """Test datetime() method in DateTime fixture."""
        assert date_time.datetime() == datetime(2016, 3, 4, 17, 45, 31, 123456)

    def test_str(self, date_time):
        """Test __str__() method in DateTime fixture."""
        assert str(date_time) == "2016-03-04T17:45:31.1234567Z"
