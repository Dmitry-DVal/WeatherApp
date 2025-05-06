class WeatherAPIError(Exception):
    """Базовое исключение для ошибок API"""
    pass

class WeatherAPITimeoutError(WeatherAPIError):
    pass

class WeatherAPIConnectionError(WeatherAPIError):
    pass

class WeatherAPIInvalidRequestError(WeatherAPIError):
    pass


class WeatherAPINoLocationsError(WeatherAPIError):
    """Базовое исключение для ошибок API"""
    pass

