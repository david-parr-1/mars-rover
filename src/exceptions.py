class MissionError(Exception):
    """
    The base exception for all mission-related errors.
    """


class InvalidInstructionError(MissionError):
    """
    Raised when a malformed set of instructions is processed.
    """


class InvalidPositionError(MissionError):
    """
    Raised when malformed position data is processed.
    """
