import time
import typing
from enum import Enum

import blessed

from .board import Board
from .connection import QUEUE, Tags, create_connection
from .user_term import convert_to_space_location, update_user_section


class Token(Enum):
    """Defines Tokens"""

    EMPTY = "·"
    PLAYER_ONE = "X"
    PLAYER_TWO = "O"
    LOCKED = "*"

    @staticmethod
    def format(input: str, term: blessed.Terminal) -> str:
        """Formats string based on what it is"""
        if input == Token.PLAYER_ONE.value:
            return f"{term.red}{input}{term.normal}"
        elif input == Token.PLAYER_TWO.value:
            return f"{term.blue}{input}{term.normal}"
        else:
            return input


class State(Enum):
    """Defines the machine state"""

    error = 0
    wait_for_ready = 10
    update_subgrid_select = 20
    update_space_select = 30
    end_of_turn = 40
    network_prompt = 80
    lobby_creation_prompt = 90
    websocket_url_prompter = 100
    lobby_code_prompter = 110
    game_over = 999


class GameState:
    """Main code for managing the game state"""

    def __init__(self, term: blessed.Terminal):
        self.current: int = 0
        self.good_move: bool = False
        self.save_subgrid: bool = False
        self.update_board: bool = False
        self.player_active: str = Token.EMPTY.value
        self.term_info: list[str] = [""] * 3
        self.user_select_subgrid: int = 0
        self.user_select_space: int = 0
        self.user_input: str = ""
        self.is_sequence: bool = False
        self.ws_url: str = ""
        self.networked: bool = False
        self.lobby_code: str = ""
        self.networked_player: str = Token.EMPTY.value

        # networking queues
        self.inputs: typing.Optional[QUEUE] = None
        self.outputs: typing.Optional[QUEUE] = None

        self.term_info[1] = "shall we play a game?"
        self.term_info[2] = "(y/n?)"
        self.redraw_user_term(term)
        self.next: int = 10

    def driver(self, term: blessed.Terminal, board: Board) -> None:
        """Main State Machine"""
        if self.next == State.wait_for_ready.value:
            self.wait_for_ready(term)
        elif self.next == State.update_subgrid_select.value:
            self.update_subgrid_select(term, board)
        elif self.next == State.update_space_select.value:
            self.update_space_select(term, board)
        elif self.next == State.game_over.value:
            return
        elif self.next == State.network_prompt.value:
            self.network_prompt(term)
        elif self.next == State.lobby_creation_prompt.value:
            self.lobby_creation_prompt(term)
        elif self.next == State.websocket_url_prompter.value:
            self.websocket_url_prompter(term)
        elif self.next == State.lobby_code_prompter.value:
            self.lobby_code_prompter(term, board)
        else:
            # TODO error state catch all
            pass

    def redraw_user_term(self, term: blessed.Terminal) -> None:
        """Redraws User Term"""
        print(term.move_up(7))
        update_user_section(term, self.term_info)

    def wait_for_ready(self, term: blessed.Terminal) -> None:
        """Wait for the player to start turn"""
        self.current = State.wait_for_ready.value
        self.player_active = Token.PLAYER_ONE.value

        if self.user_input == "y" or self.user_input == "KEY_ENTER":
            self.next = State.network_prompt.value
            self.term_info[1] = "do you wish to be WIRED?"
            self.term_info[2] = "(y/n?)"
        else:
            self.next = State.wait_for_ready.value

        self.redraw_user_term(term)

    def network_prompt(self, term: blessed.Terminal) -> None:
        """Ask the user whether they want to use multiplayer"""
        self.current = State.network_prompt.value
        if self.user_input == "y":
            self.networked = True
            print(f"{term.move_xy(0, 26)}websocket url: ", end="", flush=True)

            self.next = State.websocket_url_prompter.value
        elif self.user_input == "n":
            self.draw_starting_user_term(term)
            self.networked = False
        else:
            return

    def websocket_url_prompter(self, term: blessed.Terminal) -> None:
        """Prompt the user for the url to the websocket"""
        self.current = State.websocket_url_prompter.value
        if self.user_input == "KEY_ENTER":
            self.term_info[1] = "wanna make a lobby?"
            self.term_info[2] = "(y/n?)"
            self.redraw_user_term(term)
            print(f"{term.move_xy(0, 26)}{term.clear_eol}", end="", flush=True)
            self.next = State.lobby_creation_prompt.value

        elif self.user_input in ("KEY_BACKSPACE", "KEY_DELETE") and self.ws_url != "":
            self.ws_url = self.ws_url[:-1]
            print(f"{term.move_left} {term.move_left}", end="", flush=True)

        elif not self.is_sequence:
            self.ws_url += self.user_input
            print(self.user_input, end="", flush=True)

    def lobby_creation_prompt(self, term: blessed.Terminal) -> None:
        """Ask the user whether they want to join / make a lobby"""
        self.current = State.lobby_creation_prompt.value
        if self.user_input == "y":
            self.networked_player = Token.PLAYER_ONE.value
            self.inputs, self.outputs = create_connection(None, self.ws_url)
            output_msg = self.outputs.get()

            if output_msg[0] != Tags.GAME_MADE:
                raise Exception(f"lobby was not made, {output_msg}")

            code = output_msg[1]
            self.term_info[1] = "lobby code is:"
            self.term_info[2] = str(code)
            self.redraw_user_term(term)

            output_msg = self.outputs.get()

            if output_msg[0] != Tags.GAME_STARTED:
                raise Exception("game did not start")

            self.draw_starting_user_term(term)
        elif self.user_input == "n":
            self.networked_player = Token.PLAYER_TWO.value
            print(f"{term.move_xy(0, 26)}lobby code: ", end="", flush=True)
            self.next = State.lobby_code_prompter.value
        else:
            return

    def lobby_code_prompter(self, term: blessed.Terminal, board: Board) -> None:
        """Prompt the user for the code for their lobby"""
        self.current = State.lobby_code_prompter.value
        if self.user_input == "KEY_ENTER":
            self.inputs, self.outputs = create_connection(
                int(self.lobby_code), self.ws_url
            )
            print(f"{term.move_xy(0, 26)}{term.clear_eol}", end="", flush=True)
            # wait for GAME_STARTED
            self.outputs.get()
            self.opponent_turn(term, board)

        elif (
            self.user_input in ("KEY_BACKSPACE", "KEY_DELETE") and self.lobby_code != ""
        ):
            self.lobby_code = self.lobby_code[:-1]
            print(f"{term.move_left} {term.move_left}", end="", flush=True)

        elif not self.is_sequence and self.user_input in (
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
        ):
            self.lobby_code += self.user_input
            print(self.user_input, end="", flush=True)

    def update_subgrid_select(self, term: blessed.Terminal, board: Board) -> None:
        """Update the user selected subgrid"""
        self.current = State.update_subgrid_select.value

        if self.user_input in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
            self.user_select_subgrid = int(self.user_input)
            self.term_info[2] = f"Current: SubGrid {self.user_select_subgrid} "

        elif self.user_input == "KEY_ENTER" and self.user_select_subgrid != 0:
            if self.confirm_good_subgrid(board):
                self.term_info[1] = "Select Space by entering 1-9"
                self.confirm_entry(term)
                self.next = State.update_space_select.value
                # highlight active subgrid
                board.redraw_subgrid(
                    term,
                    board.collect_subgrid(str(self.user_select_subgrid)),
                    str(self.user_select_subgrid),
                    term.yellow,
                    None,
                )
            else:
                self.next = State.update_subgrid_select.value
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
                self.update_board = True  # good to place player Token
                self.confirm_entry(term)
            else:
                self.next = (
                    State.update_space_select.value
                )  # TODO go to error handling and reset values
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
        self.current = State.end_of_turn.value

        if (
            self.networked
            and self.player_active == self.networked_player
            and self.inputs is not None
        ):
            self.inputs.put(
                (Tags.PLACE_SQUARE, self.user_select_space, self.user_select_subgrid)
            )

        # Handle end of turn
        working_space_location = convert_to_space_location(self.user_select_space)
        subgrid_number = str(self.user_select_subgrid)
        subgrid = board.collect_subgrid(subgrid_number)
        if self.player_active == Token.PLAYER_ONE.value:
            subgrid[
                working_space_location[0], working_space_location[1]
            ] = Token.PLAYER_ONE.value
        elif self.player_active == Token.PLAYER_TWO.value:
            subgrid[
                working_space_location[0], working_space_location[1]
            ] = Token.PLAYER_TWO.value

        if board.check_grid_victory(subgrid) == Token.PLAYER_ONE.value:
            board.redraw_subgrid(
                term, subgrid, subgrid_number, term.green, Token.PLAYER_ONE.value
            )
        elif board.check_grid_victory(subgrid) == Token.PLAYER_TWO.value:
            board.redraw_subgrid(
                term, subgrid, subgrid_number, term.green, Token.PLAYER_TWO.value
            )
        else:
            board.redraw_subgrid(term, subgrid, subgrid_number, term.green, None)

        # handle logic for next grid

        if board.check_subboard_victory((str(self.user_select_space))) not in (
            Token.PLAYER_ONE.value,
            Token.PLAYER_TWO.value,
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
            self.term_info[2] = ""
            self.redraw_user_term(term)
            self.term_info[2] = f"Current: SubGrid {self.user_select_subgrid}"

        self.redraw_user_term(term)
        self.update_board = False

        # circle back to top or end the game
        if board.check_board_victory() not in ("X", "O"):
            self.term_info[0] = f"Player {self.player_active} Active"

            token = Token.PLAYER_ONE.value if self.player_active == "1" else Token.PLAYER_TWO.value 

            if not self.networked or self.networked_player == token:
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
            else:
                self.opponent_turn(term, board)
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

    def change_player(self, term: blessed.Terminal) -> None:
        """Change Player"""
        if self.player_active == Token.EMPTY.value:
            self.player_active = Token.PLAYER_ONE.value
        elif self.player_active == Token.PLAYER_ONE.value:
            self.player_active = Token.PLAYER_TWO.value
        else:
            self.player_active = Token.PLAYER_ONE.value

        self.term_info[0] = f"Player {self.player_active} Active"

    def game_over(self, term: blessed.Terminal) -> None:
        """Placeholder game over function"""
        self.term_info[0] = ""
        self.term_info[1] = f"Player {self.player_active} WINS!"
        self.term_info[2] = ""
        self.redraw_user_term(term)

    def draw_starting_user_term(self, term: blessed.Terminal) -> None:
        """Put the initial text for the user terminal and draw it"""
        self.next = State.update_subgrid_select.value
        self.term_info[0] = "Player 1 Active"
        self.term_info[1] = "Select SubGrid by entering 1-9"
        self.term_info[2] = f"Current: SubGrid {self.user_select_subgrid}"
        self.redraw_user_term(term)

    def opponent_turn(self, term: blessed.Terminal, board: Board) -> None:
        """Let the opponent play their turn"""
        self.term_info[0] = ""
        self.term_info[1] = "waiting for opponent input"
        self.term_info[2] = "use ctrl+c to exit (not q)"
        self.redraw_user_term(term)

        if self.outputs is not None:
            output_msg = self.outputs.get()
        else:
            raise Exception("somehow the game state has gone wonky.")

        if output_msg[0] == Tags.DISCONNECTED:
            # opponent disconnected, what to do?
            self.term_info[0] = ""
            self.term_info[1] = "your opponent left"
            self.term_info[2] = "(find someone with more spine next time)"
            self.term_info[3] = ""
            self.next = State.end_of_turn.value

        elif output_msg[0] == Tags.PLACE_SQUARE:
            self.user_select_space = output_msg[1]
            self.user_select_subgrid = output_msg[2]
            # this will only recurse once.
            self.end_of_turn(term, board)
        else:
            raise Exception(f"unexpected {output_msg}")
