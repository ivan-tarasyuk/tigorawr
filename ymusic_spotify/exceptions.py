from typing import Any


class YMException(Exception):
    def __init__(self, message: str = 'An error occurred', item: Any = None):
        if item is not None:
            message += f': {str(item)}'
        super().__init__(message)


class IOException(YMException):
    def __init__(self, message: str = 'An error occurred while processing file', file: Any = None):
        super().__init__(message, file)


class NoResponse(YMException):
    def __init__(self, message: str = 'No response while searching for track', track: Any = None):
        super().__init__(message, track)


class TrackNotFound(YMException):
    def __init__(self, message: str = 'No track was found matching', track: Any = None):
        super().__init__(message, track)


class InvalidDataStructure(YMException):
    def __init__(self, message='Invalid data structure', data: Any = None):
        super().__init__(message, data)
