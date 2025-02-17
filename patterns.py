import random

class Command:
    """Used to implement the Command design pattern. Stores information
    about making moves on the board, including the worker moved, the direction
    moved in, and the direction built in."""

    def __init__(self, worker, move_direction, build_direction, santorini, height_score=None, center_score=None, distance_score=None):
        self._worker = worker
        self._move_direction = move_direction
        self._build_direction = build_direction

        # Stores the instance of the game the move is being made on
        self._santorini = santorini

        # Also store the scores associated with the move if score_display is on
        self._height_score = height_score
        self._center_score = center_score
        self._distance_score = distance_score

    # Updates the board to reflect the move
    def execute(self):
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

        row, col = self._santorini.get_board().get_worker_pos(self._worker)
        self._santorini.get_board().remove_worker_pos(self._worker, row, col)

        row += directions[self._move_direction][0]
        col += directions[self._move_direction][1]
        self._santorini.get_board().set_worker_pos(self._worker, row, col)

        row, col = self._santorini.get_board().get_worker_pos(self._worker)
        row += directions[self._build_direction][0]
        col += directions[self._build_direction][1]
        self._santorini.get_board().build_level(row, col)
    

    def print(self, score_display):
        result = self._worker + "," + self._move_direction + "," + self._build_direction
        if score_display == 'on':
            result += " (" + str(self._height_score) + ", " + str(self._center_score) + ", " + str(self._distance_score) + ")"
        print(result)


class GameOverObserver:
    """Used to implement the Observer design pattern. Stores information
    about whether the game is over and who the winner is."""
    def __init__(self):
        self._game_over = False
        self._winner = None

    def notify_game_over(self, winner):
        self._game_over = True
        self._winner = winner
    
    def get_winner(self):
        return self._winner

    def is_game_over(self):
        return self._game_over

class ConditionChecker:
    """Part of the Observer design pattern. Used to check whether the game
    should end or not and notifies the observer if it should with the winner."""
    def __init__(self, end_game_observer):
        self._end_game_observer = end_game_observer

    def notify_game_over(self, winner):
        self._end_game_observer.notify_game_over(winner)

class Memento:
    """Used to implement the Memento design pattern. Stores information
    about the state of the game at a given point in time."""

    def __init__(self, state):
        self._state = state

    def get_state(self):
        return self._state

class Caretaker:
    """Manages the Memento objects."""

    def __init__(self):
        self._past_states = []
        self._future_states = []
        self._offset = None

    def add_past_memento(self, memento):
        if self._offset is not None:
            self._past_states.append(self._offset)
        self._offset = memento
    
    def add_future_memento(self, memento):
        self._future_states.append(memento)

    def pop_past_memento(self):
        if self._offset is not None:
            self._offset = self._past_states.pop()
        return self._offset

    def pop_future_memento(self):
        self._offset = self._future_states.pop()
        return self._offset

    def get_memento(self, index):
        return self._mementos[index]

    def len_past_states(self):
        return len(self._past_states)
    
    def len_future_states(self):
        return len(self._future_states)

    def clear_future_states(self):
        self._future_states = []
    
    def push_offset(self):
        self._past_states.append(self._offset)
        board = [row[:] for row in self._offset.get_state()['board']]
        self._past_states[-1].get_state()['board'] = board
        self._offset = None

class TurnStrategy:
    """Used to implement the Strategy design pattern. Provides an interface
    for the different types of turns that can be made in the game."""

    def __init__(self, santorini):
        self._game = santorini
        self._condition_checker = self._game.get_condition_checker()
        self._workers = ['A', 'B', 'Y', 'Z']
        self._directions = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']


    def make_turn(self):
        pass

