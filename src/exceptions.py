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


class InvalidPlateauError(MissionError):
    """
    Raised when malformed plateau dimensions are processed.
    """


class LoadFromDictError(MissionError):
    """
    Raised when attempting to use a class `.from_dict()` method to initialise a class from a malformed dictionary.
    """
