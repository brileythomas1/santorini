import random

from board import Board
from player import Human, Heuristic, Random
from patterns import Command, HumanTurnStrategy, RandomTurnStrategy, HeuristicTurnStrategy

class Santorini:
    """Class which manages the Santorini ruleset and gameflow. Can make
    changes to the board and game's settings based on CLI."""

    def __init__(self, white, blue, score_display, checker):
        self._board = Board()

        self._score_display = score_display
        self._directions = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']

        self._condition_checker = checker
        self._white_strategy = self._get_strategy(white)
        self._blue_strategy = self._get_strategy(blue)

        if white == 'human':
            self._p1 = Human('white')
        elif white == 'random':
            self._p1 = Random('white')
        else:
            self._p1 = Heuristic('white')
        
        self._current_player = self._p1
        
        if blue == 'human':
            self._p2 = Human('blue')
        elif blue == 'random':
            self._p2 = Random('blue')
        else:
            self._p2 = Heuristic('blue')

        self._moves = {
            'n': [-1, 0], 'ne': [-1, 1], 'e': [0, 1], 'se': [1, 1],
            's': [1, 0], 'sw': [1, -1], 'w': [0, -1], 'nw': [-1, -1]
        }

    def _get_strategy(self, player_type):
        if player_type == 'human':
            return HumanTurnStrategy(self)
        elif player_type == 'random':
            return RandomTurnStrategy(self)
        else:
            return HeuristicTurnStrategy(self)
    
    def execute_current_player_turn(self):
        current_strategy = self._white_strategy if self._current_player == self._p1 else self._blue_strategy
        return current_strategy.make_turn(player=self._current_player)
    
    def get_board(self):
        return self._board

    # Checks if a move is valid given a worker, direction, and whether it's
    # for a move or a build.
    def validate_move(self, worker, direction, build):
        current_row, current_col = self._board.get_worker_pos(worker)
        
        new_row = current_row + self._moves[direction][0]
        new_col = current_col + self._moves[direction][1]

        valid = self._check_pos(new_row, new_col, current_row, current_col, build)

        if not valid:
            return False, None, None
        else:
            return True, new_row, new_col
    
    # Helper function used to simulate a move on the board. Used for checking
    # if a build is valid.
    def simulate_move(self, worker, direction):
        prev_row, prev_col = self._board.get_worker_pos(worker)

        valid, new_row, new_col = self.validate_move(worker, direction, False)

        if valid:
            self._board.set_worker_pos(worker, new_row, new_col)
            self._board.remove_worker_pos(worker, prev_row, prev_col)


    # Helper function used to undo simulaitng a move on the board. Used for
    # checking if a build is valid.
    def undo_move(self, worker, direction):
        prev_row, prev_col = self._board.get_worker_pos(worker)

        new_row = prev_row - self._moves[direction][0]
        new_col = prev_col - self._moves[direction][1]

        self._board.remove_worker_pos(worker, prev_row, prev_col)
        self._board.set_worker_pos(worker, new_row, new_col)
    

    # Checks if a worker can make a valid move (consisting of first moving, and then building)
    def can_build(self, worker):
        for move_direction in self._directions:
            valid = self.validate_move(worker, move_direction, build=False)[0]
            if valid:
                self.simulate_move(worker, move_direction)
                for build_direction in self._directions:
                    valid = self.validate_move(worker, build_direction, True)[0]
                    if valid:
                        self.undo_move(worker, move_direction)
                        return True
                self.undo_move(worker, move_direction)
        return False
    
    # Calculates all possible moves for a given player and returns them in a list.
    def enumerate_moves(self, player):
        moves = []
        for worker in player.get_workers():
            for move_direction in self._directions:
                # Checks if the worker can move in the given direction
                valid = self.validate_move(worker, move_direction, False)[0]
                if valid:
                    # Simulate the move and check which directions the worker can build in
                    self.simulate_move(worker, move_direction)
                    for build_direction in self._directions:
                        valid = self.validate_move(worker, build_direction, True)[0]
                        if valid:
                            moves.append([worker, move_direction, build_direction])
                    self.undo_move(worker, move_direction)

        if len(moves) == 0:
            return None
        else:
            return moves
        
    # Gets a player current scores (height_score, center_score, distance_score).
    # Used for printing at the start of each turn if score display enabled.
    def calculate_curr_scores(self, player):
        height_score = 0
        center_score = 0
        distance_score = 0

        if player == 'blue':
            curr = self._p2
        else:
            curr = self._p1

        for worker in curr.get_workers():
            height_score += self.calc_height_score(worker)
            center_score += self.calc_center_score(worker)
        distance_score = self.calc_distance_score(player)

        return height_score, center_score, distance_score

    # Calculates the scores for each move in a list of moves. Returns a list of
    # scores for each move.
    def calculate_move_scores(self, player, moves):
        height_scores = []
        center_scores = []
        distance_scores = []
        win_idxs = []

        # Weights for calculating move scores
        c1 = 3
        c2 = 2
        c3 = 1

        for idx, move in enumerate(moves):
            height = 0
            center = 0

            new_worker = move[0]
            move_direction = move[1]
            self.simulate_move(new_worker, move_direction)

            for worker in player.get_workers():
                row, col = self._board.get_worker_pos(worker)
                height += self.calc_height_score(worker)
                
                # If a move would put a worker on a level 3 building, add it to
                # win idxs
                if self._board.access_board(row, col)[0] == '3':
                    win_idxs.append(idx)

                center += self.calc_center_score(worker)
            distance = self.calc_distance_score(player)

            self.undo_move(new_worker, move_direction)

            height_scores.append(height)
            center_scores.append(center)
            distance_scores.append(distance)

        move_scores = []
        for i in range(len(moves)):
            # If a move would put a worker on a level 3 building, give it a
            # very high score to ensure heuristic chooses it
            if i in win_idxs:
                move_scores.append(999999)
            else:
                move_scores.append((height_scores[i] * c1) + (center_scores[i] * c2) + (distance_scores[i] * c3))

        return height_scores, center_scores, distance_scores, move_scores

    # Helper function used to calculate the height score of a given worker.
    def calc_height_score(self, worker):
        height = 0
        row, col = self._board.get_worker_pos(worker)
        height += int(self._board.access_board(row, col)[0])
        return height

    # Helper function used to calculate the center score of a given worker.
    def calc_center_score(self, worker):
        center = 0
        row, col = self._board.get_worker_pos(worker)
        if row == 2 and col == 2:
            center += 2
        elif 1 <= row <= 3 and 1 <= col <= 3:
            center += 1
        return center
    
    # Calculate Chebyshev distance between two workers
    def distance(self, worker1, worker2):
        row1, col1 = self._board.get_worker_pos(worker1)
        row2, col2 = self._board.get_worker_pos(worker2)
        return max(abs(row1 - row2), abs(col1 - col2))

    # Calculates distance score for a given player
    def calc_distance_score(self, player):
        distance = 0
        if player == 'white':
            distance += 8 - (min(self.distance('B', 'Y'), self.distance('A', 'Y')) + min(self.distance('B', 'Z'), self.distance('A', 'Z')))
        else:
            distance += 8 - (min(self.distance('Z', 'A'), self.distance('Y', 'A')) + min(self.distance('Z', 'B'), self.distance('Y', 'B')))
        return distance
    
    # Updates the current player, checks win conditions, and prints the turn.
    def update_turn(self, scores=False):
        if self._current_player == self._p1:
            self._current_player = self._p2
            other_player = self._p1
        else:
            self._current_player = self._p1
            other_player = self._p2

        # Check win condition (one of the players' workers is on a level 3
        # building). If so, notify the observer that the game is over.
        for row in self._board.get_board():
            for cell in row:
                if 'A' in str(cell) or 'B' in str(cell):
                    if '3' in str(cell):
                        self._condition_checker.notify_game_over('white')
                elif 'Y' in str(cell) or 'Z' in str(cell):
                    if '3' in str(cell):
                        self._condition_checker.notify_game_over('blue')

        valid_moves = self.enumerate_moves(self._current_player)

        if not valid_moves:
            self._condition_checker.notify_game_over(other_player.get_color())

        height_score, center_score, distance_score = self.calculate_curr_scores(self._current_player.get_color())
        scores = [height_score, center_score, distance_score]

        self._board.update_turn()
        
        workers = ''.join(self._current_player.get_workers())
        if scores is not None and self._score_display == 'on':
            print("Turn: " + str(self._board.get_turn()) + ", " + self._current_player.get_color() + " (" + workers + "), (" + str(scores[0]) + ', ' + str(scores[1]) + ', ' + str(scores[2]) + ')')
        else:
            print("Turn: " + str(self._board.get_turn()) + ", " + self._current_player.get_color() + " (" + workers + ")")

    
    # Helper function used to simulate a build on the board. Used for checking
    # if a build is valid.
    def simulate_build(self, worker, build_direction):
        directions = {
            'n': [-1, 0],
            'ne': [-1, 1],
            'e': [0, 1],
            'se': [1, 1],
            's': [1, 0],
            'sw': [1, -1],
            'w': [0, -1],
            'nw': [-1, -1]
        }

        row, col = self._board.get_worker_pos(worker)
        row += directions[build_direction][0]
        col += directions[build_direction][1]

        self._board.build_level(row, col)
    
    # Helper function used to undo a build on the board. Used for undoing a
    # build when we simulate a turn.
    def undo_build(self, worker, build_direction):
        directions = {
            'n': [-1, 0],
            'ne': [-1, 1],
            'e': [0, 1],
            'se': [1, 1],
            's': [1, 0],
            'sw': [1, -1],
            'w': [0, -1],
            'nw': [-1, -1]
        }
        row, col = self._board.get_worker_pos(worker)
        row += directions[build_direction][0]
        col += directions[build_direction][1]
        self._board.build_destroy(row, col)
    
    # Used as part of undo/redo functionality.
    def undo(self, caretaker):
        # We're on the first turn, so there's nothing to undo. Reprint the
        # initial state of the board.
        if caretaker.len_past_states() == 0:
            # Print the current state again
            print(self._board, end='')
            if self._score_display == 'on':
                print("Turn: 1, white (AB), (0, 2, 4)")
            else:
                print("Turn: 1, white (AB)")
            return
        
        # Save the current state of the board to future states.
        caretaker.add_future_memento(self._board.create_memento())

        # Get and restore the past state of the board.
        new_state = caretaker.pop_past_memento()
        self._board.restore_from_memento(new_state)

        state_data = new_state.get_state()
        if state_data['current_player'] == 'white':
            self._current_player = self._p1
        else:
            self._current_player = self._p2
        
        # By this point, the board has been restored to the previous state.
        # Print the turn and turn score (if applicable)
        if self._score_display == 'on':
            scores = self.calculate_curr_scores(self._current_player.get_color())
            self._board.print_state(scores, new_state)
        else:
            self._board.print_state(scores=None, state=new_state)

    # Used as part of undo/redo functionality
    def redo(self, caretaker):
        if caretaker.len_future_states() == 0:
            # Print the current state again
            if self._score_display == 'on':
                scores = self.calculate_curr_scores(self._current_player.get_color())
                self._board.print_state(scores=scores)
            else:
                self._board.print_state()
            return
        
        # Add the current state to the past states
        caretaker.add_past_memento(self._board.create_memento())

        # Get and restore the future state of the board
        last_state = caretaker.pop_future_memento()
        self._board.restore_from_memento(last_state)

        last_state = last_state.get_state()
        if last_state['current_player'] == 'white':
            self._current_player = self._p1
        else:
            self._current_player = self._p2

        if self._score_display == 'on':
            scores = self.calculate_curr_scores(self._current_player.get_color())
            self._board.print_state(scores, state=last_state)
        else:
            self._board.print_state(scores=None, state=last_state)
    
    # Used for checking if a position is valid for a move or build.
    def _check_pos(self, new_row, new_col, curr_row, curr_col, build):
        # Check if the new position is on the board
        if not (0 <= new_row < len(self._board.get_board()) and 0 <= new_col < len(self._board.get_board()[0])):
            return False
        
        # Check if the new position is occupied by a worker
        if 'A' in str(self._board.access_board(new_row, new_col)) or 'B' in str(self._board.access_board(new_row, new_col)) or 'Y' in str(self._board.access_board(new_row, new_col)) or 'Z' in str(self._board.access_board(new_row, new_col)):
            return False
        
        # Check if the new position is occupied by a dome
        if '4' in self._board.access_board(new_row, new_col):
            return False
    
        # If we're trying to move, check that the constraint on moving up building
        # levels holds.
        if not build:
            old_level = int(self._board.access_board(curr_row, curr_col)[0])
            new_level = int(self._board.access_board(new_row, new_col)[0])
            # Check if the new position is more than one level above the current position
            if new_level - old_level > 1:
                return False
        
        return True
    
    def get_condition_checker(self):
        return self._condition_checker
    
    def get_score_display(self):
        return self._score_display
    
    def get_p2(self):
        return self._p2
    
    def get_p1(self):
        return self._p1
