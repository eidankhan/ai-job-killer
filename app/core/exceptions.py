# app/exceptions.py

class TranscriptError(Exception):
    """Base class for transcript-related errors"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class VideoUnavailableError(TranscriptError):
    """Video is private, deleted, or unavailable"""
    def __init__(self, message="Video unavailable"):
        super().__init__(message, code=404)


class VideoPrivateError(TranscriptError):
    """Video is private"""
    def __init__(self, message="Video is private"):
        super().__init__(message, code=403)


class LanguageNotSupportedError(TranscriptError):
    """Requested language not available"""
    def __init__(self, message="Language not supported"):
        super().__init__(message, code=422)


class TranscriptFetchError(TranscriptError):
    """Generic transcript fetch failure"""
    def __init__(self, message="Failed to fetch transcript"):
        super().__init__(message, code=500)
