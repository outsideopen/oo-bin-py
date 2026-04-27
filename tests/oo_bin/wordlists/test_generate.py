import pytest
import subprocess
from pathlib import Path
from importlib import resources

from oo_bin.wordlists import generate_name


def find_word_in_resources(path, word):
    for item in path.iterdir():
        if item.is_file() and item.name.endswith(".txt"):
            if word in item.read_text(encoding="utf-8"):
                return True

    return False


def test_generate_name():
    actual = generate_name().split("-")

    colors = (
        Path(resources.files("oo_bin.wordlists") / "colors.txt")
        .read_text()
        .splitlines()
    )

    assert actual[1] in colors
    with resources.as_file(resources.files("randomname")) as path:
        adj = find_word_in_resources(path / "wordlists/adjectives", actual[0])
        verb = find_word_in_resources(path / "wordlists/verbs", actual[0])
        animal = find_word_in_resources(path / "wordlists/nouns", actual[2])

    assert (adj or verb) and animal
