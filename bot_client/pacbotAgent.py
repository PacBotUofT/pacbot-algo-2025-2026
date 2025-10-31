from gameState import *
from collections import deque # using queue to keep track of nodes to visit next

class PacbotAgent:

    def __init__(self, state):
        self.state: GameState = state
        self.tmp_state: GameState = state

    # Safety cost currently not implemented
    # def safetyCost(self) -> int:
    #     pass

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
