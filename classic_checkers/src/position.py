class Position:
    def __init__(self, x, y):
        """
        Contructs a Postion object.
        :param x: x coordinate.
        :param y: y coordinate.
        """
        self.x = x
        self.y = y

    def __repr__(self):
        """
        Generates a string representation.
        :return: a string representation of the Position.
        """
        return "({},{})".format(self.x, self.y)

    def __eq__(self, other):
        """
        Equality operator (==) implementation for Position class.
        :param other: other position to compare with.
        :return: True if positions are equal, else False.
        """
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        else:
            return False

    def __ne__(self, other):
        """
        Inquality operator (!=) implementation for Position class.
        :param other: other position to compare with.
        :return: False if positions are equal, else True.
        """
        return not self.__eq__(other)

    def __hash__(self):
        """
        Computes hash for the Positon object.
        :return: a hash value.
        """
        return hash((self.x, self.y))
