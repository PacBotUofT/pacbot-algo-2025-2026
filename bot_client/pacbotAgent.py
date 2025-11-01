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

    def degreeAt(self, row, col) -> int:
        deg = 0
        for dirVector in DIRECTION_VECTORS.values():
            nr = row + dirVector[0]
            nc = col + dirVector[1]
            if not self.tmp_state.wallAt(nr, nc):
                deg += 1
        return deg

    def corridorEntranceAndLen(self, row, col, max_len=100):
        """
        Walk from (row, col) outwards until reaching a junction (degree > 2)
        or exceeding max_len. Returns a tuple (entrance_row, entrance_col, length)
        where length is how many steps from the original cell to the entrance.
        If the cell is not inside a corridor/dead-end (degree > 2), length will
        be 0 and entrance will be the same cell.
        """
        # If the starting cell is a junction, it's not a dead-end/corridor
        if self.degreeAt(row, col) > 2:
            return (row, col, 0)

        prev = None
        cur = (row, col)
        length = 0
        steps = 0
        while steps < max_len:
            deg = self.degreeAt(cur[0], cur[1])
            # If we found a junction or an isolated cell, stop
            if deg > 2 or deg == 0:
                return (cur[0], cur[1], length)

            # Find the next neighbour that isn't the previous cell
            next_cells = []
            for v in DIRECTION_VECTORS.values():
                nr = cur[0] + v[0]
                nc = cur[1] + v[1]
                if not self.tmp_state.wallAt(nr, nc) and (prev is None or (nr, nc) != prev):
                    next_cells.append((nr, nc))

            if not next_cells:
                return (cur[0], cur[1], length)

            # Continue down the corridor (there should usually be exactly one choice)
            prev = cur
            cur = next_cells[0]
            length += 1
            steps += 1

        # Max length reached; return current spot
        return (cur[0], cur[1], length)

    def legalDirections(self):
        legal = []
        for dirName, dirVector in DIRECTION_VECTORS.items():
            newRow = self.tmp_state.pacmanLoc.row + dirVector[0]
            newCol = self.tmp_state.pacmanLoc.col + dirVector[1]
            if not self.tmp_state.wallAt(newRow, newCol):
                legal.append(dirName)
        return legal
    
    def findSafePathToPellet(self, startRow, startCol):
        from collections import deque
        visited = set()
        queue = deque([(startRow, startCol, [])])
        bestPath = None
        bestScore = float('inf')

        while queue:
            currentRow, currentCol, path = queue.popleft()

            if (currentRow, currentCol) in visited:
                continue
            visited.add((currentRow, currentCol))

            if self.tmp_state.PelletAt(currentRow, currentCol):
                distance = len(path)
                danger = self.dangerCost(currentRow, currentCol)

                # Dead-end / corridor detection: find entrance and corridor length
                entranceRow, entranceCol, corridor_len = self.corridorEntranceAndLen(currentRow, currentCol)

                # If pellet is in a dead-end (corridor_len > 0), check ghost proximity
                dead_end_penalty = 0
                if corridor_len > 0:
                    # Distance for Pacman to entrance is distance - corridor_len
                    pac_to_entrance = max(0, distance - corridor_len)

                    # Find closest non-frightened ghost distance to the entrance
                    nonFrightened = [g for g in self.tmp_state.ghosts if not g.isFrightened()]
                    ghost_to_entrance = float('inf')
                    for ghost in nonFrightened:
                        gd = self.manhattanDistance(ghost.location.row, ghost.location.col, entranceRow, entranceCol)
                        if gd < ghost_to_entrance:
                            ghost_to_entrance = gd

                    # If a ghost can reach the entrance faster (or nearly as fast) as Pacman,
                    # heavily penalize this pellet to avoid getting trapped
                    # Allow some leeway (e.g., 2 ticks) for Pacman to enter/leave
                    if ghost_to_entrance - pac_to_entrance < 3:
                        dead_end_penalty = 1000

                # higher score means more dangerous and longer path and also probably a dead end penality
                score = distance + danger * 10 + dead_end_penalty

                if score < bestScore:
                    bestScore = score
                    bestPath = path
                    # continue searching for an even safer pellet
                    continue

            # Expand neighbors in BFS order, but prune obviously dangerous tiles
            for dirName, dirVector in DIRECTION_VECTORS.items():
                newRow = currentRow + dirVector[0]
                newCol = currentCol + dirVector[1]

                if not self.tmp_state.wallAt(newRow, newCol) and (newRow, newCol) not in visited and self.dangerCost(newRow, newCol) < 50:
                    queue.append((newRow, newCol, path + [dirName]))

        return bestPath

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
            elif ghostDistance <= 10:
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