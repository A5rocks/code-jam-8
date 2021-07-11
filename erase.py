from blessed import Terminal

term = Terminal()
char = "X"
x, y, xs = (
    1,
    2,
    4,
)
with term.cbreak(), term.hidden_cursor():
    # clear the screen
    print(term.home + term.clear)
    # print the game board
    print()
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

    # erase the gameboard
    while term.inkey(timeout=0.02) != "q":
        # erase,
        txt_erase = term.move_xy(x, y) + " "
        print(txt_erase, end="", flush=True)
        # move
        x, y = x + xs, y
        # bounce,
        if x >= 37:
            y += 2
            x = 1
