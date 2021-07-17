import time

import blessed

from library.user_term import convert_to_space_location

from .board import Board
from .user_term import update_user_section


class GameState:
    """Main code for managing the game state"""

    def __init__(self, term: blessed.Terminal):
        self.current: int = 0
        self.good_move = False
        self.save_subgrid: bool = False
        self.update_board: bool = False
        self.player_active: int = 0
        self.term_info: list[str] = [""] * 3
        self.user_select_subgrid: int = 0
        self.user_select_space: int = 0
        self.user_input: str = ""

        self.term_info[1] = "shall we play a game?"
        self.term_info[2] = "(y/n?)"
        self.redraw_user_term(term)
        self.next: int = 10

    def driver(self, term: blessed.Terminal, board: Board) -> None:
        """Main State Machine"""
        if self.next == 10:
            self.wait_for_ready(term)
        elif self.next == 20:
            self.update_subgrid_select(term, board)
        elif self.next == 30:
            self.update_space_select(term, board)
        else:
            # TODO error state catch all
            pass

    def redraw_user_term(self, term: blessed.Terminal) -> None:
        """Redraws User Term"""
        print(term.move_up(7))
        update_user_section(term, self.term_info)

    def wait_for_ready(self, term: blessed.Terminal) -> None:
        """Wait for the player to start turn"""
        self.current = 10
        if self.player_active == 0:
            self.player_active = 1

        if self.user_input == "y" or self.user_input == "KEY_ENTER":
            self.term_info[0] = f"Player {self.player_active} Active"

            if self.user_select_subgrid != 0:
                self.next = 30  # skip to space select
                self.term_info[1] = "Select Space by entering 1-9"
            else:
                self.next = 20  # go to subgrid select
                self.term_info[1] = "Select SubGrid by entering 1-9"

            self.term_info[2] = (
                f"Current: SubGrid {self.user_select_subgrid} "
                f"| Space {self.user_select_space}"
            )
            self.redraw_user_term(term)
            return None

        else:
            self.next = 10

        self.redraw_user_term(term)

    def update_subgrid_select(self, term: blessed.Terminal, board: Board) -> None:
        """Update the user selected subgrid"""
        self.current = 20

        if self.user_input in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
            self.user_select_subgrid = int(self.user_input)
            self.term_info[2] = f"Current: SubGrid {self.user_select_subgrid} "

        elif self.user_input == "KEY_ENTER" and self.user_select_subgrid != 0:
            if self.confirm_good_subgrid(board):
                self.term_info[1] = "Select Space by entering 1-9"
                self.confirm_entry(term)
                self.next = 30
            else:
                self.next = 20
                self.term_info[
                    1
                ] = f"{term.red}{term.bold}*-That is an illegal move-*{term.normal}"
                self.redraw_user_term(term)
                time.sleep(1)
                self.term_info[1] = "Select Subgrid by entering 1-9"

        self.redraw_user_term(term)

    def update_space_select(self, term: blessed.Terminal, board: Board) -> None:
        """Update the user selected space"""
        self.current = 30

        if self.user_input in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
            self.user_select_space = int(self.user_input)
            self.term_info[2] = (
                f"Current: SubGrid {self.user_select_subgrid} "
                f"| Space {self.user_select_space}"
            )
        elif self.user_input == "KEY_ENTER" and self.user_select_space != 0:
            if self.confirm_good_move(board):
                self.update_board = True  # good to place player token
                self.confirm_entry(term)
            else:
                self.next = 30  # TODO go to error handling and reset values
                self.term_info[
                    1
                ] = f"{term.red}{term.bold}*-That is an illegal move-*{term.normal}"
                self.redraw_user_term(term)
                time.sleep(1)
                self.term_info[1] = "Select Space by entering 1-9"

        self.redraw_user_term(term)

        if self.update_board:
            time.sleep(2)
            self.end_of_turn(term, board)

    def confirm_entry(self, term: blessed.Terminal) -> None:
        """Confirm user pressed enter"""
        if self.user_select_subgrid != 0 and self.current == 20:
            self.term_info[1] = "Select Space by entering 1-9"
        elif self.user_select_space != 0 and self.current == 30:
            # show confirmation
            self.term_info[0] = " "
            self.term_info[1] = "Player selected:"
            self.term_info[2] = (
                f"Current: SubGrid {self.user_select_subgrid} "
                f"| Space {self.user_select_space}"
            )

        self.redraw_user_term(term)

    def end_of_turn(self, term: blessed.Terminal, board: Board) -> None:
        """End of Turn"""
        self.current = 40

        # Handle end of turn
        working_space_location = convert_to_space_location(self.user_select_space)
        subgrid_number = str(self.user_select_subgrid)
        subgrid = board.collect_subgrid(subgrid_number)
        if self.player_active == 1:
            subgrid[working_space_location[0], working_space_location[1]] = "X"
        elif self.player_active == 2:
            subgrid[working_space_location[0], working_space_location[1]] = "O"

        self.change_player()
        if board.check_grid_victory(subgrid) == "X":
            board.redraw_subgrid(term, subgrid, subgrid_number, term.green, "X")
        elif board.check_grid_victory(subgrid) == "O":
            board.redraw_subgrid(term, subgrid, subgrid_number, term.green, "O")
        else:
            board.redraw_subgrid(term, subgrid, subgrid_number, term.green, None)

        # handle logic for next grid
        # collect the subgrid based on the space just played
        working_subgrid = board.collect_subgrid(str(self.user_select_space))
        # check that the subgrid hasn't been won and isn't full
        if (
            board.check_subboard_victory(str(self.user_select_space))
            not in (
                "X",
                "O",
            )
            and "·" in working_subgrid
        ):
            # change the selected subgrid to that space number
            self.user_select_subgrid = self.user_select_space
            self.user_select_space = 0
            self.term_info[2] = (
                f"Current: SubGrid {self.user_select_subgrid} "
                f"| Space {self.user_select_space}"
            )
        else:
            # change the subgrid to 0 to let the next player choose the subgrid
            self.user_select_subgrid = 0
        self.redraw_user_term(term)
        self.update_board = False

        # circle back to top or end the game
        if board.check_board_victory() not in ("X", "O"):
            self.wait_for_ready(term)
        else:
            self.game_over(term)

    def confirm_good_move(self, board: Board) -> bool:
        """Handle the entry of a bad move"""
        # TODO need to finish this. maybe move to game logic?
        # guilty until proven innocent
        self.good_move = False

        working_space_location = convert_to_space_location(self.user_select_space)
        if board.collect_subgrid(str(self.user_select_subgrid))[
            working_space_location[0], working_space_location[1]
        ] not in ("X", "O"):
            self.good_move = True

        return self.good_move

    def confirm_good_subgrid(self, board: Board) -> bool:
        """Handle the entry of a bad subgrid choice"""
        # TODO need to finish this. maybe move to game logic?
        # guilty until proven innocent
        good_grid = False
        # pull subgrid just chosen by player
        working_subgrid = board.collect_subgrid(str(self.user_select_subgrid))
        # check that that subgrid hasn't been won and isn't full
        if (
            board.check_grid_victory(working_subgrid) not in ("X", "O")
            and "·" in working_subgrid
        ):
            good_grid = True

        return good_grid

    def change_player(self) -> None:
        """Change Player"""
        if self.player_active == 1:
            self.player_active = 2
        else:
            self.player_active = 1

    def game_over(self, term: blessed.Terminal) -> None:
        """Placeholder game over function"""
        self.term_info[1] = "Game over!"
        self.redraw_user_term(term)
