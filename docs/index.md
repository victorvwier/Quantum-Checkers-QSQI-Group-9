# Quantum checkers

## Rules
All pieces have the possibility of making either a classical or a quantum move each turn.

A quantum move gives one the possibility to simultaneously move a piece diagonally left and diagonally right. The piece then is in a quantum state with equal probabilities of being in the two possible positions

King pieces can, aside from making a classical move, make a quantum move forward or a quantum move backward per turn.

When trying to capture an opponent's piece and one or multiple pieces are in a quantum state, a measurement takes place. Because of this measurement we know the actual position of the measured pieces, after which they lose their quantum mechanical properties. In this case one of the following four possibilities is realized:

* If both pieces in the attack are measured to be in their expected position: The pieces move according to their classical rules again, thus the attacker captures the attacked piece
* If the attacking piece is measured to not be in it's expected position, but the attacked piece is: No move takes place
* If the attacked piece is measured to not be in it's expected position, but the attacking piece is: The attacking piece does a classical move forward in the direction it wanted to capture the possible piece
* If both pieces are measured not to be in their expected position: No move takes place
  
When multiple pieces of one player are confronted by moving one piece, the pieces become entangled if at least one of them is in a quantum state. The pieces then move according to the following rules:

* If a piece does a quantum move to to a position where a classic piece is located: The quantum piece has half the probability to go to the empty one of the two possible spots to move to and half the probability to not move at all, since a piece can not move to an already full spot
* If a piece does a classical move to to a position where a quantum piece is located: Since the spot one wants to move to has a possibility of being already filled, the probability of moving there is 100% minus the probability of a piece already being there. The piece then has a probability of 100% minus the probability of executing the move, to stay in it's place
* If a piece does a quantum move to to a position where another quantum piece is located: The to-be-moved quantum piece has half the probability to go to the empty one of the two possible spots to move to. The other half of it's probability is split between a move to the possibly occupied spot and not moving at all. This is calculated in the same way as in the previous point, but of course the 100% probability of the to-be-moved piece in the previous point is now replaced by half the probability of the original to-be-moved piece