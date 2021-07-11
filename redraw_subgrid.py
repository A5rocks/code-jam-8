import time
from enum import Enum

import numpy as np
from blessed import Terminal


class Square(Enum):
    """Represents a board square."""

    EMPTY = "."
    Player1 = "X"
    Player2 = "O"


def middle_sperator() -> str:
    """Subgrid Seperator Line"""
    return (
        f"{term.green}"
        + f"{term.bold}┃{term.normal}{term.green}".join(
            "┼".join("─" * 3 for _ in range(3)) for _ in range(3)
        )
        + term.normal
    )


def major_seperator() -> str:
    """Major Seperator Line"""
    return (
        f"{term.bold}{term.green}" + "╋".join("━" * 11 for _ in range(3)) + term.normal
    )


def blank_row() -> str:
    """Add rows with Empty Values"""
    output = f"{term.bold}{term.green}┃{term.normal}".join(
        f" {Square.EMPTY.value} {term.green}│{term.normal} {Square.EMPTY.value} "
        + f"{term.green}│{term.normal} {Square.EMPTY.value} "
        for _ in range(3)
    )
    return output


def build_board() -> None:
    """Builds the whole board with Empty Values"""
    print(term.clear)
    print(blank_row())
    print(middle_sperator())
    print(blank_row())
    print(middle_sperator())
    print(blank_row())
    print(major_seperator())
    print(blank_row())
    print(middle_sperator())
    print(blank_row())
    print(middle_sperator())
    print(blank_row())
    print(major_seperator())
    print(blank_row())
    print(middle_sperator())
    print(blank_row())
    print(middle_sperator())
    print(blank_row())
    print()


def starting_user_section() -> list:
    """Starting Terminal"""
    output = []
    output += "┌─term────────────────────────────┐"
    output += "\n│                                 │"
    output += "\n│      shall we play a game?      │"
    output += "\n│             (y/n?)              │"
    output += "\n│                                 │"
    output += "\n└────────────────────('q' to esc)─┘"

    return output


def update_user_section(infoToBeAdded: list) -> list:
    """To add your information to the terminal you have 3 lines with 31 spaces"""
    output = []

    for i in infoToBeAdded:
        if len(i) > 31:
            raise NameError("Terminal conents to big")

    if len(infoToBeAdded) == 1:
        infoToBeAdded += " "
        infoToBeAdded += " "
        infoToBeAdded += " "
    elif len(infoToBeAdded) == 2:
        infoToBeAdded += " "
        infoToBeAdded += " "
    elif len(infoToBeAdded) == 3:
        infoToBeAdded += " "

    output += "┌─term────────────────────────────┐"
    output += "\n│ " + "".join(infoToBeAdded[0]).ljust(31) + " │"
    output += "\n│ " + "".join(infoToBeAdded[1]).ljust(31) + " │"
    output += "\n│ " + "".join(infoToBeAdded[2]).ljust(31) + " │"
    output += "\n│ " + "".join(infoToBeAdded[3]).ljust(31) + " │"
    output += "\n└────────────────────('q' to esc)─┘"

    return output


def reset_turn() -> dict:
    """Reset machine for next turn"""
    state = {
        "subGridSelectBool": True,
        "spaceSelectBool": True,
        "userConfirmBool": True,
        "playerActive": 1,
        "userSelectSubGrid": 0,
        "userSelectSpace": 0,
    }
    return state


def playerShift(state: dict) -> dict:
    """Change player active"""
    if state["playerActive"] == 1:
        state["playerActive"] = 2
    else:
        state["playerActive"] = 1

    return state


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


def numpy_build_start() -> np.ndarray:
    """Builds the Starting NP arrays"""
    testSubGrid = np.array([["X", "O", "X"], ["O", "O", "."], ["X", ".", "."]])
    boardState = np.array(np.full((9, 3, 3), Square.Player1.value))

    return testSubGrid, boardState


term = Terminal()

if __name__ == "__main__":
    with term.cbreak(), term.hidden_cursor():
        val = ""
        termInfo = [""] * 3
        build_board()

        # State
        state = reset_turn()

        testSubGrid, boardState = numpy_build_start()

        userSection = starting_user_section()
        print("".join(userSection))

        while (val := term.inkey()) != "q":
            with term.location():
                print(term.move_up(7))
                termInfo[0] = f"Player {state['playerActive']} Active"

                if state["subGridSelectBool"]:
                    termInfo[1] = "Select SubGrid by entering 1-9"
                else:
                    termInfo[1] = "Select Space by entering 1-9"

                if val in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
                    if state["subGridSelectBool"]:
                        state["userSelectSubGrid"] = val
                    else:
                        state["userSelectSpace"] = val
                    termInfo[
                        2
                    ] = f"Current: SubGrid {state['userSelectSubGrid']} | Space {state['userSelectSpace']}"

                elif val.is_sequence and val.name == "KEY_ENTER":
                    if state["subGridSelectBool"] and state["userSelectSubGrid"] != 0:
                        state["subGridSelectBool"] = False
                        termInfo[1] = "Select Space by entering 1-9"
                    elif state["spaceSelectBool"] and state["userSelectSpace"] != 0:
                        state["spaceSelectBool"] = False
                        termInfo[1] = "Confirm Selection?"
                    elif state["userConfirmBool"]:
                        state["userConfirmBool"] = False
                        # execute change here
                        # be sure to reset bools
                        termInfo[0] = " "
                        termInfo[1] = f"Player{state['playerActive']} selected:"
                        termInfo[
                            2
                        ] = f"SubGrid {state['userSelectSubGrid']} | Space {state['userSelectSpace']}"

                        state = reset_turn()
                        state = playerShift(state)
                        time.sleep(2)

                userSection = update_user_section(termInfo)
                print("".join(userSection))

        """
        while (val := term.inkey()) != "q":
            if val in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
                subGrid = val
                redraw_subgrid(boardState[int(subGrid)], str(int(subGrid) - 1))
            elif val == "t":
                redraw_subgrid(testSubGrid, str(int(subGrid) - 1))
        """

    print(term.clear)