class Player:
    """Base class which handles general player behavior."""

    def __init__(self, color):
        self._color = color
        self._type = None
        if color == 'white':
            self._workers = ['A', 'B']
        else:
            self._workers = ['Y', 'Z']

    def get_workers(self):
        return self._workers

    def get_color(self):
        return self._color
        

class Human(Player):
    """Subclass which handles the human player's behavior."""
    def __init__(self, color):
        super().__init__(color)
        self._type = 'human'


class Random(Player):
    """Subclass which handles the random AI computer's behavior."""
    def __init__(self, color):
        super().__init__(color)
        self._type = 'random'

class Heuristic(Player):
    """Subclass which handles the heuristic AI computer's behavior."""
    def __init__(self, color):
        super().__init__(color)
        self._type = 'heuristic'