import random
from typing import Dict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, black, Color
from bombardinha.core.constants import NOTES_TO_VALVES_MAP
from bombardinha.core.models import NoteDuration, Note, Sheet


class EuphoniumRenderer:
    PREDEFINED_PASTELS = [
        "#FFB3BA",
        "#BAE1FF",
        "#BAFFC9",
        "#FFDFBA",
        "#E0BBE4",
        "#957DAD",
        "#D291BC",
        "#FEC8D8",
        "#FFDFD3",
        "#B2E2F2",
        "#C1E1C1",
        "#FDFD96",
        "#FF6961",
        "#CFCFC4",
        "#B39EB5",
        "#FFB7CE",
        "#AEC6CF",
        "#F49AC2",
        "#CB99C9",
        "#FFFFBA",
    ]

    def __init__(self, filename: str, title: str):
        self.c = canvas.Canvas(filename, pagesize=A4)
        self.width, self.height = A4
        self.title = title
        self.margin = 25
        self.row_height = 56
        self.max_notes_per_line = 9
        self.color_index = 0
        self.part_color_map: Dict[str, Color] = {}
        self.current_y = self.height - 65

    def _get_color_for_part(self, part_name: str) -> Color:
        """Assigns a permanent color to a part name."""
        name_key = part_name.lower()
        if name_key in self.part_color_map:
            return self.part_color_map[name_key]

        if self.color_index < len(self.PREDEFINED_PASTELS):
            color_hex = self.PREDEFINED_PASTELS[self.color_index]
            self.color_index += 1
            assigned_color = HexColor(color_hex)
        else:
            r, g, b = [random.uniform(0.8, 1.0) for _ in range(3)]
            assigned_color = Color(r, g, b)

        self.part_color_map[name_key] = assigned_color
        return assigned_color

    def draw_title(self) -> None:
        self.c.setFont("Helvetica-Bold", 18)
        self.c.setFillColor(black)
        self.c.drawCentredString(self.width / 2, self.height - 40, self.title)

    def draw_note_block(
        self, note: Note, x: float, y: float, is_last: bool = False
    ) -> None:
        self.c.setFont("Helvetica-Bold", 12)
        self.c.setFillColor(black)
        self.c.setStrokeColor(black)
        self.c.drawCentredString(x, y + 36, note.name)

        valves = NOTES_TO_VALVES_MAP.get(note.name, [0, 0, 0, 0])
        if valves is None:
            valves = [0, 0, 0, 0]

        radius = 3.8
        spacing = 9.5
        start_valve_x = x - (spacing * 1.5)

        for i, pressed in enumerate(valves):
            v_x = start_valve_x + (i * spacing)
            v_y = y + 20 + (-4 if i == 3 else 0)
            fill = 1 if pressed == 1 else 0
            self.c.circle(v_x, v_y, radius, stroke=1, fill=fill)

        if note.duration == NoteDuration.LONG:
            self.c.setLineWidth(1.2)
            self.c.line(x - 8, y + 32, x + 8, y + 32)
            self.c.setLineWidth(1)
        elif note.duration == NoteDuration.SHORT:
            self.c.circle(x, y + 31, 1, fill=1, stroke=1)

        if note.is_connected:
            self.c.setLineWidth(1.2)
            if not is_last:
                self.c.arc(x + 19, y + 34, x + 39, y + 46, startAng=0, extent=180)
            else:
                self.c.arc(x + 12, y + 34, x + 24, y + 46, startAng=0, extent=180)
            self.c.setLineWidth(1)

    def render_sheet(self, sheet: Sheet) -> None:
        self.draw_title()
        available_width = self.width - (2 * self.margin)
        note_step = available_width / self.max_notes_per_line

        for part in sheet.parts:
            rows = [
                part.notes[i : i + self.max_notes_per_line]
                for i in range(0, len(part.notes), self.max_notes_per_line)
            ]

            part_height = len(rows) * self.row_height
            part_color = self._get_color_for_part(part.name)

            if self.current_y - part_height < self.margin:
                self.c.showPage()
                self.draw_title()
                self.current_y = self.height - 65

            rect_y = self.current_y - part_height
            self.c.setStrokeColor(part_color)
            self.c.setFillColor(part_color, alpha=0.4)
            self.c.rect(
                self.margin, rect_y, available_width, part_height, fill=1, stroke=1
            )

            self.c.setFont("Helvetica-Bold", 9)
            self.c.setFillColor(black)
            label_text = (
                f"{part.name} ({part.repetition}x)"
                if part.repetition > 1
                else part.name
            )
            self.c.drawString(self.margin, self.current_y + 5, label_text)

            row_start_y = self.current_y - self.row_height

            for row in rows:
                for i, note in enumerate(row):
                    note_x = self.margin + (note_step / 2) + (i * note_step)
                    is_last = i == len(row) - 1
                    self.draw_note_block(note, note_x, row_start_y, is_last=is_last)
                row_start_y -= self.row_height

            self.current_y -= part_height + 22

        self.c.save()
