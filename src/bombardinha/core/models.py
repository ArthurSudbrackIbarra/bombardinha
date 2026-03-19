from enum import Enum, auto
from typing import List


class NoteDuration(Enum):
    SHORT = auto()
    NORMAL = auto()
    LONG = auto()


class Note:
    def __init__(
        self,
        name: str,
        duration: NoteDuration = NoteDuration.NORMAL,
        is_connected: bool = False,
    ):
        self.name = name
        self.duration = duration
        self.is_connected = is_connected


class Part:
    def __init__(self, name: str, notes: List[Note], repetition: int = 1):
        self.name = name
        self.notes = notes
        self.repetition = repetition


class Sheet:
    def __init__(self, parts: List[Part]):
        self.parts = parts
