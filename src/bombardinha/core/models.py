from typing import List


class Note:
    def __init__(self, name: str, duration: str = "normal"):
        self.name = name
        self.duration = duration.strip().lower()


class Part:
    def __init__(self, name: str, notes: List[Note], repetition: int = 1):
        self.name = name
        self.notes = notes
        self.repetition = repetition


class Sheet:
    def __init__(self, parts: List[Part]):
        self.parts = parts
