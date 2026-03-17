from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from bombardinha.core.constants import NOTES_TO_VALVES_MAP


def draw_note_block(c: canvas.Canvas, note: str, x: float, y: float):
    """Draws the note name and its 4 valves with the 4th valve slightly lowered."""
    # 1. Draw the Note Name.
    c.setFont("Helvetica-Bold", 14)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(x + 25, y + 45, note)

    # 2. Draw the 4 Valves.
    valves = NOTES_TO_VALVES_MAP.get(note, [0, 0, 0, 0])
    radius = 5
    spacing = 12

    for i, pressed in enumerate(valves):
        # Calculate horizontal position.
        valve_x = x + 7 + (i * spacing)

        # Logic for the 4th valve offset.
        # We drop the y position by 5 units only for the last valve (index 3).
        y_offset = -5 if i == 3 else 0
        valve_y = y + 25 + y_offset

        # Set colors for the valves.
        fill = 1 if pressed == 1 else 0
        c.setStrokeColorRGB(0, 0, 0)
        c.setFillColorRGB(0, 0, 0)

        c.circle(valve_x, valve_y, radius, stroke=1, fill=fill)


def create_sheet(filename: str):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Define a "Part".
    part_name = "Part A"
    part_color = HexColor("#CCCCFF")
    notes = ["C1", "D1", "Eb1", "F1", "C1"]

    # Draw Part Container.
    margin = 50
    box_y = height - 150
    box_height = 85  # Increased slightly to accommodate the lowered 4th valve.

    c.setStrokeColor(part_color)
    c.setFillColor(part_color, alpha=0.3)
    c.rect(margin, box_y, width - (margin * 2), box_height, stroke=1, fill=1)

    # Label the Part.
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin + 10, box_y + 65, part_name)

    # Draw the notes inside the box.
    start_x = margin + 50
    for i, note in enumerate(notes):
        draw_note_block(c, note, start_x + (i * 60), box_y)

    c.save()


def main():
    print("Generating PDF...")
    create_sheet("euphonium_sheet.pdf")
    print("Done! Check euphonium_sheet.pdf")


if __name__ == "__main__":
    main()
