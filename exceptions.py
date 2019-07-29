"""This module holds exceptions to be used with Alpyca."""


class NumericError(Exception):
    """Exception for when Alpaca throws an error with a numeric value.
    
    Args:
        ErrorNumber (int): Non-zero integer.
        ErrorMessage (str): Message describing the issue that was encountered.
    
    """

    def __init__(self, ErrorNumber: int, ErrorMessage: str):
        """Initialize NumericError object."""
        super().__init__(self)
        self.message = "Error %d: %s" % (ErrorNumber, ErrorMessage)

    def __str__(self):
        """Message to display with error."""
        return self.message


class ErrorMessage(Exception):
    """Exception for when Alpaca throws an error without a numeric value.
    
    Args:
        Value (str): Message describing the issue that was encountered.
    
    """

    def __init__(self, Value: str):
        """Initialize ErrorMessage object."""
        super().__init__(self)
        self.message = Value

    def __str__(self):
        """Message to display with error."""
        return self.message
