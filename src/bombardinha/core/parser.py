import os
import sys
import re
from typing import Tuple, Dict, List
from bombardinha.core.models import NoteDuration, Note, Part, Sheet


class BombaParser:
    def parse(self, filepath: str) -> Tuple[str, Sheet]:
        if not os.path.exists(filepath):
            print(f"Error: File '{filepath}' not found.")
            sys.exit(1)

        # 1. Read lines, strip comments, and filter empty lines.
        lines = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                clean_line = line.split("//")[0].strip()
                if clean_line:
                    lines.append(clean_line)

        title = None
        part_blueprints: Dict[str, List[Note]] = {}
        part_display_names: Dict[str, str] = {}
        final_parts: List[Part] = []

        current_section_id = None
        in_order_section = False

        for line in lines:
            # 2. First valid line is always the title.
            if title is None:
                title = line
                continue

            # 3. Handle Section Headers.
            if line.startswith("["):
                lower_line = line.lower()
                if lower_line == "[order]":
                    in_order_section = True
                    current_section_id = None
                    continue

                # Match [Display Name] [id].
                header_match = re.match(r"^\[(.*?)\]\s*\[([a-zA-Z0-9_-]+)\]$", line)
                if header_match:
                    display_name = header_match.group(1).strip()
                    part_id = header_match.group(2).strip().lower()

                    current_section_id = part_id
                    part_display_names[part_id] = display_name
                    part_blueprints[part_id] = []
                    continue
                else:
                    print(
                        f"Warning: Malformed part header '{line}'. Expected format: [Name] [id]"
                    )
                    continue

            # 4. Handle [Order] items.
            if in_order_section:
                # E.g., "a 2" or "b".
                order_tokens = line.split()
                if not order_tokens:
                    continue

                p_id = order_tokens[0].lower()
                repetition = int(order_tokens[1]) if len(order_tokens) > 1 else 1

                if p_id not in part_blueprints:
                    print(
                        f"Error: Part ID '{p_id}' used in [Order] but not defined in parts."
                    )
                    sys.exit(1)

                # Create the final part using the blueprint and display name.
                display_name = part_display_names[p_id]
                final_parts.append(
                    Part(display_name, part_blueprints[p_id], repetition)
                )
                continue

            # 5. Handle Notes within a defined part.
            if current_section_id and not in_order_section:
                # Split the line by spaces to get individual notes.
                raw_notes = line.split()

                for raw in raw_notes:
                    duration = NoteDuration.NORMAL
                    is_connected = False
                    chunk = raw

                    # Check and strip attributes (Order doesn't matter: C_- or C-_).
                    if "-" in chunk:
                        is_connected = True
                        chunk = chunk.replace("-", "")

                    if "_" in chunk:
                        duration = NoteDuration.LONG
                        chunk = chunk.replace("_", "")
                    elif "." in chunk:
                        duration = NoteDuration.SHORT
                        chunk = chunk.replace(".", "")

                    # Parse note: Base (A-G), optional accidental (#, S, b), optional octave (0-9).
                    note_match = re.match(r"^([A-Ga-g])([#sSbB])?(\d)?$", chunk)
                    if note_match:
                        base = note_match.group(1).upper()
                        raw_accidental = note_match.group(2)
                        octave = note_match.group(3) if note_match.group(3) else "1"

                        # Normalize accidentals.
                        accidental = ""
                        if raw_accidental:
                            if raw_accidental.lower() == "s" or raw_accidental == "#":
                                accidental = "#"
                            elif raw_accidental.lower() == "b":
                                accidental = "b"

                        note_name = f"{base}{accidental}{octave}"
                        part_blueprints[current_section_id].append(
                            Note(note_name, duration, is_connected)
                        )
                    else:
                        print(
                            f"Warning: Could not parse note '{raw}' in part '{part_display_names[current_section_id]}'"
                        )

        # 6. Final validations.
        if not title or not part_blueprints or not final_parts:
            print(
                "Error: Invalid .bomba file structure. Ensure Title, Parts, and [Order] exist."
            )
            sys.exit(1)

        return title, Sheet(final_parts)
