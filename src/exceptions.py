class NotFoundError(Exception):
    """Common exception when resource is not found."""


class DoctorNotFoundError(NotFoundError):
    """Raised when a resource is not found."""


class DoctorSessionDurationExceededError(Exception):
    pass


class SelectedDateIsExceededError(Exception):
    pass


class SelectedScheduleIsNotAvailableError(Exception):
    pass
