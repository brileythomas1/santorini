import sys

from santorini import Santorini
from patterns import GameOverObserver, ConditionChecker, Caretaker

class SantoriniCLI:
    """Class which controls the initial setup and CLI of the Santorini game. 
    Calls on Santorini to make changes to the board."""

    def __init__(self):
        self._game = None
        self._white_player_type = 'human'
        self._blue_player_type = 'human'
        self._undo_redo = 'off'
        self._score_display = 'off'

        # Observer pattern. Used to notify when the game is over.
        self._observer = GameOverObserver()
        self._condition_checker = ConditionChecker(self._observer)

        # Memento pattern. Manages the Memento objects
        self._caretaker = Caretaker()

    # Handles the undo, redo, and next options for the game.
    def handle_history_options(self):
        while True:
            print("undo, redo, or next")
            choice = input()
            if choice == 'undo':
                self._game.undo(self._caretaker)
            elif choice == 'redo':
                self._game.redo(self._caretaker)
            elif choice == 'next':
                # If a new move is made, clear the future states and save
                # the current state.
                self._caretaker.push_offset()
                self._caretaker.clear_future_states()
                break

    # Configures command-line arguments and starts main game loop.
    def start(self, argv):
        if len(argv) > 1:
            self._white_player_type = argv[1]
        if len(argv) > 2:
            self._blue_player_type = argv[2]
        if len(argv) > 3:
            self._undo_redo = argv[3]
        if len(argv) > 4:
            self._score_display = argv[4]
        
        self._game = Santorini(self._white_player_type, self._blue_player_type, self._score_display, self._condition_checker)
        print(self._game.get_board(), end="")
        if self._score_display == 'on':
            print("Turn: 1, white (AB), (0, 2, 4)")
        else:
            print("Turn: 1, white (AB)")
        self.run()

    def run(self):
        while not self._observer.is_game_over():
            if self._undo_redo == 'on':
                self._caretaker.add_past_memento(self._game._board.create_memento())
                self.handle_history_options()
                
            command = self._game.execute_current_player_turn()
            
            command.execute()
            command.print(self._score_display)  

            print(self._game.get_board(), end="")

            if self._score_display == 'on':
                self._game.update_turn(scores=True)
            else:
                self._game.update_turn()
            
        print(self._observer.get_winner() + " has won")
        print("Play again?")
        answer = input()
        if answer == "yes":
            SantoriniCLI().start(sys.argv)
        else:
            sys.exit()


if __name__ == "__main__":
    SantoriniCLI().start(sys.argv)
