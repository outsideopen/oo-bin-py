import functools
from pathlib import Path

import randomname
from randomname.util import choose

OUR_PATH = Path(__file__).parent


@functools.lru_cache(128)
def load_file(path: Path):
    # this is ripped out of the randomname.util package
    with path.open(mode="r", encoding="utf-8") as file:
        return [
            line
            for line in map(str.strip, file)
            if line and not line.startswith((";", "#"))
        ]


randomname.util.WORD_FUNCS["custom"] = lambda *args: choose(
    load_file(OUR_PATH / Path(*args).with_suffix(".txt"))
)


def generate_name():
    return randomname.generate(
        [
            "a/appearance",
            "a/character",
            "a/complexity",
            "a/emotions",
            "a/food",
            "a/geometry",
            "a/physics",
            "a/sound",
        ],
        "custom/colors.txt",
        ["n/apex_predators", "n/birds", "n/cats", "n/dogs", "n/fish", "n/wood"],
    )
