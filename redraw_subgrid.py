import numpy as np
from blessed import Terminal

term = Terminal()
char = "."
x, y, xs = 1, 2, 4


def draw_board() -> None:
    """Rudimentary attempt to draw a game board."""
    # clear the screen
    print(term.clear)
    # print the game board
    print(
        " "
        + f" {term.bold}{term.green}┃{term.normal} ".join(
            f"{char} {term.dim}{term.green}│{term.normal} {char} {term.dim}{term.green}│{term.normal} {char}"
            for _ in range(3)
        )
    )
    print(
        f"{term.green}"
        + f"{term.bold}┃{term.normal}{term.green}".join(
            "┼".join("─" * 3 for _ in range(3)) for _ in range(3)
        )
        + term.normal
    )
    print(
        " "
        + f" {term.bold}{term.green}┃{term.normal} ".join(
            f"{char} {term.dim}{term.green}│{term.normal} {char} {term.dim}{term.green}│{term.normal} {char}"
            for _ in range(3)
        )
    )
    print(
        f"{term.green}"
        + f"{term.bold}┃{term.normal}{term.green}".join(
            "┼".join("─" * 3 for _ in range(3)) for _ in range(3)
        )
        + term.normal
    )
    print(
        " "
        + f" {term.bold}{term.green}┃{term.normal} ".join(
            f"{char} {term.dim}{term.green}│{term.normal} {char} {term.dim}{term.green}│{term.normal} {char}"
            for _ in range(3)
        )
    )
    print(
        f"{term.bold}{term.green}" + "╋".join("━" * 11 for _ in range(3)) + term.normal
    )
    print(
        " "
        + f" {term.bold}{term.green}┃{term.normal} ".join(
            f"{char} {term.dim}{term.green}│{term.normal} {char} {term.dim}{term.green}│{term.normal} {char}"
            for _ in range(3)
        )
    )
    print(
        f"{term.green}"
        + f"{term.bold}┃{term.normal}{term.green}".join(
            "┼".join("─" * 3 for _ in range(3)) for _ in range(3)
        )
        + term.normal
    )
    print(
        " "
        + f" {term.bold}{term.green}┃{term.normal} ".join(
            f"{char} {term.dim}{term.green}│{term.normal} {char} {term.dim}{term.green}│{term.normal} {char}"
            for _ in range(3)
        )
    )
    print(
        f"{term.green}"
        + f"{term.bold}┃{term.normal}{term.green}".join(
            "┼".join("─" * 3 for _ in range(3)) for _ in range(3)
        )
        + term.normal
    )
    print(
        " "
        + f" {term.bold}{term.green}┃{term.normal} ".join(
            f"{char} {term.dim}{term.green}│{term.normal} {char} {term.dim}{term.green}│{term.normal} {char}"
            for _ in range(3)
        )
    )
    print(
        f"{term.bold}{term.green}" + "╋".join("━" * 11 for _ in range(3)) + term.normal
    )
    print(
        " "
        + f" {term.bold}{term.green}┃{term.normal} ".join(
            f"{char} {term.dim}{term.green}│{term.normal} {char} {term.dim}{term.green}│{term.normal} {char}"
            for _ in range(3)
        )
    )
    print(
        f"{term.green}"
        + f"{term.bold}┃{term.normal}{term.green}".join(
            "┼".join("─" * 3 for _ in range(3)) for _ in range(3)
        )
        + term.normal
    )
    print(
        " "
        + f" {term.bold}{term.green}┃{term.normal} ".join(
            f"{char} {term.dim}{term.green}│{term.normal} {char} {term.dim}{term.green}│{term.normal} {char}"
            for _ in range(3)
        )
    )
    print(
        f"{term.green}"
        + f"{term.bold}┃{term.normal}{term.green}".join(
            "┼".join("─" * 3 for _ in range(3)) for _ in range(3)
        )
        + term.normal
    )
    print(
        " "
        + f" {term.bold}{term.green}┃{term.normal} ".join(
            f"{char} {term.dim}{term.green}│{term.normal} {char} {term.dim}{term.green}│{term.normal} {char}"
            for _ in range(3)
        )
    )
    print()


def redraw_subgrid(subgrid: np.array, number: str) -> None:
    """Takes the subgrid number range(0,9) and redraws that grid based on the subgrid"""
    # Set Start Coordinates based on subgrid number
    start_coords = {
        "0": (0, 13),
        "1": (12, 13),
        "2": (24, 13),
        "3": (0, 7),
        "4": (12, 7),
        "5": (24, 7),
        "6": (0, 1),
        "7": (12, 1),
        "8": (24, 1),
    }
    redraw_game(subgrid, start_coords[number])
    # Can also write functions to redraw


def redraw_game(subgrid: np.array, start_coords: tuple) -> None:
    """Takes a subgrid numpy array and draws the current state of the game on that board"""
    x, y = start_coords
    x += 1
    for row in subgrid:
        for entry in row:
            print(term.move_xy(x, y) + f"{entry}")
            x += 4
            if x > start_coords[0] + 12:
                y += 2
                x = start_coords[0] + 1


with term.cbreak(), term.hidden_cursor():
    val = ""
    draw_board()
    test_subgrid = np.array([["X", "O", "X"], ["O", "O", "."], ["X", ".", "."]])

    while (val := term.inkey()) != "q":
        if val in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
            redraw_subgrid(test_subgrid, str(int(val) - 1))
        continue
