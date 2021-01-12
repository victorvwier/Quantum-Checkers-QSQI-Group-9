from numpy.random import choice

class Piece:
    def __init__(self, position):
        """
        Initializes a piece at a given position.
        :param position: initial position.
        """
        self.positions = {position: 1}

    def classical_move(self, current_position, new_position):
        """
        Performs a classical move.
        :param current_position: initial position.
        :param new_position: position after performing the move.
        """
        prob = self.positions.pop(current_position)
        self.positions[new_position] = prob

    def quantum_move(self, current_position, new_positions):
        """
        Performs a quantum move. Results in a superposition.
        :param current_position: initial position.
        :param new_positions: positions after performing the move.
        """
        prob = self.positions.pop(current_position)

        for new_position in new_positions:
            # assume equal probability of positions
            self.positions[new_position] = prob/len(new_positions)

    def collapse(self):
        """
        Performs a collapse on the piece - one of the positions gets picked in random process.
        """
        positions = list(self.positions.keys())
        probabilities = list(self.positions.values())

        collapsed_position = choice(positions, 1, p=probabilities)[0]
        self.positions = {collapsed_position: 1}