class HumanTurnStrategy(TurnStrategy):
    """Subclass which is part of the Strategy design pattern. Used for the logic
    of a human turn."""

    def __init__(self, santorini):
        super().__init__(santorini) 

    def make_turn(self, player):
        while True:
            print("Select a worker to move")
            worker = input()

            if worker not in self._workers:
                print("Not a valid worker")
                continue
            elif worker not in player.get_workers():
                print("That is not your worker")
                continue
            elif not self._game.can_build(worker):
                print("That worker cannot move")
                continue
            break

        while True:
            print("Select a direction to move (n, ne, e, se, s, sw, w, nw)")
            move_direction = input()
            if move_direction not in self._directions:
                print("Not a valid direction")
                continue
            valid = self._game.validate_move(worker, move_direction, False)
            if not valid[0]:
                print("Cannot move " + move_direction)
                continue
            break

        while True:
            print("Select a direction to build (n, ne, e, se, s, sw, w, nw)")
            build_direction = input()

            if build_direction not in self._directions:
                print("Not a valid direction")
                continue

            self._game.simulate_move(worker, move_direction)
            valid = self._game.validate_move(worker, build_direction, True)
            self._game.undo_move(worker, move_direction)
            if not valid[0]:
                print("Cannot build " + build_direction)
                continue
            break

        move = [worker, move_direction, build_direction]
        
        if self._game.get_score_display() == 'on':
            self._game.simulate_move(move[0], move[1])
            self._game.simulate_build(move[0], move[2])
            height_score, center_score, distance_score = self._game.calculate_curr_scores(player.get_color())
            self._game.undo_build(move[0], move[2])
            self._game.undo_move(move[0], move[1])
            return Command(move[0], move[1], move[2], self._game, height_score, center_score, distance_score)

        return Command(move[0], move[1], move[2], self._game)

class RandomTurnStrategy(TurnStrategy):
    """Subclass which is part of the Strategy design pattern. Used for the logic
    of a random turn."""

    def __init__(self, santorini):
        super().__init__(santorini) 

    def make_turn(self, player):
        moves = self._game.enumerate_moves(player)
        if player.get_color() == 'white':
            other_player = self._game.get_p2()
        else:
            other_player = self._game.get_p1()
        
        if moves is None:
            self._condition_checker.notify_game_over(other_player.get_color())
        else:
            move = random.choice(moves)
        
        if self._game.get_score_display() == 'on':
            self._game.simulate_move(move[0], move[1])
            self._game.simulate_build(move[0], move[2])
            height_score, center_score, distance_score = self._game.calculate_curr_scores(player.get_color())
            self._game.undo_build(move[0], move[2])
            self._game.undo_move(move[0], move[1])
            return Command(move[0], move[1], move[2], self._game, height_score, center_score, distance_score)

        return Command(move[0], move[1], move[2], self._game)

class HeuristicTurnStrategy(TurnStrategy):
    """Subclass which is part of the Strategy design pattern. Used for the logic
    of a heuristic turn."""

    def __init__(self, santorini):
        super().__init__(santorini)

    def make_turn(self, player):
        moves = self._game.enumerate_moves(player)

        if player.get_color() == 'white':
            other_player = self._game.get_p2()
        else:
            other_player = self._game.get_p1()
        
        if moves is None:
            self._condition_checker.notify_game_over(other_player.get_color())
        else:
            height_score, center_score, distance_score, move_scores = self._game.calculate_move_scores(player, moves)

            best_moves = []
            for idx, move in enumerate(moves):
                if move_scores[idx] == max(move_scores):
                    best_moves.append(idx)
            
            move = moves[random.choice(best_moves)]
            
        if self._game.get_score_display() == 'on':
            self._game.simulate_move(move[0], move[1])
            self._game.simulate_build(move[0], move[2])
            height_score, center_score, distance_score = self._game.calculate_curr_scores(player)
            self._game.undo_build(move[0], move[2])
            self._game.undo_move(move[0], move[1])
            return Command(move[0], move[1], move[2], self._game, height_score, center_score, distance_score)

        return Command(move[0], move[1], move[2], self._game)
