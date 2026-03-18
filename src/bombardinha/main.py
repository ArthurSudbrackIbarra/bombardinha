import os
from datetime import datetime
from bombardinha.core.parser import BombaParser
from bombardinha.core.renderer import EuphoniumRenderer


def setup_directories() -> None:
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)


def main():
    setup_directories()

    files = sorted([f for f in os.listdir("input") if f.endswith(".bomba")])

    if not files:
        print("No .bomba files found in the 'input' directory.")
        return

    print("--- Available Songs ---")
    for idx, f in enumerate(files, start=1):
        print(f"[{idx}] {f}")

    try:
        choice = int(input("\nSelect the song index: "))
        selected_file = files[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    input_path = os.path.join("input", selected_file)
    parser = BombaParser()
    title, sheet = parser.parse(input_path)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_name = selected_file.replace(".bomba", "").replace(" ", "_")
    output_filename = f"{clean_name}_{timestamp}.pdf"
    output_path = os.path.join("output", output_filename)

    print(f"Generating PDF for '{title}'...")
    renderer = EuphoniumRenderer(output_path, title)
    renderer.render_sheet(sheet)
    print(f"Success! File saved at: {output_path}")


if __name__ == "__main__":
    main()
