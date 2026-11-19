from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "képek" / "panem_map.jpeg"


def get_map_path():
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"A Panem térkép nem található: {IMAGE_PATH}"
        )

    return IMAGE_PATH