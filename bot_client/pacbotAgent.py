from gameState import *
from collections import deque    # using queue to store path to next pellet

class PacbotAgent:

    def __init__(self, state):
        self.state: GameState = state
        self.tmp_state: GameState = state

        # BFS variables
        self.path = deque()     # Queue of directions to follow
        self.targeted_pellet = None     # Current target pellet (row, col)


    # Safety cost currently not implemented
    # def safetyCost(self) -> int:
    #     pass

    def bfs_nearest_pellet(self) -> list[Directions]:
        """
        Implement bfs to find nearest pellet.
        Then return a path to pellet.
        """



        # Should return a list of directions
        return []

    def act(self):

        # Skip if the game is paused
        if self.state.gameMode == GameModes.PAUSED:
            return

        # Deepcopy the game state
        decompressGameState(self.tmp_state, compressGameState(self.state))

        # TODO: Do some calculations...

        # TODO: Send a message to the server
        # (you should rewrite this to send to your robot)
        self.state.queueAction(
            numTicks=4,
            pacmanDir=Directions.RIGHT
        )
