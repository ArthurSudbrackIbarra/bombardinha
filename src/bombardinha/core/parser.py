import os
import sys
import re
from typing import Tuple, Dict, List
from bombardinha.core.models import Note, Part, Sheet


class BombaParser:
    def __init__(self):
        self.sections = [
            "-- DEFINE NAME --",
            "-- DEFINE PARTS --",
            "-- DEFINE ORDER --",
        ]

    def parse(self, filepath: str) -> Tuple[str, Sheet]:
        if not os.path.exists(filepath):
            print(f"Error: File '{filepath}' not found.")
            sys.exit(1)

        with open(filepath, "r", encoding="utf-8") as f:
            lines = [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.startswith("//")
            ]

        title = "Untitled"
        part_blueprints: Dict[str, List[Note]] = {}
        final_parts: List[Part] = []
        current_section = None

        for line in lines:
            upper_line = line.upper()
            if upper_line in self.sections:
                current_section = upper_line
                continue

            if current_section == "-- DEFINE NAME --":
                title = line

            elif current_section == "-- DEFINE PARTS --":
                if ":" not in line:
                    continue
                part_name, notes_str = line.split(":", 1)
                part_name = part_name.strip()

                notes_list = []
                raw_notes = notes_str.split(",")
                for raw in raw_notes:
                    # Regex handles optional octave (defaults to 1) and optional duration.
                    match = re.search(
                        r"([A-Ga-g][#b]?)(\d)?\s*(?:\(\s*duration\s*=\s*(short|normal|long)\s*\))?",
                        raw,
                        re.IGNORECASE,
                    )
                    if match:
                        note_base = match.group(1).capitalize()
                        octave = match.group(2) if match.group(2) else "1"
                        note_name = f"{note_base}{octave}"

                        duration = match.group(3) if match.group(3) else "normal"
                        notes_list.append(Note(note_name, duration))

                part_blueprints[part_name.lower()] = notes_list

            elif current_section == "-- DEFINE ORDER --":
                match = re.search(r"^(.+?)(?:\s+[xX](\d+))?$", line)
                if match:
                    p_name = match.group(1).strip()
                    repetition = int(match.group(2)) if match.group(2) else 1

                    p_key = p_name.lower()
                    if p_key not in part_blueprints:
                        print(
                            f"Error: Part '{p_name}' used in ORDER but not defined in PARTS."
                        )
                        sys.exit(1)

                    final_parts.append(Part(p_name, part_blueprints[p_key], repetition))

        if not title or not part_blueprints or not final_parts:
            print("Error: Invalid .bomba file structure.")
            sys.exit(1)

        return title, Sheet(final_parts)
