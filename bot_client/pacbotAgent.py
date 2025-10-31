from gameState import *
from gameState import Directions
from gameState import reversedDirections
from copy import deepcopy
import random

DIRECTION_VECTORS = {
    Directions.UP: (-1, 0),
    Directions.LEFT: (0, -1),
    Directions.DOWN: (1, 0),
    Directions.RIGHT: (0, 1),
}

class PacbotAgent:

    def __init__(self, state):
        self.state: GameState = state
        self.tmp_state: GameState = state
        self.lastMove = None

    def dangerCost(self, row, col) -> int:
        nonFrightenedGhosts = [ghost for ghost in self.tmp_state.ghosts if not ghost.isFrightened()]

        for ghost in nonFrightenedGhosts:
            distance = self.manhattanDistance(ghost.location.row, ghost.location.col, row, col)
            if distance < 5:
                return 100
            elif distance < 15:
                return 50
            elif distance < 25:
                return 25
            elif distance < 35:
                return 10
        return 0

    direction = [Directions.RIGHT, Directions.UP, Directions.LEFT, Directions.DOWN]
    counter = 0

    def manhattanDistance(self, row1, col1, row2, col2):
        return abs(row1 - row2) + abs(col1 - col2)

    def legalDirections(self):
        legal = []
        for dirName, dirVector in DIRECTION_VECTORS.items():
            newRow = self.tmp_state.pacmanLoc.row + dirVector[0]
            newCol = self.tmp_state.pacmanLoc.col + dirVector[1]
            if not self.tmp_state.wallAt(newRow, newCol):
                legal.append(dirName)
        return legal
    
    def findSafePathToPellet(self, startRow, startCol):
        visited = set()
        queue = [(startRow, startCol, [])]

        while queue:
            currentRow, currentCol, path = queue.pop(0)

            if(currentRow, currentCol) in visited:
                continue
            visited.add((currentRow, currentCol))

            if self.tmp_state.PelletAt(currentRow, currentCol):
                return path
            
            for dirName, dirVector in DIRECTION_VECTORS.items():
                newRow = currentRow + dirVector[0]
                newCol = currentCol + dirVector[1]

                if not self.tmp_state.wallAt(newRow, newCol) and (newRow, newCol) not in visited and self.dangerCost(newRow, newCol) < 50:
                    queue.append((newRow, newCol, path + [dirName]))

        return None

    def act(self):
        if self.state.gameMode == GameModes.PAUSED:
            return

        decompressGameState(self.tmp_state, compressGameState(self.state))

        pacManRow, pacManCol = self.tmp_state.pacmanLoc.row, self.tmp_state.pacmanLoc.col
        ghosts = self.tmp_state.ghosts

        closestGhost = min(ghosts, key=lambda g: self.manhattanDistance(g.location.row, g.location.col, pacManRow, pacManCol))
        ghostDistance = self.manhattanDistance(closestGhost.location.row, closestGhost.location.col, pacManRow, pacManCol)
        closestGhostFrightened = closestGhost.isFrightened()

        legalMoves = self.legalDirections()

        if closestGhostFrightened:
            if ghostDistance <= 3:
                vectorToGhost = (closestGhost.location.row - pacManRow, closestGhost.location.col - pacManCol)
                bestDir = None
                bestDot = float('-inf')

                for dirName, dirVector in DIRECTION_VECTORS.items():
                    if dirName in legalMoves:
                        dot = dirVector[0] * vectorToGhost[0] + dirVector[1] * vectorToGhost[1]
                        if dot > bestDot:
                            bestDot = dot
                            bestDir = dirName

                self.state.queueAction(numTicks=4, pacmanDir=bestDir)
                self.lastMove = bestDir
                return
            elif ghostDistance <= 6:
                # check distance between ghost and nearest pellet
                minPelletDistance = float('inf')
                for pellet in self.tmp_state.pellets:
                    pelletDistance = self.manhattanDistance(pacManRow, pacManCol, pellet.row, pellet.col)
                    if pelletDistance < minPelletDistance:
                        minPelletDistance = pelletDistance  
                
                if ghostDistance < minPelletDistance:
                    vectorToGhost = (closestGhost.location.row - pacManRow, closestGhost.location.col - pacManCol)
                    bestDir = None
                    bestDot = float('-inf')

                    for dirName, dirVector in DIRECTION_VECTORS.items():
                        if dirName in legalMoves:
                            dot = dirVector[0] * vectorToGhost[0] + dirVector[1] * vectorToGhost[1]
                            if dot > bestDot:
                                bestDot = dot
                                bestDir = dirName

                    self.state.queueAction(numTicks=4, pacmanDir=bestDir)
                    self.lastMove = bestDir
                    return
                else:
                    # seek pellets, closer to the pellet than the ghost
                    pathToPellet = self.findSafePathToPellet(pacManRow, pacManCol)
                    if pathToPellet and len(pathToPellet) > 0:
                        nextMove = pathToPellet[0]
                        self.state.queueAction(numTicks=4, pacmanDir=nextMove)
                        self.lastMove = nextMove
                        return 
            else:
                # seek pellets
                pathToPellet = self.findSafePathToPellet(pacManRow, pacManCol)
                if pathToPellet and len(pathToPellet) > 0:
                    nextMove = pathToPellet[0]
                    self.state.queueAction(numTicks=4, pacmanDir=nextMove)
                    self.lastMove = nextMove
                    return

        # Ghost is NOT frightened — play defensively
        dangerCosts = {}
        safeMoves = []
        for move in legalMoves:
            delta = DIRECTION_VECTORS[move]
            nextRow = pacManRow + delta[0]
            nextCol = pacManCol + delta[1]

            # Base danger from ghosts
            danger = self.dangerCost(nextRow, nextCol)

            # Small noise to break ties randomly
            danger += random.uniform(0, 0.5)

            # Penalize going back the way we came
            if move == reversedDirections.get(self.lastMove):
                danger += 30

            # Simulate the move
            simState = deepcopy(self.tmp_state)
            if simState.simulateAction(numTicks=4, pacmanDir=move):
                dangerCosts[move] = danger
                safeMoves.append(move)

        if safeMoves:
            bestMove = min(safeMoves, key=lambda move: dangerCosts[move])
        else:
            # No simulated move is safe, fallback to least dangerous legal move
            bestMove = min(legalMoves, key=lambda move: self.dangerCost(
                pacManRow + DIRECTION_VECTORS[move][0],
                pacManCol + DIRECTION_VECTORS[move][1]
            ))

        self.state.queueAction(numTicks=4, pacmanDir=bestMove)
        self.lastMove = bestMove