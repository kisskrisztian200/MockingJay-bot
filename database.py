import json
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "characters.json"
PLAYERS_PATH = Path(__file__).resolve().parent / "players.json"


def load_characters():
    if not DATABASE_PATH.exists():
        return {}

    with open(DATABASE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_characters(characters):
    with open(DATABASE_PATH, "w", encoding="utf-8") as file:
        json.dump(
            characters,
            file,
            ensure_ascii=False,
            indent=4
        )


def load_players():
    if not PLAYERS_PATH.exists():
        return {}

    with open(PLAYERS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_players(players):
    with open(PLAYERS_PATH, "w", encoding="utf-8") as file:
        json.dump(
            players,
            file,
            ensure_ascii=False,
            indent=4
        )