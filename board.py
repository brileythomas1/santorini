from patterns import Memento

class Board:
    """Class which represents the board of a generic game. The board is a
    5x5 grid of cells which can be updated and adjusted."""
    
    def __init__(self):
        self._board = [
            ['0', '0', '0', '0', '0'],
            ['0', '0Y', '0', '0B', '0'],
            ['0', '0', '0', '0', '0'],
            ['0', '0A', '0', '0Z', '0'],
            ['0', '0', '0', '0', '0']
        ]

        self._pieces = {
                        'white': ['A', 'B'],
                        'blue': ['Y', 'Z']
        }

        self._turn = 1
        self._current_player = 'white'

    # Returns the current state of the board as a dict of all its attributes.
    # IMPORTANT: makes an actual copy of the board by value, not by reference.
    def save_state(self):
        return {
            'board': [row[:] for row in self._board],
            'turn': self._turn,
            'current_player': self._current_player
        }
    
    # Restores the state of the board from a dict of all its attributes.
    def restore_state(self, state):
        self._board = state['board']
        self._turn = state['turn']
        self._current_player = state['current_player']
    
    # Prints the given state of the board.
    def print_state(self, scores=None, state=None):
        # We use a "None" state to indicate that we're already at the most
        # recent state. In this case, create a state of the most recent state and
        # print it.
        if state is None:
            state = self.save_state()
            self.print_state(scores=scores, state=state)
            return

        # Prints board and turn info
        print(self, end='')
        workers = ''.join(self._pieces[self._current_player])

        if scores is None:
            print(f"Turn: {self._turn}, {self._current_player} ({workers})")
        else:
            print(f"Turn: {self._turn}, {self._current_player} ({workers}), ({scores[0]}, {scores[1]}, {scores[2]})")

    # Increases the building level of the given cell by 1.
    def build_level(self, row, col):
            current_level = int(self._board[row][col][0])
            self._board[row][col] = str(current_level + 1)

    # Decreases the building level of the given cell by 1. Used for undoing a
    # build when we simulate a turn.
    def build_destroy(self, row, col):
        current_level = int(self._board[row][col][0])
        self._board[row][col] = str(current_level - 1)
    
    # Str representation of the board in accordance with the format in the spec.
    def __str__(self):
        board = "+--+--+--+--+--+\n"
        for row in self._board:
            board += "|" + "|".join(f"{cell:2s}" for cell in row) + "|\n"
            board += "+--+--+--+--+--+\n"
        return board

    # Updates the current player, checks win conditions, updates turn number
    # and prints
    def update_turn(self):
        if self._current_player == 'white':
            self._current_player = 'blue'
        else:
            self._current_player = 'white'

        self._turn += 1
        
    def access_board(self, row, col):
            return self._board[row][col]

    def get_board(self):
        return self._board
    
    def get_worker_pos(self, worker):
        for row in range(len(self._board)):
            for col in range(len(self._board[row])):
                if worker in self._board[row][col]:
                    return row, col
    
    def set_worker_pos(self, worker, row, col):
        self._board[row][col] = self._board[row][col] + worker
    
    def remove_worker_pos(self, worker, row, col):
        self._board[row][col] = self._board[row][col].replace(worker, '')  
    
    def get_turn(self):
        return self._turn
    
    def create_memento(self):
        return Memento(self.save_state())
    
    def restore_from_memento(self, memento):
        self.restore_state(memento.get_state())
        