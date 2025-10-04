from gameState import *

class PacbotAgent:

    def __init__(self, state):
        self.state: GameState = state
        self.tmp_state: GameState = state

    def safetyCost(self) -> int:
        pass

    direction = [Directions.RIGHT, Directions.UP, Directions.LEFT, Directions.DOWN]
    counter = 0

    def act(self):

        # Skip if the game is paused
        if self.state.gameMode == GameModes.PAUSED:
            return

        # Deepcopy the game state
        decompressGameState(self.tmp_state, compressGameState(self.state))

        # Get Pacman's and ghosts' positions
        pacManRow, pacManCol = self.tmp_state.pacmanLoc.row, self.tmp_state.pacmanLoc.col
        ghosts = self.gameState.ghosts

        closestGhost = min(ghosts, key=lambda ghost: ghost.location.distance(pacManRow, pacManCol))
        ghostDistance = closestGhost.location.distance(pacManRow, pacManCol)
        ghostDistances = sorted([ghost.location.distance(pacManRow, pacManCol) for ghost in ghosts])

        # Evaluate flee, stay, or ignore
        closestGhostState = closestGhost.isFrightened()
        legalDirections = self.state.legalDirections()

        # this will check to see if the closest ghost is frightened or not
        if closestGhostState:
            if ghostDistance <= 3:
                vectorToGhost = (closestGhost.location.row - pacManRow, closestGhost.location.col - pacManCol)
                bestDir = None
                bestDot = float('-inf')

                for dirName, dirVector in Directions.directions.items():
                    if dirName in legalDirections:
                        dot = dirVector[0] * vectorToGhost[0] + dirVector[1] * vectorToGhost[1]
                        if dot > bestDot:
                            bestDir = dirName
                            bestDot = dot

                self.state.queueAction(
                    numTicks=4,
                    pacmanDir=bestDir
                )
        # to do, implement logic for if ghost is not frightened
        else:
            # TODO: Send a message to the server
            # (you should rewrite this to send to your robot)
            self.state.queueAction(
                numTicks=4,
                pacmanDir=Directions.directions[self.counter % 4]
            )