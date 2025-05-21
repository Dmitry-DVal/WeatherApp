class WeatherAPIError(Exception):
    """Basic exception for API errors."""

    pass


class WeatherAPITimeoutError(WeatherAPIError):
    pass


class WeatherAPIConnectionError(WeatherAPIError):
    pass


class WeatherAPIInvalidRequestError(WeatherAPIError):
    pass


class WeatherAPINoLocationsError(WeatherAPIError):
    pass
