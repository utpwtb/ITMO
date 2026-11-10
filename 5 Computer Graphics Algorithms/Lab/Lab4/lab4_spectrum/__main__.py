from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lab4_spectrum.gui import launch


def main():
    launch()


if __name__ == "__main__":
    main()
